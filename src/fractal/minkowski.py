"""
Algoritmo de Manta de Minkowski (Minkowski Cover / Peleg Blanket Method) sobre Escala de Grises.
Refactorizado (Fase 4):
- Escala de intensidad estandarizada [0, 255] sin factores divididos por 4 arbitrarios.
- Sin clamping silencioso [2.0, 3.0] para visibilizar fallos de regresión o superficies planas.
- Devuelve R² de ajuste lineal sin distorsión.
"""

from typing import Dict, Any
import numpy as np


def compute_minkowski_blanket_dimension(
    grayscale_image: np.ndarray,
    max_scale: int = 5,
) -> Dict[str, Any]:
    """
    Calcula la Dimensión Fractal de Minkowski Cover (Peleg et al. 1984) sobre una imagen en escala de grises.

    Fórmula:
        u(x,y,0) = I(x,y)
        b(x,y,0) = I(x,y)

        u(x,y,ε) = max(u(x,y,ε-1) + 1, max_N u)
        b(x,y,ε) = min(b(x,y,ε-1) - 1, min_N b)

        Área A(ε) = (V(ε) - V(ε-1)) / 2
        Dimensión fractal D_M = 2 - slope(log A(ε) vs log ε)

    Args:
        grayscale_image: Imagen 2D en escala de grises (uint8 o float [0, 255]).
        max_scale: Escala máxima ε (típicamente 4 o 5).

    Returns:
        Diccionario con 'minkowski_dimension', 'r_squared', 'volumes', 'areas', 'scales'.
    """
    if grayscale_image.ndim != 2:
        raise ValueError("La imagen debe ser 2D en escala de grises.")

    img = grayscale_image.astype(np.float64)
    min_val, max_val = img.min(), img.max()

    if max_val - min_val > 1e-8:
        # Estandarizar rango dinámico continuo a escala fija [0, 255]
        img_scaled = ((img - min_val) / (max_val - min_val)) * 255.0
    else:
        img_scaled = np.zeros_like(img)

    u = img_scaled.copy()
    b = img_scaled.copy()

    volumes = []
    areas = []
    scales = list(range(1, max_scale + 1))
    v_prev = 0.0

    for eps in scales:
        u_padded = np.pad(u, 1, mode="edge")
        u_neighbors = np.maximum.reduce([
            u_padded[1:-1, 1:-1] + 1.0,
            u_padded[:-2, 1:-1],
            u_padded[2:, 1:-1],
            u_padded[1:-1, :-2],
            u_padded[1:-1, 2:],
        ])
        u = u_neighbors

        b_padded = np.pad(b, 1, mode="edge")
        b_neighbors = np.minimum.reduce([
            b_padded[1:-1, 1:-1] - 1.0,
            b_padded[:-2, 1:-1],
            b_padded[2:, 1:-1],
            b_padded[1:-1, :-2],
            b_padded[1:-1, 2:],
        ])
        b = b_neighbors

        v_curr = float(np.sum(u - b))
        volumes.append(v_curr)

        if eps == 1:
            a_curr = v_curr / 2.0
        else:
            a_curr = (v_curr - v_prev) / 2.0

        areas.append(a_curr)
        v_prev = v_curr

    scales_arr = np.array(scales, dtype=float)
    areas_arr = np.array(areas, dtype=float)

    valid = (scales_arr > 0) & (areas_arr > 0)
    if np.sum(valid) >= 3:
        log_eps = np.log(scales_arr[valid])
        log_a = np.log(areas_arr[valid])

        coeffs = np.polyfit(log_eps, log_a, deg=1)
        slope = float(coeffs[0])
        intercept = float(coeffs[1])

        d_minkowski = float(2.0 - slope)

        y_pred = slope * log_eps + intercept
        ss_res = np.sum((log_a - y_pred) ** 2)
        ss_tot = np.sum((log_a - np.mean(log_a)) ** 2)
        r2 = float(1.0 - (ss_res / (ss_tot + 1e-12))) if ss_tot > 0 else 0.0
    else:
        d_minkowski = 2.0
        r2 = 0.0

    return {
        "minkowski_dimension": d_minkowski,
        "r_squared": r2,
        "volumes": volumes,
        "areas": areas,
        "scales": scales,
    }
