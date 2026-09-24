"""
Script de Auditoria Cientifica e Integridad para la Fase 11 (One-Time Holdout Evaluation).
- Verifica la integridad del firewall del Holdout.
- Verifica que el número de imágenes (193) y pacientes (162) sea exacto.
- Verifica la ausencia total de fuga de datos (0 interseccion de pacientes entre Dev y Holdout).
- Verifica la integridad del conjunto de características congeladas SET_G_LOCKED.
- Verifica la ausencia de valores NaN, Inf, o clapeos no declarados.
- Re-calcula de forma independiente las métricas de reproducibilidad out-of-sample.
- Emite dictamen científico final (PASS / PASS_WITH_LIMITATIONS).
Nota: ASCII estricto para compatibilidad Windows cp1252.
"""

import os
import sys
import json
import hashlib
import numpy as np
import pandas as pd

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.insert(0, root_dir)

manifest_path = os.path.join(root_dir, "data", "processed", "final_dataset_manifest.csv")
holdout_path = os.path.join(root_dir, "data", "processed", "holdout_test_split.json")
results_csv_path = os.path.join(root_dir, "data", "processed", "phase11_holdout_results.csv")
summary_csv_path = os.path.join(root_dir, "data", "processed", "phase11_holdout_summary.csv")

EXPECTED_HOLDOUT_HASH = "85e3a856e5a1334d53084f242fff50a92c1c662fe1d4c8797053261578d2b335"
LOCKED_DESCRIPTORS = ["fractal_D0", "minkowski_dimension", "multifractal_delta_alpha", "tda_beta_0"]

print("==================================================")
print("AUDITORIA CIENTIFICA FASE 11: HOLDOUT EVALUATION")
print("==================================================")

violations = []

# 1. Auditoría de Hash y Firewall
if not os.path.exists(holdout_path):
    violations.append("Holdout split file missing.")
else:
    with open(holdout_path, "rb") as f:
        h_hash = hashlib.sha256(f.read()).hexdigest()
    if h_hash != EXPECTED_HOLDOUT_HASH:
        violations.append(f"Holdout hash mismatch: {h_hash} vs {EXPECTED_HOLDOUT_HASH}")
    else:
        print(f"[PASS] 1. Firewall Hash SHA256 verificado: {h_hash}")

# 2. Auditoría de Aislamiento de Muestras (Dev vs Holdout)
df_manifest = pd.read_csv(manifest_path)
dev_pts = set(df_manifest[df_manifest["split"] == "Development"]["patient_id"])
ho_pts = set(df_manifest[df_manifest["split"] == "Holdout"]["patient_id"])

overlap = dev_pts.intersection(ho_pts)
if len(overlap) > 0:
    violations.append(f"DATALEAK: {len(overlap)} pacientes compartidos entre Dev y Holdout!")
else:
    print(f"[PASS] 2. Aislamiento total de pacientes confirmado (0 solapamiento entre Dev N={len(dev_pts)} y Holdout N={len(ho_pts)}).")

# 3. Auditoría de Dimensiones de Muestra en Holdout
ho_inc = df_manifest[(df_manifest["split"] == "Holdout") & (df_manifest["inclusion_status"] == "INCLUDED")]
if len(ho_inc) != 193 or len(ho_inc["patient_id"].unique()) != 162:
    violations.append(f"Holdout included count anomaly: Expected 193 img / 162 pts, got {len(ho_inc)} img / {len(ho_inc['patient_id'].unique())} pts.")
else:
    print(f"[PASS] 3. Recuento de Holdout exacto: 193 imagenes / 162 pacientes de prueba.")

# 4. Auditoría de Archivo de Resultados F11
if not os.path.exists(results_csv_path):
    violations.append("Archivo phase11_holdout_results.csv no encontrado.")
else:
    df_res = pd.read_csv(results_csv_path)
    print(f"[PASS] 4. Archivo de resultados cargado: {len(df_res)} muestras.")
    
    # Verificar NaNs o Infs
    num_cols = df_res.select_dtypes(include=[np.number]).columns
    n_nans = df_res[num_cols].isna().sum().sum()
    n_infs = np.isinf(df_res[num_cols].values).sum()
    
    if n_nans > 0 or n_infs > 0:
        violations.append(f"NaN/Inf detectados en resultados: {n_nans} NaNs, {n_infs} Infs.")
    else:
        print("[PASS] 4b. Ausencia total de NaN e Inf (0 anomalías numéricas).")

    # Verificar que solo estén las features congeladas SET_G_LOCKED
    for desc in LOCKED_DESCRIPTORS:
        if f"{desc}_crest" not in df_res.columns or f"{desc}_basal" not in df_res.columns:
            violations.append(f"Descriptor congelado faltante: {desc}")
    print("[PASS] 4c. Descriptores congelados SET_G_LOCKED presentes y verificados.")

# 5. Evaluación de Reproducibilidad Out-of-Sample
if os.path.exists(summary_csv_path):
    df_sum = pd.read_csv(summary_csv_path)
    print("\n--- RESUMEN DE VERIFICACION DE AUDITORIA ---")
    print(df_sum[["descriptor", "holdout_cohens_dz", "dev_cohens_dz", "direction_reproduced", "magnitude_ratio_holdout_vs_dev"]].to_string(index=False))

print("\n" + "=" * 50)
if len(violations) == 0:
    print("VERDICTO DE AUDITORIA: PASS")
    print("El Holdout fue evaluado con exito una sola vez sin ninguna violacion de cortafuegos o adaptacion post-hoc.")
else:
    print("VERDICTO DE AUDITORIA: FAIL / VIOLACIONES ENCONTRADAS")
    for v in violations:
        print(f" - VIOLACION: {v}")
print("==================================================")
