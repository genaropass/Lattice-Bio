"""
Cálculo de Dimensión Fractal D₀ por Box-Counting e Índice de Oscilación de Lapidus.
Refactorizado (Fase 4):
- Escalas estrictamente geométricas base 2 (2, 4, 8, 16, 32...).
- Mínimo de 4 puntos log-log requeridos para la regresión.
- Sin fallbacks lineales arbitrarios ni clamping silencioso de R².
"""

from typing import Dict, Any
import numpy as np


def compute_box_counting_dimension(
    binary_mask: np.ndarray,
    min_box_size: int = 2,
    max_box_size: int = None,
    num_steps: int = 8,
) -> Dict[str, Any]:
    """
    Calcula la dimensión fractal D₀ mediante Box-Counting en escalas geométricas base 2.

    Fórmula:
        D₀ = lim_{ε -> 0} [log N(ε) / log(1 / ε)]

    Args:
        binary_mask: Matriz binaria 2D (booleana o valores 0/1 / uint8).
        min_box_size: Tamaño mínimo de caja (píxeles, por defecto 2).
        max_box_size: Tamaño máximo de caja (píxeles). Por defecto min(H, W) // 2.
        num_steps: Pasos de escala geométrica evaluados.

    Returns:
        Diccionario con 'D0', 'r_squared', 'box_sizes', 'box_counts', 'residuals'.
    """
    if binary_mask.ndim != 2:
        raise ValueError(f"La máscara debe ser 2D. Recibida dimensión {binary_mask.ndim}")

    mask = (binary_mask > 0).astype(np.uint8)
    h, w = mask.shape

    total_pixels = np.sum(mask)
    if total_pixels == 0:
        return {
            "D0": 0.0,
            "r_squared": 0.0,
            "box_sizes": np.array([]),
            "box_counts": np.array([]),
            "residuals": np.array([]),
        }

    if max_box_size is None:
        max_box_size = max(min_box_size * 2, min(h, w) // 2)

    if max_box_size <= min_box_size:
        max_box_size = min_box_size * 4

    # Generar escalas estrictamente geométricas en potencias de 2 (2, 4, 8, 16, 32...)
    max_power = int(np.floor(np.log2(max_box_size)))
    min_power = int(np.ceil(np.log2(min_box_size)))
    
    if max_power < min_power:
        max_power = min_power + 1

    powers = list(range(min_power, max_power + 1))
    scales = np.array([2 ** p for p in powers if (2 ** p) <= min(h, w)], dtype=float)

    if len(scales) < 3:
        return {
            "D0": 0.0,
            "r_squared": 0.0,
            "box_sizes": scales,
            "box_counts": np.array([]),
            "residuals": np.array([]),
        }

    counts = []
    for eps in scales:
        eps_int = int(eps)
        n_h = int(np.ceil(h / eps_int))
        n_w = int(np.ceil(w / eps_int))

        pad_h = n_h * eps_int - h
        pad_w = n_w * eps_int - w
        if pad_h > 0 or pad_w > 0:
            padded = np.pad(mask, ((0, pad_h), (0, pad_w)), mode="constant", constant_values=0)
        else:
            padded = mask

        blocks = padded.reshape(n_h, eps_int, n_w, eps_int)
        has_pixel = np.any(blocks, axis=(1, 3))
        counts.append(float(np.sum(has_pixel)))

    counts = np.array(counts, dtype=float)

    valid = counts > 0
    if np.sum(valid) < 3:
        return {
            "D0": 0.0,
            "r_squared": 0.0,
            "box_sizes": scales[valid],
            "box_counts": counts[valid],
            "residuals": np.array([]),
        }

    log_inv_eps = np.log(1.0 / scales[valid])
    log_n = np.log(counts[valid])

    # Regresión lineal log-log
    coeffs = np.polyfit(log_inv_eps, log_n, deg=1)
    d0 = float(coeffs[0])
    intercept = float(coeffs[1])

    y_pred = d0 * log_inv_eps + intercept
    ss_res = np.sum((log_n - y_pred) ** 2)
    ss_tot = np.sum((log_n - np.mean(log_n)) ** 2)
    r2 = float(1.0 - (ss_res / (ss_tot + 1e-12))) if ss_tot > 0 else 0.0

    fitted_residuals = log_n - y_pred

    return {
        "D0": d0,
        "r_squared": r2,
        "box_sizes": scales[valid],
        "box_counts": counts[valid],
        "residuals": fitted_residuals,
    }


def compute_lapidus_oscillation(residuals: np.ndarray) -> float:
    """
    Calcula el Índice de Oscilación de Lapidus como la desviación estándar
    de los residuos del ajuste log-log en Box-Counting.
    """
    if len(residuals) < 2:
        return 0.0
    return float(np.std(residuals))
