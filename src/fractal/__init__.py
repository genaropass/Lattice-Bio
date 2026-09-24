"""
Módulo de Geometría Fractal y Análisis Topológico de Datos (TDA) para MorphoEngine.
"""

from .box_counting import compute_box_counting_dimension, compute_lapidus_oscillation
from .lacunarity import compute_gliding_box_lacunarity, compute_lacunarity_spectrum
from .multifractal import compute_multifractal_spectrum
from .tda_features import compute_topological_features
from .feature_extractor import FractalFeatureExtractor

__all__ = [
    "compute_box_counting_dimension",
    "compute_lapidus_oscillation",
    "compute_gliding_box_lacunarity",
    "compute_lacunarity_spectrum",
    "compute_multifractal_spectrum",
    "compute_topological_features",
    "FractalFeatureExtractor",
]
