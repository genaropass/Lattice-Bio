"""
Script de Inicialización de Ledger y Split Estricto por Paciente (Fase 0 y Fase 1).
- Infiere patient_id de los archivos en data/raw/
- Detecta duplicados o imágenes sin ID confiable (se excluyen del benchmark principal)
- Genera data/processed/experiment_ledger.csv
- Genera data/processed/patient_mapping.csv
- Congela e aísla data/processed/holdout_test_split.json (20% Holdout, 80% Dev)
Nota: ASCII estricto para compatibilidad Windows cp1252.
"""

import os
import sys
import re
import glob
import json
import hashlib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, ".."))
data_dir = os.path.join(root_dir, "data")
processed_dir = os.path.join(data_dir, "processed")
raw_dir = os.path.join(data_dir, "raw")

os.makedirs(processed_dir, exist_ok=True)

print("==================================================")
print("FASE 0 Y FASE 1: PACIENTE GROUPING Y HOLDOUT FREEZE")
print("==================================================")

# 1. Inicializar Experiment Ledger si no existe
ledger_path = os.path.join(processed_dir, "experiment_ledger.csv")
if not os.path.exists(ledger_path):
    ledger_df = pd.DataFrame([
        {
            "exp_id": "EXP-001",
            "date": "2026-09-21",
            "dataset": "Full Images (2795)",
            "preprocessing": "CLAHE/Sauvola",
            "feature_set": "Math (16)",
            "model": "XGBoost",
            "split": "Random 5-Fold",
            "target": "source_dataset",
            "auc": 0.9937,
            "status": "INVALID",
            "reason": "Shortcut bias + Patient leakage"
        },
        {
            "exp_id": "EXP-002",
            "date": "2026-09-21",
            "dataset": "Full Images (2795)",
            "preprocessing": "DINOv2 140x140",
            "feature_set": "DINOv2 (384)",
            "model": "XGBoost",
            "split": "Random 5-Fold",
            "target": "source_dataset",
            "auc": 0.9980,
            "status": "INVALID",
            "reason": "Shortcut bias por resolucion/sensor"
        },
        {
            "exp_id": "EXP-003",
            "date": "2026-09-21",
            "dataset": "Full Images (2795)",
            "preprocessing": "Concatenado",
            "feature_set": "Hybrid (400)",
            "model": "XGBoost",
            "split": "Random OOF",
            "target": "source_dataset",
            "auc": 0.9996,
            "status": "INVALID",
            "reason": "DeLong en OOF conc. + Data leakage"
        },
        {
            "exp_id": "EXP-004",
            "date": "2026-09-22",
            "dataset": "Full Images (2795)",
            "preprocessing": "Full Image",
            "feature_set": "Hybrid (400)",
            "model": "XGBoost",
            "split": "100% Train",
            "target": "source_dataset",
            "auc": 0.9997,
            "status": "INVALID",
            "reason": "Evaluacion sobre datos de entrenamiento"
        },
        {
            "exp_id": "EXP-005",
            "date": "2026-09-22",
            "dataset": "ROIs 64x64 (400)",
            "preprocessing": "Parche Interdental",
            "feature_set": "Math (13)",
            "model": "XGBoost",
            "split": "Random 5-Fold",
            "target": "source_dataset",
            "auc": 0.7437,
            "status": "PROVISIONAL",
            "reason": "Muestra reduccion de sesgo, requiere GroupKFold"
        }
    ])
    ledger_df.to_csv(ledger_path, index=False)
    print(f"[OK] Ledger de experimentos guardado en: {ledger_path}")

# 2. Escanear imagenes y resolver patient_id
raw_images = glob.glob(os.path.join(raw_dir, "**", "*.jpg"), recursive=True) + \
             glob.glob(os.path.join(raw_dir, "**", "*.png"), recursive=True) + \
             glob.glob(os.path.join(raw_dir, "**", "*.jpeg"), recursive=True)

print(f"Total de imagenes encontradas en raw/: {len(raw_images)}")

patient_records = []
unidentified_count = 0

for img_path in raw_images:
    fname = os.path.basename(img_path)
    
    # Inferencia de patient_id mediante regex
    # Ejemplo: ahmed_fares_1899_12_30_..., Tawfik_Layan_2016_05_03...-3-
    clean_name = re.sub(r'(\.rf\.[a-f0-9]+|\.jpg|\.png|\.jpeg)', '', fname, flags=re.IGNORECASE)
    parts = clean_name.split('_')
    
    if len(parts) >= 2 and not parts[0].isdigit():
        patient_id = f"{parts[0]}_{parts[1]}".lower()
    else:
        # Si no se puede inferir paciente claro
        patient_id = "UNKNOWN_PATIENT"
        unidentified_count += 1
        
    source = "Periodontal" if "Periodontal" in img_path else "Panoramic"
    
    # MD5 Hash para deduplicacion idéntica
    with open(img_path, 'rb') as f:
        file_hash = hashlib.md5(f.read()).hexdigest()
        
    patient_records.append({
        "filepath": img_path,
        "filename": fname,
        "patient_id": patient_id,
        "source": source,
        "file_hash": file_hash
    })

df_map = pd.DataFrame(patient_records)

# Eliminar duplicados exactos por hash
df_map_unique = df_map.drop_duplicates(subset=["file_hash"]).copy()
print(f"Duplicados exactos eliminados: {len(df_map) - len(df_map_unique)}")

mapping_path = os.path.join(processed_dir, "patient_mapping.csv")
df_map_unique.to_csv(mapping_path, index=False)
print(f"[OK] Mapeo de pacientes guardado en: {mapping_path}")

# 3. Filtrar pacientes validos para el Benchmark Principal
df_valid = df_map_unique[df_map_unique["patient_id"] != "UNKNOWN_PATIENT"].copy()
unique_patients = np.array(list(df_valid["patient_id"].unique()))
print(f"Pacientes unicos identificados: {len(unique_patients)}")
print(f"Imagenes con paciente no identificable excluidas del split principal: {unidentified_count}")

# 4. Congelar Holdout Test Set (20% de pacientes unicos)
np.random.seed(42)
dev_patients, holdout_patients = train_test_split(unique_patients, test_size=0.20, random_state=42)

holdout_split = {
    "created_at": "2026-09-23",
    "seed": 42,
    "num_total_patients": int(len(unique_patients)),
    "num_dev_patients": int(len(dev_patients)),
    "num_holdout_patients": int(len(holdout_patients)),
    "dev_patient_ids": dev_patients.tolist(),
    "holdout_patient_ids": holdout_patients.tolist()
}

split_path = os.path.join(processed_dir, "holdout_test_split.json")
with open(split_path, 'w') as f:
    json.dump(holdout_split, f, indent=2)

print(f"\n[OK] HOLDOUT TEST SET CONGELADO Y GUARDADO EN: {split_path}")
print(f"  - Pacientes en Desarrollo (80%): {len(dev_patients)}")
print(f"  - Pacientes en Holdout (20% Retenido): {len(holdout_patients)}")
print("==================================================")
