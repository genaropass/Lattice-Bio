"""
Técnicas de Preprocesamiento de Radiografías: CLAHE, Normalización y Binarización Adaptativa.
Versión Robustecida para Producción y QA.
"""

from typing import Tuple
import numpy as np
import cv2
from skimage.filters import threshold_sauvola, threshold_local


def normalize_intensity(
    image: np.ndarray,
    method: str = "minmax",
) -> np.ndarray:
    """
    Normaliza el rango dinámico de una imagen radiográfica o recorte con protección ante varianza nula.
    """
    if image is None or image.size == 0:
        return np.zeros((1, 1), dtype=np.float32)

    img = image.astype(np.float32)
    if method == "minmax":
        min_val = float(np.min(img))
        max_val = float(np.max(img))
        if max_val - min_val > 1e-8:
            return (img - min_val) / (max_val - min_val)
        return np.zeros_like(img)
    elif method == "zscore":
        mean = float(np.mean(img))
        std = float(np.std(img))
        if std > 1e-8:
            return (img - mean) / std
        return img - mean
    else:
        raise ValueError(f"Método de normalización desconocido: {method}")


def apply_clahe(
    image: np.ndarray,
    clip_limit: float = 3.0,
    tile_grid_size: Tuple[int, int] = (8, 8),
) -> np.ndarray:
    """
    Aplica Ecualización de Histograma Adaptativa Limitada por Contraste (CLAHE)
    con verificación de tamaño y tipo de datos.
    """
    if image is None or image.size == 0:
        return np.zeros((10, 10), dtype=np.uint8)

    # Convertir a escala de grises si es RGB/RGBA
    if image.ndim == 3:
        if image.shape[2] == 4:
            image = cv2.cvtColor(image, cv2.COLOR_RGBA2GRAY)
        elif image.shape[2] == 3:
            image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

    if image.dtype != np.uint8:
        norm = normalize_intensity(image, method="minmax")
        uint8_img = (norm * 255.0).astype(np.uint8)
    else:
        uint8_img = image

    # Ajustar grilla si la imagen es más pequeña que tile_grid_size
    h, w = uint8_img.shape
    grid_y = min(tile_grid_size[0], max(1, h // 4))
    grid_x = min(tile_grid_size[1], max(1, w // 4))
    safe_grid = (grid_y, grid_x)

    clahe = cv2.createCLAHE(clipLimit=max(1.0, float(clip_limit)), tileGridSize=safe_grid)
    enhanced = clahe.apply(uint8_img)
    return enhanced


def adaptive_trabecular_binarization(
    image: np.ndarray,
    window_size: int = 25,
    k: float = 0.2,
    method: str = "sauvola",
) -> np.ndarray:
    """
    Binarización adaptativa local (Sauvola o Local Mean) blindada ante ventanas mayores que la imagen.
    """
    if image is None or image.size == 0:
        return np.zeros((10, 10), dtype=np.uint8)

    if image.ndim == 3:
        image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

    if image.dtype != np.uint8:
        norm = normalize_intensity(image, method="minmax")
        uint8_img = (norm * 255.0).astype(np.uint8)
    else:
        uint8_img = image

    h, w = uint8_img.shape
    # Asegurar que window_size sea impar y no supere la dimensión mínima de la imagen
    max_safe_window = min(h, w)
    if max_safe_window < 3:
        return (uint8_img > 128).astype(np.uint8)

    safe_window = min(window_size, max_safe_window)
    if safe_window % 2 == 0:
        safe_window = max(3, safe_window - 1)

    if method == "sauvola":
        try:
            thresh = threshold_sauvola(uint8_img, window_size=safe_window, k=float(k))
            binary = (uint8_img > thresh).astype(np.uint8)
        except Exception:
            # Fallback a Otsu global si Sauvola falla por dimensiones límite
            _, binary = cv2.threshold(uint8_img, 0, 1, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    else:
        thresh = threshold_local(uint8_img, block_size=safe_window, method="mean")
        binary = (uint8_img > thresh).astype(np.uint8)

    return binary


def standardize_spatial_resolution(
    image: np.ndarray,
    source_dpi: float = 150.0,
    target_pixel_um: float = 35.0,
) -> np.ndarray:
    """
    Re-muestrea la radiografía a una resolución espacial estandarizada (~35 µm/pixel)
    antes de cualquier análisis fractal, asegurando comparabilidad entre distintos sensores.
    
    Args:
        image: Imagen 2D de entrada.
        source_dpi: Puntos por pulgada del detector/escáner fuente.
        target_pixel_um: Resolución objetivo en micrómetros por pixel (35.0 µm es el estándar de literatura).
        
    Returns:
        Imagen re-muestreada con interpolación Lanczos4.
    """
    if image is None or image.size == 0:
        return image

    # 1 pulgada = 25,400 micrómetros
    current_um_per_pixel = 25400.0 / max(1.0, float(source_dpi))
    scale_factor = current_um_per_pixel / max(1.0, float(target_pixel_um))

    if abs(scale_factor - 1.0) < 0.05:
        return image

    h, w = image.shape[:2]
    new_h = max(16, int(round(h * scale_factor)))
    new_w = max(16, int(round(w * scale_factor)))

    return cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)


def preprocess_radiograph_roi(
    roi_image: np.ndarray,
    clip_limit: float = 2.5,
    sauvola_window: int = 25,
    source_dpi: float = 150.0,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Pipeline completo de preprocesamiento seguro.
    """
    resampled_img = standardize_spatial_resolution(roi_image, source_dpi=source_dpi)
    clahe_img = apply_clahe(resampled_img, clip_limit=clip_limit)
    binary_mask = adaptive_trabecular_binarization(clahe_img, window_size=sauvola_window)
    return clahe_img, binary_mask

