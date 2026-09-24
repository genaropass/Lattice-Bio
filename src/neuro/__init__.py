"""
Módulo de Procesamiento y Biomarcadores Fractales para Señales Neurológicas (EEG / EMG / Series Temporales).
"""

from .signals import (
    compute_higuchi_fd,
    compute_hurst_exponent,
    extract_signal_fractal_features,
)

__all__ = [
    "compute_higuchi_fd",
    "compute_hurst_exponent",
    "extract_signal_fractal_features",
]
