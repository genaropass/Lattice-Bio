"""
Tests unitarios de precisión matemática y robustez para MorphoEngine (incluyendo Minkowski, Heatmaps y Neuro).
"""

import unittest
import numpy as np

from src.fractal.box_counting import compute_box_counting_dimension, compute_lapidus_oscillation
from src.fractal.lacunarity import compute_gliding_box_lacunarity, compute_lacunarity_spectrum
from src.fractal.multifractal import compute_multifractal_spectrum
from src.fractal.minkowski import compute_minkowski_blanket_dimension
from src.fractal.local_heatmap import compute_local_fractal_heatmap, overlay_fractal_heatmap_rgb
from src.fractal.feature_extractor import FractalFeatureExtractor
from src.neuro.signals import compute_higuchi_fd, compute_hurst_exponent, extract_signal_fractal_features


class TestMorphoEngineFractals(unittest.TestCase):
    def test_box_counting_filled_square(self):
        """Un cuadrado sólido 2D bidimensional debe tener D0 ≈ 2.0 (con R² alto)."""
        mask = np.ones((128, 128), dtype=np.uint8)
        res = compute_box_counting_dimension(mask, min_box_size=2, max_box_size=32)
        self.assertGreater(res["D0"], 1.80)
        self.assertGreater(res["r_squared"], 0.98)

    def test_minkowski_blanket(self):
        """La manta de Minkowski sobre escala de grises debe retornar D_M en rango válido."""
        img = (np.random.rand(64, 64) * 255).astype(np.uint8)
        res = compute_minkowski_blanket_dimension(img, max_scale=4)
        self.assertGreaterEqual(res["minkowski_dimension"], 1.5)
        self.assertLessEqual(res["minkowski_dimension"], 3.5)

    def test_local_heatmap(self):
        """El mapa de calor local debe generar una matriz de dimensiones del tamaño completo de la imagen."""
        img = (np.random.rand(64, 64) * 255).astype(np.uint8)
        heatmap, raw = compute_local_fractal_heatmap(img, window_size=16, stride=8, method="minkowski")
        self.assertEqual(heatmap.shape, (64, 64))

        overlay = overlay_fractal_heatmap_rgb(img, heatmap, alpha=0.5)
        self.assertEqual(overlay.shape, (64, 64, 3))
        self.assertEqual(overlay.dtype, np.uint8)

    def test_higuchi_fd_and_hurst(self):
        """Higuchi FD y Hurst Exponent para señales neurológicas 1D."""
        np.random.seed(42)
        signal = np.sin(np.linspace(0, 10, 500)) + 0.1 * np.random.randn(500)
        hfd = compute_higuchi_fd(signal)
        hurst = compute_hurst_exponent(signal)

        self.assertGreaterEqual(hfd, 1.0)
        self.assertLessEqual(hfd, 2.0)
        self.assertGreaterEqual(hurst, 0.0)
        self.assertLessEqual(hurst, 1.0)

    def test_fractal_feature_extractor_with_minkowski(self):
        """El extractor unificado debe devolver el diccionario completo incluyendo Minkowski."""
        np.random.seed(42)
        mask = np.random.choice([0, 1], size=(64, 64), p=[0.7, 0.3]).astype(np.uint8)
        gray = (np.random.rand(64, 64) * 255).astype(np.uint8)

        extractor = FractalFeatureExtractor(use_tda=False, use_minkowski=True)
        feats = extractor.extract_features(mask, roi_grayscale=gray)

        expected_keys = [
            "fractal_D0",
            "minkowski_dimension",
            "lacunarity_mean",
            "multifractal_delta_alpha",
        ]
        for key in expected_keys:
            self.assertIn(key, feats)
            self.assertIsInstance(feats[key], float)


if __name__ == "__main__":
    unittest.main()
