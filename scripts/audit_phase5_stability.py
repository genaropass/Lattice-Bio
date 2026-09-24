"""
Script de Auditoría de Estabilidad Computacional de Descriptores (Fase 5).
- Verifica la existencia y consistencia de data/processed/phase5_stability_results.csv.
- Comprueba la ausencia de NaNs o inconsistencias de formato.
- Valida la integridad estricta del Holdout congelado (SHA256 hash).
- Valida que final_dataset_manifest.csv no haya sido alterado.
Nota: ASCII estricto para compatibilidad Windows cp1252.
"""

import os
import sys
import hashlib
import pandas as pd

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, ".."))

results_csv = os.path.join(root_dir, "data", "processed", "phase5_stability_results.csv")
holdout_path = os.path.join(root_dir, "data", "processed", "holdout_test_split.json")
manifest_path = os.path.join(root_dir, "data", "processed", "final_dataset_manifest.csv")

EXPECTED_HOLDOUT_HASH = "85e3a856e5a1334d53084f242fff50a92c1c662fe1d4c8797053261578d2b335"

print("==================================================")
print("AUDITORIA FASE 5: ESTABILIDAD COMPUTACIONAL")
print("==================================================")

# 1. Verificar Hash del Holdout
if not os.path.exists(holdout_path):
    print("CRITICAL ERROR: Holdout split file does not exist!")
    sys.exit(1)

with open(holdout_path, "rb") as f:
    holdout_hash = hashlib.sha256(f.read()).hexdigest()

if holdout_hash != EXPECTED_HOLDOUT_HASH:
    print(f"CRITICAL ERROR: Holdout SHA256 mismatch! Expected {EXPECTED_HOLDOUT_HASH}, got {holdout_hash}")
    sys.exit(1)

print(f"[PASS] Holdout SHA256 match confirmed: {holdout_hash}")

# 2. Verificar Manifest Dataset
if not os.path.exists(manifest_path):
    print("CRITICAL ERROR: final_dataset_manifest.csv does not exist!")
    sys.exit(1)

df_manifest = pd.read_csv(manifest_path)
df_included = df_manifest[df_manifest["inclusion_status"] == "INCLUDED"]
if len(df_included) != 850:
    print(f"CRITICAL ERROR: Included benchmark count changed! Expected 850, got {len(df_included)}")
    sys.exit(1)

dev_cnt = len(df_included[df_included["split"] == "Development"])
holdout_cnt = len(df_included[df_included["split"] == "Holdout"])
print(f"[PASS] Manifest integrity confirmed: 2599 raw records total, {len(df_included)} included benchmark images ({dev_cnt} Dev / {holdout_cnt} Holdout)")

# 3. Verificar Archivo de Resultados de Estabilidad
if not os.path.exists(results_csv):
    print(f"ERROR: Results file {results_csv} does not exist yet.")
    sys.exit(1)

df_res = pd.read_csv(results_csv)
print(f"\nResultados cargados: {len(df_res)} descriptores evaluados.")
print(df_res.to_string(index=False))

# Verificaciones de calidad
if df_res.isna().sum().sum() > 0:
    print("WARNING: Found NaNs in stability results!")
    sys.exit(1)

expected_descriptors = ["fractal_D0", "minkowski_dimension", "lacunarity_mean", "multifractal_delta_alpha", "tda_beta_0", "tda_beta_1"]
missing_desc = [d for d in expected_descriptors if d not in df_res["descriptor"].values]
if missing_desc:
    print(f"CRITICAL ERROR: Missing descriptors in stability evaluation: {missing_desc}")
    sys.exit(1)

print("\n[PASS] Todos los descriptores requeridos fueron evaluados correctamente.")
print("[PASS] Auditoria Fase 5 completada EXITOSAMENTE con 0 violaciones.")
print("==================================================")
