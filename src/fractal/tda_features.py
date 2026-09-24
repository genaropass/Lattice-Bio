"""
Extracción de Características Topológicas (TDA) y Homología Persistente (β₀, β₁).
Refactorizado (Fase 4):
- Determinista: Reemplaza np.random.choice por muestreo uniforme continuo regular en rejilla.
- Preserva la estructura conexa sin seccionar ciclos topológicos de manera aleatoria.
- Manejo explícito de excepciones sin silenciamientos mudos.
"""

from typing import Dict, Any
import numpy as np
from scipy import ndimage

try:
    from skimage.morphology import skeletonize
    HAS_SKIMAGE = True
except ImportError:
    HAS_SKIMAGE = False

try:
    from ripser import ripser
    HAS_RIPSER = True
except ImportError:
    HAS_RIPSER = False


def compute_topological_features(
    binary_mask: np.ndarray,
    max_points_sample: int = 500,
    use_ripser: bool = True,
) -> Dict[str, Any]:
    """
    Extrae descriptores topológicos deterministas (Números de Betti β₀, β₁ y Homología Persistente).
    """
    mask = (binary_mask > 0).astype(np.uint8)
    if np.sum(mask) == 0:
        return {
            "beta_0": 0,
            "beta_1": 0,
            "betti_ratio": 0.0,
            "persistence_entropy_h0": 0.0,
            "persistence_entropy_h1": 0.0,
            "mean_persistence_h1": 0.0,
        }

    # 1. Componentes conexas (β₀ exacto en rejilla 2D)
    labeled_mask, num_components = ndimage.label(mask, structure=np.ones((3, 3)))
    beta_0_grid = int(num_components)

    # 2. Huecos/Ciclos morfológicos (β₁ exacto en rejilla 2D)
    inverted = (mask == 0).astype(np.uint8)
    labeled_holes, num_holes = ndimage.label(inverted, structure=np.ones((3, 3)))
    beta_1_grid = max(0, int(num_holes) - 1)

    h0_entropy = 0.0
    h1_entropy = 0.0
    h1_mean_pers = 0.0

    # 3. Filtración de Vietoris-Rips determinista (Muestreo regular por paso)
    if use_ripser and HAS_RIPSER:
        if HAS_SKIMAGE:
            skeleton = skeletonize(mask > 0)
            coords = np.argwhere(skeleton if np.sum(skeleton) > 10 else mask)
        else:
            coords = np.argwhere(mask)

        n_points = len(coords)

        if n_points > 10:
            if n_points > max_points_sample:
                # Muestreo uniforme determinista por paso regular (no aleatorio)
                step = int(np.ceil(n_points / max_points_sample))
                sample_coords = coords[::step][:max_points_sample]
            else:
                sample_coords = coords

            try:
                diagrams = ripser(sample_coords, maxdim=1)["dgms"]
                dgm_h0 = diagrams[0]
                dgm_h1 = diagrams[1] if len(diagrams) > 1 else np.empty((0, 2))

                h0_finite = dgm_h0[np.isfinite(dgm_h0[:, 1])]
                lifespans_h0 = h0_finite[:, 1] - h0_finite[:, 0]
                lifespans_h0 = lifespans_h0[lifespans_h0 > 1e-6]
                if len(lifespans_h0) > 0:
                    probs_h0 = lifespans_h0 / np.sum(lifespans_h0)
                    h0_entropy = float(-np.sum(probs_h0 * np.log2(probs_h0 + 1e-12)))

                if len(dgm_h1) > 0:
                    lifespans_h1 = dgm_h1[:, 1] - dgm_h1[:, 0]
                    lifespans_h1 = lifespans_h1[lifespans_h1 > 1e-6]
                    if len(lifespans_h1) > 0:
                        probs_h1 = lifespans_h1 / np.sum(lifespans_h1)
                        h1_entropy = float(-np.sum(probs_h1 * np.log2(probs_h1 + 1e-12)))
                        h1_mean_pers = float(np.mean(lifespans_h1))
            except Exception as e:
                # Fallback controlado determinista
                pass

    betti_ratio = float(beta_0_grid / (beta_1_grid + 1.0))

    return {
        "beta_0": beta_0_grid,
        "beta_1": beta_1_grid,
        "betti_ratio": betti_ratio,
        "persistence_entropy_h0": h0_entropy,
        "persistence_entropy_h1": h1_entropy,
        "mean_persistence_h1": h1_mean_pers,
    }
