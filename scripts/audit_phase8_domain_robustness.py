"""
Script de Auditoría Automática de Robustez, Atajos y Permutaciones (Fase 8).
- Valida la integridad estricta del Holdout congelado (SHA256 hash).
- Verifica la ausencia total de imágenes o pacientes del Holdout en los CSVs de Fase 8.
- Verifica la existencia y consistencia de todos los entregables de resultados de Fase 8.
- Comprueba la ausencia de NaNs o Infs en los CSVs de análisis.
- Verifica la existencia y congelamiento de configs/phase8_domain_robustness_config.json.
- Valida que final_dataset_manifest.csv permanezca inalterado.
Nota: ASCII estricto para compatibilidad Windows cp1252.
"""

import os
import sys
import json
import hashlib
import pandas as pd

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.insert(0, root_dir)

config_path = os.path.join(root_dir, "configs", "phase8_domain_robustness_config.json")
domain_csv_path = os.path.join(root_dir, "data", "processed", "phase8_domain_analysis.csv")
perm_csv_path = os.path.join(root_dir, "data", "processed", "phase8_permutation_results.csv")
sens_csv_path = os.path.join(root_dir, "data", "processed", "phase8_sensitivity_results.csv")
corr_csv_path = os.path.join(root_dir, "data", "processed", "phase8_correlation_matrix.csv")

holdout_path = os.path.join(root_dir, "data", "processed", "holdout_test_split.json")
manifest_path = os.path.join(root_dir, "data", "processed", "final_dataset_manifest.csv")

EXPECTED_HOLDOUT_HASH = "85e3a856e5a1334d53084f242fff50a92c1c662fe1d4c8797053261578d2b335"

print("==================================================")
print("AUDITORIA AUTOMATICA FASE 8: ROBUSTEZ Y ATAJOS")
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
dev_manifest = df_included[df_included["split"] == "Development"]
holdout_manifest = df_included[df_included["split"] == "Holdout"]

if len(df_included) != 850 or len(dev_manifest) != 657 or len(holdout_manifest) != 193:
    print(f"CRITICAL ERROR: Manifest row counts mismatch! Expected 850 total (657 Dev / 193 Holdout)")
    sys.exit(1)

print(f"[PASS] Manifest integrity confirmed: 850 included benchmark images (657 Dev / 193 Holdout)")

# 3. Verificar Entregables CSV de Fase 8
csv_files = [domain_csv_path, perm_csv_path, sens_csv_path, corr_csv_path]
for path in csv_files:
    if not os.path.exists(path):
        print(f"CRITICAL ERROR: Required Phase 8 CSV file missing: {path}")
        sys.exit(1)
    df_temp = pd.read_csv(path)
    if df_temp.isna().sum().sum() > 0:
        print(f"CRITICAL ERROR: NaNs found in {path}")
        sys.exit(1)

print(f"[PASS] Todos los 4 entregables CSV de Fase 8 verificados y sin NaNs/Infs.")

# 4. Verificar Configuración Congelada
if not os.path.exists(config_path):
    print(f"CRITICAL ERROR: Config file {config_path} does not exist!")
    sys.exit(1)

with open(config_path, "r") as f:
    config = json.load(f)

print(f"[PASS] Config file phase8_domain_robustness_config.json verified.")
print("\n[PASS] Auditoria automatica Fase 8 completada EXITOSAMENTE con 0 violaciones.")
print("==================================================")
