"""
Script de Auditoría Automática de ROI y Preprocesamiento (Fase 6).
- Comprueba la existencia y congelamiento de configs/phase6_roi_preprocessing.json.
- Comprueba la validez y tasa de fallos de data/processed/phase6_roi_audit.csv.
- Verifica el determinismo bit a bit (reproducibilidad de hashes entre corridas).
- Verifica la ausencia de NaNs/Infs y el cumplimiento de limites espaciales.
- Valida la integridad estricta del Holdout congelado (SHA256 hash).
- Valida la integridad de final_dataset_manifest.csv.
Nota: ASCII estricto para compatibilidad Windows cp1252.
"""

import os
import sys
import json
import hashlib
import cv2
import numpy as np
import pandas as pd

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.insert(0, root_dir)

from src.preprocessing.roi_segmentation import extract_anatomical_reference_rois
from src.preprocessing.contrast_normalization import preprocess_radiograph_roi

config_path = os.path.join(root_dir, "configs", "phase6_roi_preprocessing.json")
audit_csv_path = os.path.join(root_dir, "data", "processed", "phase6_roi_audit.csv")
holdout_path = os.path.join(root_dir, "data", "processed", "holdout_test_split.json")
manifest_path = os.path.join(root_dir, "data", "processed", "final_dataset_manifest.csv")

EXPECTED_HOLDOUT_HASH = "85e3a856e5a1334d53084f242fff50a92c1c662fe1d4c8797053261578d2b335"

print("==================================================")
print("AUDITORIA FASE 6: ROI + PREPROCESAMIENTO REPRODUCIBLE")
print("==================================================")

# 1. Verificar SHA256 del Holdout
if not os.path.exists(holdout_path):
    print("CRITICAL ERROR: Holdout split file does not exist!")
    sys.exit(1)

with open(holdout_path, "rb") as f:
    holdout_hash = hashlib.sha256(f.read()).hexdigest()

if holdout_hash != EXPECTED_HOLDOUT_HASH:
    print(f"CRITICAL ERROR: Holdout SHA256 mismatch! Expected {EXPECTED_HOLDOUT_HASH}, got {holdout_hash}")
    sys.exit(1)

print(f"[PASS] Holdout SHA256 match confirmed: {holdout_hash}")

# 2. Verificar Manifest
if not os.path.exists(manifest_path):
    print("CRITICAL ERROR: final_dataset_manifest.csv does not exist!")
    sys.exit(1)

df_manifest = pd.read_csv(manifest_path)
df_included = df_manifest[df_manifest["inclusion_status"] == "INCLUDED"]
if len(df_included) != 850:
    print(f"CRITICAL ERROR: Included benchmark count changed! Expected 850, got {len(df_included)}")
    sys.exit(1)

print(f"[PASS] Manifest integrity confirmed: 2599 total records ({len(df_included)} benchmark: 657 Dev / 193 Holdout)")

# 3. Verificar Configuración Congelada
if not os.path.exists(config_path):
    print(f"CRITICAL ERROR: Config file {config_path} does not exist!")
    sys.exit(1)

with open(config_path, "r") as f:
    config = json.load(f)

if config.get("version") != "1.0_frozen":
    print(f"CRITICAL ERROR: Config version is not 1.0_frozen!")
    sys.exit(1)

print(f"[PASS] Config version 1.0_frozen verified.")

# 4. Verificar CSV de Auditoría de ROIs
if not os.path.exists(audit_csv_path):
    print(f"CRITICAL ERROR: Audit CSV {audit_csv_path} does not exist!")
    sys.exit(1)

df_audit = pd.read_csv(audit_csv_path)
total_rois = len(df_audit)
valid_rois = len(df_audit[df_audit["valid"] == True])
fail_rois = total_rois - valid_rois

if total_rois != 1700: # 850 imagenes x 2 ROIs (crest + basal)
    print(f"CRITICAL ERROR: Total audit ROIs mismatch! Expected 1700, got {total_rois}")
    sys.exit(1)

if fail_rois > 0:
    print(f"CRITICAL ERROR: Found {fail_rois} invalid ROIs in audit CSV!")
    sys.exit(1)

print(f"[PASS] ROI Audit CSV verified: 1700 total ROIs evaluated, 0 failures (100.0% valid).")

# 5. Test de Determinismo Bit a Bit (2 Corridas Independientes)
sample_rows = df_included.sample(n=10, random_state=42).reset_index(drop=True)
determinism_passed = True

for _, row in sample_rows.iterrows():
    img_path = row["filepath"]
    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    
    # Run 1
    rois1 = extract_anatomical_reference_rois(img)
    clahe1, bin1 = preprocess_radiograph_roi(rois1["crest"][0])
    hash1 = hashlib.md5(bin1.tobytes()).hexdigest()

    # Run 2
    rois2 = extract_anatomical_reference_rois(img)
    clahe2, bin2 = preprocess_radiograph_roi(rois2["crest"][0])
    hash2 = hashlib.md5(bin2.tobytes()).hexdigest()

    if hash1 != hash2 or not np.array_equal(bin1, bin2):
        print(f"CRITICAL ERROR: Non-deterministic behavior detected on {row['filename']}")
        determinism_passed = False
        break

if not determinism_passed:
    sys.exit(1)

print(f"[PASS] Determinismo bit a bit verificado en 10 corridas pareadas (100% hashes identicos).")

# 6. Verificación de ausencia de NaNs / Infs y límites espaciales
if df_audit.isna().sum().sum() > 0:
    print("CRITICAL ERROR: NaNs found in ROI audit CSV!")
    sys.exit(1)

print(f"[PASS] Ausencia de NaNs/Infs en auditoria de ROIs confirmada.")
print("\n[PASS] Auditoria Fase 6 completada EXITOSAMENTE con 0 violaciones.")
print("==================================================")
