"""
Pipeline de Fusión de Características y Benchmark Comparativo para Publicación Científica.
"""

from typing import Dict, Any, Tuple, List
import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import (
    roc_auc_score,
    f1_score,
    accuracy_score,
    precision_score,
    recall_score,
    classification_report,
)
import xgboost as xgb


def train_xgboost_classifier(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_val: np.ndarray = None,
    y_val: np.ndarray = None,
    params: Dict[str, Any] = None,
) -> xgb.XGBClassifier:
    """
    Entrena un clasificador XGBoost con regularización adecuada para prevenir sobreajuste.
    """
    default_params = {
        "n_estimators": 150,
        "max_depth": 4,
        "learning_rate": 0.05,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "random_state": 42,
        "eval_metric": "logloss",
    }
    if params:
        default_params.update(params)

    model = xgb.XGBClassifier(**default_params)
    if X_val is not None and y_val is not None:
        model.fit(
            X_train,
            y_train,
            eval_set=[(X_val, y_val)],
            verbose=False,
        )
    else:
        model.fit(X_train, y_train, verbose=False)

    return model


class BenchmarkExperiment:
    """
    Ejecuta el protocolo de validación cruzada estratificada (K-Fold)
    comparando los 3 escenarios clave del paper científico:
    1. Solo Características Fractales / Topológicas
    2. Solo Embeddings de Visión Profunda (CNN / DINOv2)
    3. Fusión Híbrida (Embeddings + Fractales)
    """

    def __init__(
        self,
        n_splits: int = 5,
        random_state: int = 42,
    ):
        self.n_splits = n_splits
        self.random_state = random_state

    def run_cv_evaluation(
        self,
        X: np.ndarray,
        y: np.ndarray,
        feature_names: List[str] = None,
    ) -> Dict[str, Any]:
        """
        Ejecuta validación cruzada estratificada y recolecta métricas con intervalos de confianza.
        """
        skf = StratifiedKFold(n_splits=self.n_splits, shuffle=True, random_state=self.random_state)
        
        auc_scores = []
        f1_scores = []
        acc_scores = []
        feature_importances = []

        is_multiclass = len(np.unique(y)) > 2

        for fold, (train_idx, test_idx) in enumerate(skf.split(X, y)):
            X_train, X_test = X[train_idx], X[test_idx]
            y_train, y_test = y[train_idx], y[test_idx]

            model = train_xgboost_classifier(X_train, y_train, X_test, y_test)
            y_pred = model.predict(X_test)
            y_proba = model.predict_proba(X_test)

            acc = accuracy_score(y_test, y_pred)
            f1 = f1_score(y_test, y_pred, average="macro" if is_multiclass else "binary")

            if is_multiclass:
                try:
                    auc = roc_auc_score(y_test, y_proba, multi_class="ovr", average="macro")
                except ValueError:
                    auc = 0.5
            else:
                try:
                    auc = roc_auc_score(y_test, y_proba[:, 1])
                except ValueError:
                    auc = 0.5

            auc_scores.append(auc)
            f1_scores.append(f1)
            acc_scores.append(acc)

            if hasattr(model, "feature_importances_"):
                feature_importances.append(model.feature_importances_)

        mean_auc = float(np.mean(auc_scores))
        std_auc = float(np.std(auc_scores))
        mean_f1 = float(np.mean(f1_scores))
        std_f1 = float(np.std(f1_scores))
        mean_acc = float(np.mean(acc_scores))

        avg_importances = None
        if feature_importances:
            mean_imp = np.mean(feature_importances, axis=0)
            if feature_names and len(feature_names) == len(mean_imp):
                avg_importances = dict(zip(feature_names, [float(v) for v in mean_imp]))
            else:
                avg_importances = {f"feature_{i}": float(v) for i, v in enumerate(mean_imp)}

        return {
            "mean_auc": mean_auc,
            "std_auc": std_auc,
            "mean_f1": mean_f1,
            "std_f1": std_f1,
            "mean_accuracy": mean_acc,
            "fold_aucs": auc_scores,
            "fold_f1s": f1_scores,
            "feature_importances": avg_importances,
        }

    def run_full_comparative_benchmark(
        self,
        X_fractal: np.ndarray,
        X_embeddings: np.ndarray,
        y: np.ndarray,
        fractal_names: List[str] = None,
        embedding_names: List[str] = None,
    ) -> pd.DataFrame:
        """
        Ejecuta el benchmark completo comparando:
        - Exp 1: Solo Fractales
        - Exp 2: Solo Embeddings
        - Exp 3: Fusión Híbrida (Embeddings + Fractales)
        """
        # 1. Solo Fractales
        res_fractal = self.run_cv_evaluation(X_fractal, y, feature_names=fractal_names)

        # 2. Solo Embeddings
        res_embed = self.run_cv_evaluation(X_embeddings, y, feature_names=embedding_names)

        # 3. Híbrido
        X_hybrid = np.hstack([X_embeddings, X_fractal])
        all_names = (embedding_names or []) + (fractal_names or [])
        res_hybrid = self.run_cv_evaluation(
            X_hybrid, y, feature_names=all_names if len(all_names) == X_hybrid.shape[1] else None
        )

        results_table = pd.DataFrame([
            {
                "Experimento": "1. Solo Características Fractales / TDA",
                "AUC-ROC (Media ± Desv)": f"{res_fractal['mean_auc']:.3f} ± {res_fractal['std_auc']:.3f}",
                "F1-Score (Macro)": f"{res_fractal['mean_f1']:.3f} ± {res_fractal['std_f1']:.3f}",
                "Accuracy": f"{res_fractal['mean_accuracy']:.3f}",
                "AUC_raw": res_fractal["mean_auc"],
            },
            {
                "Experimento": "2. Solo Embeddings de Visión Profunda",
                "AUC-ROC (Media ± Desv)": f"{res_embed['mean_auc']:.3f} ± {res_embed['std_auc']:.3f}",
                "F1-Score (Macro)": f"{res_embed['mean_f1']:.3f} ± {res_embed['std_f1']:.3f}",
                "Accuracy": f"{res_embed['mean_accuracy']:.3f}",
                "AUC_raw": res_embed["mean_auc"],
            },
            {
                "Experimento": "3. Fusión Híbrida (Embeddings + Fractales)",
                "AUC-ROC (Media ± Desv)": f"{res_hybrid['mean_auc']:.3f} ± {res_hybrid['std_auc']:.3f}",
                "F1-Score (Macro)": f"{res_hybrid['mean_f1']:.3f} ± {res_hybrid['std_f1']:.3f}",
                "Accuracy": f"{res_hybrid['mean_accuracy']:.3f}",
                "AUC_raw": res_hybrid["mean_auc"],
            },
        ])

        return results_table


def evaluate_hybrid_fusion(
    X_fractal: np.ndarray,
    X_embeddings: np.ndarray,
    y: np.ndarray,
    fractal_names: List[str] = None,
) -> pd.DataFrame:
    """Helper directo para correr el benchmark comparativo con 5-fold CV."""
    bench = BenchmarkExperiment(n_splits=5)
    return bench.run_full_comparative_benchmark(
        X_fractal, X_embeddings, y, fractal_names=fractal_names
    )
