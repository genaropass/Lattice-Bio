"""
Módulo de Segmentación Autónoma de Regiones de Interés (ROIs) Anatómicas Interdentales y Basales.
Versión Congelada para Fase 6: Definición Anatómica Geométrica Independiente de la Textura.
"""

from typing import Dict, List, Tuple
import numpy as np
import cv2


def extract_anatomical_reference_rois(
    image: np.ndarray,
    patch_size: Tuple[int, int] = (64, 64),
    crest_y_ratio: float = 0.45,
    basal_y_ratio: float = 0.80,
    x_ratio: float = 0.50,
) -> Dict[str, Tuple[np.ndarray, Tuple[int, int, int, int]]]:
    """
    Extracción puramente geométrica y determinista de las dos ROIs de referencia anatómica:
    - Cresta Alveolar / Interdental (ROI A): Zona interproximal trabecular (cervical-coronal).
    - Hueso Trabecular Basal (ROI B): Zona cortical/basal trabecular de referencia intra-imagen.
    
    Independiente 100% de la textura, intensidad o modulación de gris de la imagen.

    Args:
        image: Imagen 2D en escala de grises o BGR/RGB.
        patch_size: Tamaño (ancho, alto) de la ROI recortada (por defecto 64x64 px).
        crest_y_ratio: Posición vertical relativa del centro de la Cresta (45% de la altura).
        basal_y_ratio: Posición vertical relativa del centro de la ROI Basal (80% de la altura).
        x_ratio: Posición horizontal relativa del centro de las ROIs (50% del ancho).

    Returns:
        Diccionario con claves 'crest' y 'basal', cada una conteniendo (crop_array, (x, y, w, h)).
    """
    if image is None or image.size == 0:
        empty = np.zeros((1, 1), dtype=np.uint8)
        return {
            "crest": (empty, (0, 0, 0, 0)),
            "basal": (empty, (0, 0, 0, 0)),
        }

    if image.ndim == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()

    h, w = gray.shape
    pw, ph = patch_size

    # Calcular coordenadas centroides geométricas
    cx = int(round(w * x_ratio))
    cy_crest = int(round(h * crest_y_ratio))
    cy_basal = int(round(h * basal_y_ratio))

    # Definir esquinas superiores izquierdas con bound checking
    x1_crest = max(0, min(w - pw, cx - pw // 2))
    y1_crest = max(0, min(h - ph, cy_crest - ph // 2))

    x1_basal = max(0, min(w - pw, cx - pw // 2))
    y1_basal = max(0, min(h - ph, cy_basal - ph // 2))

    # Recortes
    crop_crest = gray[y1_crest : y1_crest + ph, x1_crest : x1_crest + pw]
    crop_basal = gray[y1_basal : y1_basal + ph, x1_basal : x1_basal + pw]

    # Redimensionar si la imagen fuente era más pequeña que la ROI
    if crop_crest.shape != (ph, pw):
        crop_crest = cv2.resize(crop_crest, (pw, ph), interpolation=cv2.INTER_LANCZOS4)
    if crop_basal.shape != (ph, pw):
        crop_basal = cv2.resize(crop_basal, (pw, ph), interpolation=cv2.INTER_LANCZOS4)

    return {
        "crest": (crop_crest, (x1_crest, y1_crest, pw, ph)),
        "basal": (crop_basal, (x1_basal, y1_basal, pw, ph)),
    }


def extract_interdental_rois(
    image: np.ndarray,
    roi_size: Tuple[int, int] = (64, 128),
    max_rois: int = 4,
    method: str = "geometric",
) -> List[Tuple[np.ndarray, Tuple[int, int, int, int]]]:
    """
    Función de compatibilidad con versiones anteriores para extracción de ROIs interdentales.
    """
    if method == "geometric":
        refs = extract_anatomical_reference_rois(image, patch_size=(roi_size[0], roi_size[1]))
        return [refs["crest"], refs["basal"]]
    
    # Implementación legacy por varianza de textura (conservada solo para referencia histórica)
    if image is None or image.size == 0:
        return []

    if image.ndim == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    else:
        gray = image.copy()

    h, w = gray.shape
    roi_w, roi_h = roi_size

    if h < roi_h or w < roi_w:
        return [(gray, (0, 0, w, h))]

    ymin, ymax = int(h * 0.40), int(h * 0.85)
    xmin, xmax = int(w * 0.15), int(w * 0.85)

    sub_img = gray[ymin:ymax, xmin:xmax]
    sub_h, sub_w = sub_img.shape

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
        cx, cy = w // 2 - roi_w // 2, h // 2 - roi_h // 2
        rois.append((gray[cy : cy + roi_h, cx : cx + roi_w], (cx, cy, roi_w, roi_h)))

    return rois
