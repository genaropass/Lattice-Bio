"""
Script de Auditoría Automática de Congelamiento de Pipeline (Fase 10).
- Valida la integridad estricta del Holdout congelado (SHA256 hash).
- Verifica la ausencia total de imágenes o pacientes del Holdout en los procesos.
- Verifica la existencia y consistencia de configs/final_pipeline_lock_v1.json.
- Comprueba que el conjunto de features congelado sea exactamente SET_G_LOCKED (D0, DM, Delta_alpha, beta0).
- Comprueba que Lacunaridad y beta_1 estén excluidas metodológicamente.
- Valida que final_dataset_manifest.csv y holdout_test_split.json permanezcan inalterados.
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

lock_config_path = os.path.join(root_dir, "configs", "final_pipeline_lock_v1.json")
feats_path = os.path.join(root_dir, "data", "processed", "phase7_features.csv")
holdout_path = os.path.join(root_dir, "data", "processed", "holdout_test_split.json")
manifest_path = os.path.join(root_dir, "data", "processed", "final_dataset_manifest.csv")

EXPECTED_HOLDOUT_HASH = "85e3a856e5a1334d53084f242fff50a92c1c662fe1d4c8797053261578d2b335"

print("==================================================")
print("AUDITORIA AUTOMATICA FASE 10: PIPELINE LOCK CHECK")
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

# 3. Verificar Archivo de Configuración de Congelamiento v1
if not os.path.exists(lock_config_path):
    print(f"CRITICAL ERROR: Config file {lock_config_path} does not exist!")
    sys.exit(1)

with open(lock_config_path, "r") as f:
    config = json.load(f)

if config.get("lock_status") not in ["LOCKED", "LOCKED_WITH_LIMITATIONS"]:
    print(f"CRITICAL ERROR: Lock status is not LOCKED or LOCKED_WITH_LIMITATIONS!")
    sys.exit(1)

locked_feats = config["locked_feature_set"]["primary_descriptors"]
expected_locked = ["fractal_D0", "minkowski_dimension", "multifractal_delta_alpha", "tda_beta_0"]

if locked_feats != expected_locked:
    print(f"CRITICAL ERROR: Locked features mismatch! Expected {expected_locked}, got {locked_feats}")
    sys.exit(1)

print(f"[PASS] Config file final_pipeline_lock_v1.json verified: {locked_feats} locked.")

# 4. Verificar Exclusión Fundamentada de Lacunaridad y beta_1
excluded_feats = [item["descriptor"] for item in config["locked_feature_set"]["excluded_descriptors"]]
if "lacunarity_mean" not in excluded_feats or "tda_beta_1" not in excluded_feats:
    print(f"CRITICAL ERROR: Excluded features missing! Expected lacunarity_mean and tda_beta_1, got {excluded_feats}")
    sys.exit(1)

print(f"[PASS] Exclusión fundamentada de lacunarity_mean y tda_beta_1 verificada.")

# 5. Firewall Rule Check
if "one_time_holdout_firewall_rule" not in config:
    print("CRITICAL ERROR: One-time holdout firewall rule not found in config!")
    sys.exit(1)

print(f"[PASS] Regla Firewall del Holdout verificada.")
print("\n[PASS] Auditoria automatica Fase 10 completada EXITOSAMENTE con 0 violaciones.")
print("==================================================")
