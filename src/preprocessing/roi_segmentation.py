"""
Módulo de Segmentación Autónoma de Regiones de Interés (ROIs) Interdentales.
Aísla la zona interproximal trabecular (1.5 x 3.0 mm) excluyendo dientes y aire.
"""

from typing import List, Tuple
import numpy as np
import cv2


def extract_interdental_rois(
    image: np.ndarray,
    roi_size: Tuple[int, int] = (64, 128),
    max_rois: int = 4,
) -> List[Tuple[np.ndarray, Tuple[int, int, int, int]]]:
    """
    Detecta y recorta automáticamente las regiones trabeculares interdentales prioritarias.
    Returns:
        Lista de tuplas (roi_crop, (x, y, w, h)).
    """
    if image is None or image.size == 0:
        return []

    if image.ndim == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    else:
        gray = image.copy()

    h, w = gray.shape
    roi_w, roi_h = roi_size

    if h < roi_h or w < roi_w:
        # Si la imagen es más pequeña que la ROI, retornar la imagen completa
        return [(gray, (0, 0, w, h))]

    # Encontrar la zona del cuerpo mandibular (franja central-inferior)
    ymin, ymax = int(h * 0.40), int(h * 0.85)
    xmin, xmax = int(w * 0.15), int(w * 0.85)

    sub_img = gray[ymin:ymax, xmin:xmax]
    sub_h, sub_w = sub_img.shape

    # Mapeo de varianza de textura para priorizar hueso trabecular frente a dientes/aire
    laplacian = cv2.Laplacian(sub_img, cv2.CV_32F)
    variance_map = cv2.blur(np.abs(laplacian), (15, 15))

    rois = []
    step_x = max(roi_w // 2, (xmax - xmin) // (max_rois + 1))

    for x_offset in range(0, sub_w - roi_w + 1, step_x):
        window_var = variance_map[0:sub_h - roi_h + 1, x_offset:x_offset + roi_w]
        if window_var.size == 0:
            continue
            
        best_y_idx = np.unravel_index(np.argmax(window_var), window_var.shape)[0]
        
        real_x = xmin + x_offset
        real_y = ymin + best_y_idx

        roi_crop = gray[real_y : real_y + roi_h, real_x : real_x + roi_w]
        rois.append((roi_crop, (real_x, real_y, roi_w, roi_h)))

        if len(rois) >= max_rois:
            break

    if not rois:
        # Fallback a recorte central
        cx, cy = w // 2 - roi_w // 2, h // 2 - roi_h // 2
        rois.append((gray[cy : cy + roi_h, cx : cx + roi_w], (cx, cy, roi_w, roi_h)))

    return rois
