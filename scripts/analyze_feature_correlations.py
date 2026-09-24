"""
Script de Análisis de Correlación y Multicolinealidad (VIF) de las Características de Lattice Bio.
Analiza la matriz de correlación de los 2,795 registros procesados en el dataset.
"""

import os
import sys
import numpy as np
import pandas as pd

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, ".."))
csv_path = os.path.join(root_dir, "data", "processed", "dataset_latticebio_features.csv")

if not os.path.exists(csv_path):
    print(f"Error: No se encontró el archivo CSV en {csv_path}")
    sys.exit(1)

print(f"Cargando dataset desde: {csv_path}")
df = pd.read_csv(csv_path)
print(f"Dataset cargado con {len(df)} filas y {len(df.columns)} columnas.")

# Filtrar columnas numéricas de biomarcadores
non_feature_cols = ["filepath", "source_dataset", "filename", "sample_id"]
feature_cols = [c for c in df.columns if c not in non_feature_cols]

print(f"\n--- Características Cuantitativas ({len(feature_cols)}) ---")
for col in feature_cols:
    print(f" - {col}")

# Matriz de Correlación de Pearson
corr = df[feature_cols].corr()

print("\n--- Matriz de Correlación de Pearson entre Métricas Clave ---")
key_metrics = ["fractal_D0", "minkowski_dimension", "lacunarity_mean", "multifractal_delta_alpha", "tda_betti_ratio"]
available_keys = [k for k in key_metrics if k in corr.columns]
print(corr[available_keys].loc[available_keys].round(3).to_string())

# Identificar pares con alta correlación (|r| > 0.70)
print("\n--- Pares con Alta Correlación (|r| > 0.70) ---")
high_corr_pairs = []
for i in range(len(feature_cols)):
    for j in range(i + 1, len(feature_cols)):
        col1 = feature_cols[i]
        col2 = feature_cols[j]
        r_val = corr.loc[col1, col2]
        if abs(r_val) > 0.70:
            high_corr_pairs.append((col1, col2, r_val))

if high_corr_pairs:
    for c1, c2, r in sorted(high_corr_pairs, key=lambda x: abs(x[2]), reverse=True):
        print(f" * {c1} <--> {c2}: r = {r:+.3f}")
else:
    print(" No se encontraron pares con |r| > 0.70.")

# Estadísticas Descriptivas
print("\n--- Resumen de Estadísticas Descriptivas (Empíricas del Dataset) ---")
stats_df = df[feature_cols].describe().T[["mean", "std", "min", "50%", "max"]]
stats_df.columns = ["Media", "Desv.Std", "Mín", "Mediana", "Máx"]
print(stats_df.round(4).to_string())

print("\n[OK] Analisis completado con exito.")
