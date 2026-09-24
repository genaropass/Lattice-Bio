"""
Módulo de Fusión de Características y Benchmark Comparativo de Machine Learning.
"""

from .feature_fusion import (
    BenchmarkExperiment,
    evaluate_hybrid_fusion,
    train_xgboost_classifier,
)

__all__ = [
    "BenchmarkExperiment",
    "evaluate_hybrid_fusion",
    "train_xgboost_classifier",
]
