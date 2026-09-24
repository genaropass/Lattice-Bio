"""
Generador de Mapas de Complejidad Fractal Radiográfica Locales (Heatmaps Pixel a Pixel) y Superposición de Colores.
Versión Robustecida para Producción y QA.
"""

from typing import Tuple, Dict, Any
import numpy as np
from scipy.ndimage import zoom

from .box_counting import compute_box_counting_dimension
from .minkowski import compute_minkowski_blanket_dimension


import cv2


def compute_local_fractal_heatmap(
    image: np.ndarray,
    window_size: int = 32,
    stride: int = 24,
    method: str = "minkowski",
    max_processing_dim: int = 384,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Calcula un mapa de calor local de dimensión fractal escaneando la imagen con una ventana deslizante.
    Optimizado para rendimiento ultrarrápido (sub-segundo).
    """
    if image is None or image.size == 0:
        return np.full((10, 10), 2.0), np.array([[2.0]])

    if image.ndim != 2:
        if image.ndim == 3:
            image = image[:, :, 0]

    orig_h, orig_w = image.shape

    # Optimización: Reducir escala internamente si la imagen supera max_processing_dim
    if max(orig_h, orig_w) > max_processing_dim:
        scale = max_processing_dim / float(max(orig_h, orig_w))
        proc_h = int(round(orig_h * scale))
        proc_w = int(round(orig_w * scale))
        proc_img = cv2.resize(image, (proc_w, proc_h), interpolation=cv2.INTER_AREA)
    else:
        proc_img = image

    h, w = proc_img.shape
    safe_window = min(window_size, min(h, w))
    if safe_window < 8:
        return np.full((orig_h, orig_w), 2.0), np.array([[2.0]])

    safe_stride = max(4, min(stride, safe_window // 2))

    rows = list(range(0, h - safe_window + 1, safe_stride))
    cols = list(range(0, w - safe_window + 1, safe_stride))

    if len(rows) == 0 or len(cols) == 0:
        return np.full((orig_h, orig_w), 2.0), np.array([[2.0]])

    grid_h = len(rows)
    grid_w = len(cols)
    heatmap_raw = np.zeros((grid_h, grid_w), dtype=np.float32)

    for i, r in enumerate(rows):
        for j, c in enumerate(cols):
            roi = proc_img[r : r + safe_window, c : c + safe_window]

            if method == "minkowski":
                res = compute_minkowski_blanket_dimension(roi, max_scale=3)
                d_val = res["minkowski_dimension"]
            else:
                mean_val = float(np.mean(roi))
                bin_roi = (roi > mean_val).astype(np.uint8)
                res = compute_box_counting_dimension(bin_roi, min_box_size=2, max_box_size=safe_window // 2)
                d_val = res["D0"]

            heatmap_raw[i, j] = d_val

    # Re-escalar al tamaño original de la imagen
    zoom_y = float(orig_h) / float(grid_h)
    zoom_x = float(orig_w) / float(grid_w)

    heatmap_full = zoom(heatmap_raw, (zoom_y, zoom_x), order=1)
    heatmap_full = heatmap_full[:orig_h, :orig_w]

    if heatmap_full.shape[0] < orig_h or heatmap_full.shape[1] < orig_w:
        pad_h = max(0, orig_h - heatmap_full.shape[0])
        pad_w = max(0, orig_w - heatmap_full.shape[1])
        heatmap_full = np.pad(heatmap_full, ((0, pad_h), (0, pad_w)), mode="edge")

    return heatmap_full, heatmap_raw


def overlay_fractal_heatmap_rgb(
    base_image: np.ndarray,
    heatmap: np.ndarray,
    alpha: float = 0.45,
    threshold_healthy: float = None,
    threshold_warning: float = None,
) -> np.ndarray:
    """
    Genera una superposición RGB a color (Alpha Blending) adaptativa basada en la distribución local de la radiografía:
        🟢 Verde: Zonas de mayor densidad y complejidad trabecular relativa (dentro de norma)
        🟡 Amarillo: Zonas intermedias de transición
        🔴 Rojo: Zonas de menor densidad trabecular relativa (rarefacción / pérdida ósea)
    """
    if base_image is None or base_image.size == 0:
        return np.zeros((10, 10, 3), dtype=np.uint8)

    if base_image.ndim == 3:
        base_image = base_image[:, :, 0]

    h, w = base_image.shape
    if heatmap.shape != (h, w):
        zoom_y = float(h) / float(heatmap.shape[0])
        zoom_x = float(w) / float(heatmap.shape[1])
        heatmap = zoom(heatmap, (zoom_y, zoom_x), order=1)[:h, :w]
        if heatmap.shape[0] < h or heatmap.shape[1] < w:
            pad_h = max(0, h - heatmap.shape[0])
            pad_w = max(0, w - heatmap.shape[1])
            heatmap = np.pad(heatmap, ((0, pad_h), (0, pad_w)), mode="edge")

    if base_image.dtype == np.uint8:
        norm_base = base_image.astype(np.float32) / 255.0
        uint8_base = base_image
    else:
        norm_base = base_image.astype(np.float32)
        uint8_base = (np.clip(norm_base, 0, 1) * 255.0).astype(np.uint8)

    base_rgb = np.stack([norm_base] * 3, axis=-1)

    # Calibración adaptativa basada en la distribución estadística de la propia imagen
    h_mean = float(np.mean(heatmap))
    h_std = float(np.std(heatmap))

    if threshold_healthy is None or threshold_healthy > np.max(heatmap) or threshold_warning < np.min(heatmap):
        th_healthy = h_mean + 0.25 * h_std
        th_warning = h_mean - 0.35 * h_std
    else:
        th_healthy = threshold_healthy
        th_warning = threshold_warning

    color_map = np.zeros((h, w, 3), dtype=np.float32)

    mask_healthy = heatmap >= th_healthy
    mask_warning = (heatmap >= th_warning) & (heatmap < th_healthy)
    mask_danger = heatmap < th_warning

    color_map[mask_healthy] = [0.1, 0.8, 0.2]   # Verde sano / estructura densa
    color_map[mask_warning] = [0.95, 0.75, 0.1] # Amarillo advertencia / transición
    color_map[mask_danger]  = [0.9, 0.2, 0.2]   # Rojo riesgo / rarefacción

    # Enmascarar zonas de aire/fondo negro ultra oscuro y brillos extremos (no son tejido trabecular)
    non_tissue_mask = (uint8_base < 20) | (uint8_base > 250)

    alpha_clamped = max(0.0, min(1.0, float(alpha)))
    alpha_map = np.full((h, w), alpha_clamped, dtype=np.float32)
    alpha_map[non_tissue_mask] = 0.0  # Fondo transparente

    overlay = (1.0 - alpha_map[:, :, None]) * base_rgb + alpha_map[:, :, None] * color_map
    overlay = np.clip(overlay * 255.0, 0, 255).astype(np.uint8)

    return overlay
