"""
Cálculo de Lacunaridad por el algoritmo de Gliding Box (Allain & Cloitre 1991).
Refactorizado (Fase 4):
- Escalas geométricas puras base 2 (2, 4, 8, 16, 32...).
- Definición rigurosa de convolución deslizante mode='valid'.
"""

from typing import Dict, List, Any
import numpy as np
from scipy.signal import convolve2d


def compute_gliding_box_lacunarity(
    binary_mask: np.ndarray,
    box_size: int,
) -> float:
    """
    Calcula la lacunaridad Λ(r) para un tamaño de caja r específico usando una ventana deslizante.

    Fórmula:
        Λ(r) = E[s²] / (E[s])²
    """
    if binary_mask.ndim != 2:
        raise ValueError("La máscara debe ser bidimensional (2D).")

    mask = (binary_mask > 0).astype(np.float32)
    h, w = mask.shape

    if box_size <= 0 or box_size > min(h, w):
        return 1.0

    kernel = np.ones((box_size, box_size), dtype=np.float32)
    box_masses = convolve2d(mask, kernel, mode="valid")

    if box_masses.size == 0:
        return 1.0

    mean_mass = float(np.mean(box_masses))
    mean_sq_mass = float(np.mean(box_masses ** 2))

    if mean_mass <= 1e-8:
        return 0.0

    lacunarity = mean_sq_mass / (mean_mass ** 2)
    return float(lacunarity)


def compute_lacunarity_spectrum(
    binary_mask: np.ndarray,
    box_sizes: List[int] = None,
    min_box: int = 2,
    max_box: int = None,
    num_scales: int = 6,
) -> Dict[str, Any]:
    """
    Calcula el espectro de lacunaridad Λ(r) a través de escalas de caja geométricas en base 2.
    """
    h, w = binary_mask.shape
    if max_box is None:
        max_box = max(min_box * 2, min(h, w) // 3)

    if box_sizes is None:
        max_power = int(np.floor(np.log2(max_box)))
        min_power = int(np.ceil(np.log2(min_box)))
        if max_power < min_power:
            max_power = min_power + 1

        powers = list(range(min_power, max_power + 1))
        scales = [2 ** p for p in powers if (2 ** p) <= min(h, w)]
    else:
        scales = [int(s) for s in box_sizes if s >= 1 and s <= min(h, w)]

    if not scales:
        return {
            "mean_lacunarity": 1.0,
            "lacunarity_spectrum": np.array([]),
            "box_sizes": np.array([]),
            "lacunarity_slope": 0.0,
        }

    lacunarities = []
    for r in scales:
        lac = compute_gliding_box_lacunarity(binary_mask, box_size=r)
        lacunarities.append(lac)

    lacunarities = np.array(lacunarities, dtype=float)
    scales_arr = np.array(scales, dtype=float)

    valid = (lacunarities > 0) & (scales_arr > 0)
    if np.sum(valid) >= 3:
        coeffs = np.polyfit(np.log(scales_arr[valid]), np.log(lacunarities[valid]), deg=1)
        slope = float(coeffs[0])
    else:
        slope = 0.0

    return {
        "mean_lacunarity": float(np.mean(lacunarities)) if len(lacunarities) > 0 else 1.0,
        "lacunarity_spectrum": lacunarities,
        "box_sizes": scales_arr,
        "lacunarity_slope": slope,
    }
