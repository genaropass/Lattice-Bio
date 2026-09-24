"""
Script de Cierre Metodológico y Generación de Manifest Final (Fase 1 y 1.5).
- Verifica SHA256 del holdout_test_split.json antes y después.
- Excluye NOBODY_bmp por conflicto de identidad (EXCLUDED_IDENTITY_CONFLICT).
- Evalúa los 105 duplicados técinicos de mismo paciente (EXCLUDED_PERCEPTUAL_DUPLICATE).
- Genera data/processed/final_dataset_manifest.csv
- Genera data/processed/final_phase1_audit.json
- NO elimina archivos físicos.
- NO modifica holdout_test_split.json.
Nota: ASCII estricto para Windows.
"""

import os
import sys
import json
import hashlib
import pandas as pd
import numpy as np

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, ".."))
processed_dir = os.path.join(root_dir, "data", "processed")

mapping_path = os.path.join(processed_dir, "patient_mapping.csv")
split_path = os.path.join(processed_dir, "holdout_test_split.json")
cand_path = os.path.join(processed_dir, "perceptual_duplicate_candidates.csv")

print("==================================================")
print("FINALIZACION Y RESOLUCION DE MANIFEST (FASE 1 Y 1.5)")
print("==================================================")

# 1. SHA256 del holdout_test_split.json ANTES de operar
def calculate_sha256(filepath):
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as f:
        hasher.update(f.read())
    return hasher.hexdigest()

sha256_before = calculate_sha256(split_path)
print(f"SHA256 holdout_test_split.json (ANTES): {sha256_before}")

# Cargar datos
df_map = pd.read_csv(mapping_path)
df_cand = pd.read_csv(cand_path)
with open(split_path, 'r') as f:
    split_data = json.load(f)

dev_patients = set(split_data["dev_patient_ids"])
holdout_patients = set(split_data["holdout_patient_ids"])

# Asignar split inicial
df_map["split"] = df_map["patient_id"].apply(
    lambda pid: "Development" if pid in dev_patients else ("Holdout" if pid in holdout_patients else "Excluded")
)

df_map["inclusion_status"] = "INCLUDED"
df_map["exclusion_reason"] = "NONE"

# Marcar UNKNOWN_PATIENT
df_map.loc[df_map["patient_id"] == "UNKNOWN_PATIENT", "inclusion_status"] = "EXCLUDED_UNKNOWN_PATIENT"
df_map.loc[df_map["patient_id"] == "UNKNOWN_PATIENT", "exclusion_reason"] = "No patient_id metadata in filename"

# 2. RESOLVER DUPLICADO CONFIRMADO CROSS-PATIENT (NOBODY_bmp)
nobody_mask = df_map["filename"].str.contains("NOBODY_bmp", case=False, na=False)
df_map.loc[nobody_mask, "inclusion_status"] = "EXCLUDED_IDENTITY_CONFLICT"
df_map.loc[nobody_mask, "exclusion_reason"] = "Identity conflict duplicate of khatibi-danah"
df_map.loc[nobody_mask, "split"] = "Excluded"

print(f"Conflicto NOBODY_bmp marcado como EXCLUDED_IDENTITY_CONFLICT.")

# 3. EVALUAR DUPLICADOS TECNICOS SAME-PATIENT (105)
# Filtrar candidatos evidentes del mismo paciente
df_same_patient = df_cand[
    (df_cand["patient_a"] == df_cand["patient_b"]) & 
    (df_cand["cosine_similarity"] >= 0.995) & 
    (df_cand["dhash_distance"] <= 1)
]

excluded_perceptual_files = set()
for idx, row in df_same_patient.iterrows():
    # Conservar image_a, marcar image_b como duplicado técnico excluido
    file_b = row["image_b"]
    # Solo excluir si está en Development (nunca tocar Holdout)
    if row["split_b"] == "Development":
        excluded_perceptual_files.add(file_b)

for fname in excluded_perceptual_files:
    mask = df_map["filename"] == fname
    df_map.loc[mask, "inclusion_status"] = "EXCLUDED_PERCEPTUAL_DUPLICATE"
    df_map.loc[mask, "exclusion_reason"] = "Technical perceptual re-save duplicate of same patient"
    df_map.loc[mask, "split"] = "Excluded"

print(f"Duplicados perceptuales técnicos de Development marcados como EXCLUDED_PERCEPTUAL_DUPLICATE: {len(excluded_perceptual_files)}")

# Guardar Manifest Final
manifest_path = os.path.join(processed_dir, "final_dataset_manifest.csv")
df_map.to_csv(manifest_path, index=False)
print(f"[OK] MANIFEST FINAL GUARDADO EN: {manifest_path}")

# 4. SHA256 del holdout_test_split.json DESPUES de operar
sha256_after = calculate_sha256(split_path)
print(f"SHA256 holdout_test_split.json (DESPUES): {sha256_after}")
print(f"¿Holdout completamente intacto byte-a-byte?: {sha256_before == sha256_after}")

# 5. CONTEOS FINALMENTE INCLUIDOS Y EXCLUIDOS
dev_included = df_map[(df_map["split"] == "Development") & (df_map["inclusion_status"] == "INCLUDED")]
holdout_included = df_map[(df_map["split"] == "Holdout") & (df_map["inclusion_status"] == "INCLUDED")]

excl_md5 = 197 # eliminados antes
excl_perceptual = len(df_map[df_map["inclusion_status"] == "EXCLUDED_PERCEPTUAL_DUPLICATE"])
excl_identity = len(df_map[df_map["inclusion_status"] == "EXCLUDED_IDENTITY_CONFLICT"])
excl_unknown = len(df_map[df_map["inclusion_status"] == "EXCLUDED_UNKNOWN_PATIENT"])

audit_summary = {
    "total_raw_images": 2795,
    "excluded_exact_md5": excl_md5,
    "manifest_total_images": len(df_map),
    "development_included_images": len(dev_included),
    "development_included_patients": int(len(dev_included["patient_id"].unique())),
    "holdout_included_images": len(holdout_included),
    "holdout_included_patients": int(len(holdout_included["patient_id"].unique())),
    "excluded_perceptual_duplicates": excl_perceptual,
    "excluded_identity_conflicts": excl_identity,
    "excluded_unknown_patients": excl_unknown,
    "holdout_sha256_before": sha256_before,
    "holdout_sha256_after": sha256_after,
    "holdout_intact": sha256_before == sha256_after,
    "patient_overlap_dev_holdout": int(len(set(dev_included["patient_id"]).intersection(set(holdout_included["patient_id"])))),
    "image_overlap_dev_holdout": int(len(set(dev_included["filepath"]).intersection(set(holdout_included["filepath"]))))
}

audit_json_path = os.path.join(processed_dir, "final_phase1_audit.json")
with open(audit_json_path, 'w') as f:
    json.dump(audit_summary, f, indent=2)

print(f"[OK] RESUMEN FINAL AUDITADO GUARDADO EN: {audit_json_path}")

print("\n--- RESUMEN FINAL AUDITADO DE DATASET DE BENCHMARK ---")
print(f"Development Incluido : {len(dev_included)} imagenes ({len(dev_included['patient_id'].unique())} pacientes)")
print(f"Holdout Incluido     : {len(holdout_included)} imagenes ({len(holdout_included['patient_id'].unique())} pacientes)")
print(f"Excluidas Total      : {excl_md5 + excl_perceptual + excl_identity + excl_unknown} imagenes")
print("==================================================")
