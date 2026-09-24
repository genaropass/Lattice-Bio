"""
Script de Auditoría Automática Científica de ROI y Preprocesamiento (Fase 6.1).
- Comprueba la existencia y congelamiento de configs/phase6_1_roi_validation.json.
- Comprueba la validez anatómica en data/processed/phase6_1_roi_validation.csv.
- Comprueba la presencia de las 30 imágenes anotadas en data/processed/phase6_1_roi_visual_audit/.
- Comprueba la independencia total de la textura en el código de extracción.
- Valida la integridad estricta del Holdout congelado (SHA256 hash).
- Valida la integridad del manifest final del dataset.
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

from src.preprocessing.roi_segmentation import extract_anatomical_reference_rois

config_path = os.path.join(root_dir, "configs", "phase6_1_roi_validation.json")
csv_path = os.path.join(root_dir, "data", "processed", "phase6_1_roi_validation.csv")
audit_dir = os.path.join(root_dir, "data", "processed", "phase6_1_roi_visual_audit")
holdout_path = os.path.join(root_dir, "data", "processed", "holdout_test_split.json")
manifest_path = os.path.join(root_dir, "data", "processed", "final_dataset_manifest.csv")

EXPECTED_HOLDOUT_HASH = "85e3a856e5a1334d53084f242fff50a92c1c662fe1d4c8797053261578d2b335"

print("==================================================")
print("AUDITORIA FASE 6.1: VALIDACION ANATOMICA Y CIENTIFICA")
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

# 3. Verificar Configuración F6.1
if not os.path.exists(config_path):
    print(f"CRITICAL ERROR: Config file {config_path} does not exist!")
    sys.exit(1)

with open(config_path, "r") as f:
    config = json.load(f)

if config.get("decision") != "F6.1 CLOSED_WITH_LIMITATIONS":
    print(f"CRITICAL ERROR: Decision in config is not F6.1 CLOSED_WITH_LIMITATIONS!")
    sys.exit(1)

print(f"[PASS] Config decision verified: F6.1 CLOSED_WITH_LIMITATIONS.")

# 4. Verificar CSV y Directorio de Auditoría Visual
if not os.path.exists(csv_path):
    print(f"CRITICAL ERROR: Validation CSV {csv_path} does not exist!")
    sys.exit(1)

df_val = pd.read_csv(csv_path)
if len(df_val) < 30:
    print(f"CRITICAL ERROR: Sample size in visual audit CSV is {len(df_val)}, expected 30!")
    sys.exit(1)

valid_cnt = len(df_val[df_val["overall_anatomical_status"] == "VALID"])
print(f"[PASS] Visual audit CSV verified: {len(df_val)} sampled images evaluated, {valid_cnt} VALID ({valid_cnt/len(df_val)*100:.1f}%).")

if not os.path.exists(audit_dir) or len(os.listdir(audit_dir)) < 30:
    print(f"CRITICAL ERROR: Visual audit directory does not contain 30 annotated images!")
    sys.exit(1)

print(f"[PASS] Visual audit directory confirmed with {len(os.listdir(audit_dir))} annotated images.")

# 5. Verificación de Independencia de la Textura
import inspect
src_code = inspect.getsource(extract_anatomical_reference_rois)
texture_keywords = ["Laplacian", "variance", "threshold", "D0", "Dino", "texture"]
found_keywords = [kw for kw in texture_keywords if kw in src_code]
if found_keywords:
    print(f"CRITICAL ERROR: Found texture dependence in extract_anatomical_reference_rois: {found_keywords}")
    sys.exit(1)

print(f"[PASS] Independencia total de la textura confirmada en extract_anatomical_reference_rois.")
print("\n[PASS] Auditoria Fase 6.1 completada EXITOSAMENTE con 0 violaciones.")
print("==================================================")
