"""
Extractor Unificado de Características Fractales y Topológicas (FractalFeatureExtractor).
"""

from typing import Dict, Any, Union
import numpy as np
import pandas as pd

from .box_counting import compute_box_counting_dimension, compute_lapidus_oscillation
from .lacunarity import compute_lacunarity_spectrum
from .multifractal import compute_multifractal_spectrum
from .tda_features import compute_topological_features
from .minkowski import compute_minkowski_blanket_dimension


class FractalFeatureExtractor:
    """
    Orquestador científico modular para extraer el vector completo de biomarcadores
    fractales (Box-Counting, Manta de Minkowski, Lacunaridad, Multifractal) y topológicos (TDA).
    """

    def __init__(
        self,
        box_min: int = 2,
        box_max: int = None,
        lacunarity_scales: int = 6,
        multifractal_q_steps: int = 15,
        use_tda: bool = True,
        use_minkowski: bool = True,
    ):
        self.box_min = box_min
        self.box_max = box_max
        self.lacunarity_scales = lacunarity_scales
        self.multifractal_q_steps = multifractal_q_steps
        self.use_tda = use_tda
        self.use_minkowski = use_minkowski

    def extract_features(
        self,
        roi_mask: np.ndarray,
        roi_grayscale: np.ndarray = None,
    ) -> Dict[str, float]:
        """
        Calcula todos los biomarcadores cuantitativos sobre la región de interés.

        Args:
            roi_mask: Matriz binaria 2D (estructura trabecular / lesión binarizada).
            roi_grayscale: Imagen 2D opcional en escala de grises para Minkowski y Multifractal.

        Returns:
            Diccionario plano {nombre_metrica: valor_flotante}.
        """
        features = {}

        # 1. Dimensión Fractal D₀ por Box-Counting e Índice de Lapidus
        bc_results = compute_box_counting_dimension(
            roi_mask,
            min_box_size=self.box_min,
            max_box_size=self.box_max,
        )
        features["fractal_D0"] = float(bc_results["D0"])
        features["fractal_r2"] = float(bc_results["r_squared"])
        features["lapidus_oscillation"] = compute_lapidus_oscillation(bc_results["residuals"])

        # 2. Manta de Minkowski (Fractal 3D sobre escala de grises sin binarización destructiva)
        if self.use_minkowski:
            gray_input = roi_grayscale if roi_grayscale is not None else (roi_mask * 255)
            mink_results = compute_minkowski_blanket_dimension(gray_input, max_scale=4)
            features["minkowski_dimension"] = float(mink_results["minkowski_dimension"])
            features["minkowski_r2"] = float(mink_results["r_squared"])

        # 3. Espectro de Lacunaridad
        lac_results = compute_lacunarity_spectrum(
            roi_mask,
            min_box=self.box_min,
            max_box=self.box_max,
            num_scales=self.lacunarity_scales,
        )
        features["lacunarity_mean"] = float(lac_results["mean_lacunarity"])
        features["lacunarity_slope"] = float(lac_results["lacunarity_slope"])

        # 4. Espectro Multifractal f(α) y Heterogeneidad Δα
        mf_input = roi_grayscale if roi_grayscale is not None else roi_mask
        q_range = np.linspace(-4.0, 4.0, num=self.multifractal_q_steps)
        mf_results = compute_multifractal_spectrum(mf_input, q_range=q_range)
        features["multifractal_delta_alpha"] = float(mf_results["delta_alpha"])
        features["multifractal_D1"] = float(mf_results["D1"])
        features["multifractal_D2"] = float(mf_results["D2"])

        # 5. Topología y Homología Persistente (TDA)
        if self.use_tda:
            tda_results = compute_topological_features(roi_mask)
            features["tda_beta_0"] = float(tda_results["beta_0"])
            features["tda_beta_1"] = float(tda_results["beta_1"])
            features["tda_betti_ratio"] = float(tda_results["betti_ratio"])
            features["tda_persistence_entropy_h0"] = float(tda_results["persistence_entropy_h0"])
            features["tda_persistence_entropy_h1"] = float(tda_results["persistence_entropy_h1"])
            features["tda_mean_persistence_h1"] = float(tda_results["mean_persistence_h1"])

        return features

    def extract_to_dataframe(self, rois: list, ids: list = None) -> pd.DataFrame:
        """
        Extrae características de una lista de ROIs y las devuelve en formato DataFrame de pandas.
        """
        rows = []
        for i, roi in enumerate(rois):
            feats = self.extract_features(roi)
            if ids is not None and i < len(ids):
                feats["sample_id"] = ids[i]
            rows.append(feats)
        return pd.DataFrame(rows)
