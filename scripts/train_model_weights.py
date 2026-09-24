"""
Entrenamiento y Exportación del Modelo Calibrado de Lattice Bio (XGBoost).
Guarda los pesos entrenados en data/processed/latticebio_model.json.
"""

import os
import sys
import pandas as pd
import numpy as np
from xgboost import XGBClassifier

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, ".."))
csv_path = os.path.join(root_dir, "data", "processed", "dataset_latticebio_features.csv")
model_save_path = os.path.join(root_dir, "data", "processed", "latticebio_model.json")

df = pd.read_csv(csv_path)
df["target"] = (df["source_dataset"].str.contains("Periodontal", case=False)).astype(int)

non_feat = ["filepath", "source_dataset", "filename", "sample_id", "target", "img_height", "img_width"]
feature_cols = [c for c in df.columns if c not in non_feat]

X = df[feature_cols].values
y = df["target"].values

print(f"Entrenando modelo XGBoost sobre {len(df)} radiografías y {len(feature_cols)} características...")

model = XGBClassifier(
    n_estimators=150,
    max_depth=4,
    learning_rate=0.05,
    random_state=42,
    eval_metric="logloss"
)
model.fit(X, y)

model.save_model(model_save_path)
print(f"[OK] Modelo calibrado guardado exitosamente en: {model_save_path}")
