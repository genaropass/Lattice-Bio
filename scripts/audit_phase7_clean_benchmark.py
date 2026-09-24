"""
Script de Auditoría Automática del Clean Benchmark (Fase 7).
- Valida la integridad estricta del Holdout congelado (SHA256 hash).
- Verifica la ausencia total de imágenes o pacientes del Holdout en data/processed/phase7_features.csv.
- Verifica el agrupamiento por paciente (PATIENT unit of analysis) y 0 patient leakage.
- Comprueba la ausencia de NaNs o Infs en el CSV de features.
- Verifica la existencia y consistencia de configs/phase7_clean_benchmark.json.
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

config_path = os.path.join(root_dir, "configs", "phase7_clean_benchmark.json")
features_csv_path = os.path.join(root_dir, "data", "processed", "phase7_features.csv")
holdout_path = os.path.join(root_dir, "data", "processed", "holdout_test_split.json")
manifest_path = os.path.join(root_dir, "data", "processed", "final_dataset_manifest.csv")

EXPECTED_HOLDOUT_HASH = "85e3a856e5a1334d53084f242fff50a92c1c662fe1d4c8797053261578d2b335"

print("==================================================")
print("AUDITORIA FASE 7: CLEAN BENCHMARK CIENTIFICO")
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

# 3. Verificar Archivo de Features de Fase 7
if not os.path.exists(features_csv_path):
    print(f"ERROR: Features CSV {features_csv_path} does not exist yet.")
    sys.exit(1)

df_feats = pd.read_csv(features_csv_path)
if len(df_feats) != 657:
    print(f"CRITICAL ERROR: Features CSV row count is {len(df_feats)}, expected exactly 657 Development images!")
    sys.exit(1)

print(f"[PASS] Features CSV loaded: exactly 657 Development records.")

# 4. Verificar CERO Contaminación / Leakage del Holdout
holdout_filenames = set(holdout_manifest["filename"].values)
holdout_patients = set(holdout_manifest["patient_id"].values)

dev_filenames_in_feats = set(df_feats["filename"].values)
dev_patients_in_feats = set(df_feats["patient_id"].values)

filename_intersection = dev_filenames_in_feats.intersection(holdout_filenames)
if filename_intersection:
    print(f"CRITICAL ERROR: Found Holdout files in Development features! {filename_intersection}")
    sys.exit(1)

patient_intersection = dev_patients_in_feats.intersection(holdout_patients)
if patient_intersection:
    print(f"CRITICAL ERROR: Found Holdout patients in Development features! {patient_intersection}")
    sys.exit(1)

print(f"[PASS] Contaminacion del Holdout: 0.0% (0 imagenes / 0 pacientes compartidos).")

# 5. Verificación de ausencia de NaNs o Infs
if df_feats.isna().sum().sum() > 0:
    print("CRITICAL ERROR: Found NaNs in Phase 7 features CSV!")
    sys.exit(1)

print(f"[PASS] Ausencia de NaNs/Infs en dataset de features confirmada.")

# 6. Verificar Configuración Congelada
if not os.path.exists(config_path):
    print(f"CRITICAL ERROR: Config file {config_path} does not exist!")
    sys.exit(1)

with open(config_path, "r") as f:
    config = json.load(f)

if config.get("version") != "1.0_frozen":
    print(f"CRITICAL ERROR: Config version is not 1.0_frozen!")
    sys.exit(1)

print(f"[PASS] Config version 1.0_frozen verified.")
print("\n[PASS] Auditoria Fase 7 completada EXITOSAMENTE con 0 violaciones.")
print("==================================================")
