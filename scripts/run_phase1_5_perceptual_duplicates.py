"""
Script de Auditoría de Fase 1.5 - Detección de Duplicados Perceptuales.
Metodología:
- dHash (Difference Hash 64-bit) y pHash (DCT 64-bit)
- Similitud de Coseno de Intensidad Estandarizada (64x64)
- Screening thresholds: Hamming Distance <= 4 o Cosine Similarity >= 0.98
- Genera data/processed/perceptual_duplicate_candidates.csv
- Genera data/processed/perceptual_duplicate_summary.json
- NO modifica dataset, ni patient_mapping.csv ni holdout_test_split.json
Nota: ASCII estricto para compatibilidad Windows cp1252.
"""

import os
import sys
import json
import cv2
import numpy as np
import pandas as pd
from PIL import Image
from scipy.fftpack import dct

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, ".."))
processed_dir = os.path.join(root_dir, "data", "processed")

mapping_path = os.path.join(processed_dir, "patient_mapping.csv")
split_path = os.path.join(processed_dir, "holdout_test_split.json")

print("==================================================")
print("FASE 1.5: DETECCION AUDITADA DE DUPLICADOS PERCEPTUALES")
print("==================================================")

df_map = pd.read_csv(mapping_path)
with open(split_path, "r") as f:
    split_data = json.load(f)

dev_patients = set(split_data["dev_patient_ids"])
holdout_patients = set(split_data["holdout_patient_ids"])

# Filtrar solo imágenes del benchmark principal (987 imágenes)
df_valid = df_map[df_map["patient_id"] != "UNKNOWN_PATIENT"].copy()
df_valid["split"] = df_valid["patient_id"].apply(
    lambda pid: "Development" if pid in dev_patients else ("Holdout" if pid in holdout_patients else "Excluded")
)

df_bm = df_valid[df_valid["split"].isin(["Development", "Holdout"])].reset_index(drop=True)

print(f"Total imágenes en el Benchmark Principal: {len(df_bm)}")
print(f"  - Development : {len(df_bm[df_bm['split'] == 'Development'])}")
print(f"  - Holdout     : {len(df_bm[df_bm['split'] == 'Holdout'])}")

# Funciones de Hashing Perceptual y Similitud

def compute_dhash(img_gray, hash_size=8):
    """Calcula dHash (Difference Hash 64-bit)"""
    resized = cv2.resize(img_gray, (hash_size + 1, hash_size), interpolation=cv2.INTER_AREA)
    diff = resized[:, 1:] > resized[:, :-1]
    return diff.flatten()

def compute_phash(img_gray, hash_size=8, highfreq_factor=4):
    """Calcula pHash (DCT-based Perceptual Hash 64-bit)"""
    img_size = hash_size * highfreq_factor
    resized = cv2.resize(img_gray, (img_size, img_size), interpolation=cv2.INTER_AREA).astype(np.float32)
    dct_mat = dct(dct(resized.T, norm='ortho').T, norm='ortho')
    dct_lowfreq = dct_mat[:hash_size, :hash_size]
    med = np.median(dct_lowfreq)
    diff = dct_lowfreq > med
    return diff.flatten()

def compute_normalized_vector(img_gray, size=64):
    """Vector de intensidad estandarizado 64x64 para similitud de coseno"""
    resized = cv2.resize(img_gray, (size, size), interpolation=cv2.INTER_AREA).astype(np.float32)
    norm = (resized - np.mean(resized)) / (np.std(resized) + 1e-8)
    return norm.flatten()

def hamming_distance(hash1, hash2):
    return np.sum(hash1 != hash2)

def cosine_similarity(v1, v2):
    return float(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-8))

print("\nCalculando hashes perceptuales y vectores de intensidad...")
records = []
for idx, row in df_bm.iterrows():
    img_path = row["filepath"]
    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        continue
    
    dh = compute_dhash(img)
    ph = compute_phash(img)
    vec = compute_normalized_vector(img)
    
    records.append({
        "filepath": img_path,
        "filename": row["filename"],
        "patient_id": row["patient_id"],
        "split": row["split"],
        "dhash": dh,
        "phash": ph,
        "vector": vec
    })

print(f"Vectores y hashes generados para {len(records)} imagenes.")

# Comparación Pareada (N * (N-1) / 2)
print("\nEjecutando comparacion pareada (Screening thresholds: dHash <= 4 o Cosine >= 0.95)...")
candidates = []
n = len(records)

for i in range(n):
    rec_a = records[i]
    for j in range(i + 1, n):
        rec_b = records[j]
        
        dh_dist = hamming_distance(rec_a["dhash"], rec_b["dhash"])
        ph_dist = hamming_distance(rec_a["phash"], rec_b["phash"])
        cos_sim = cosine_similarity(rec_a["vector"], rec_b["vector"])
        
        # Screening Thresholds
        if dh_dist <= 6 or ph_dist <= 6 or cos_sim >= 0.95:
            # Determinar prioridad y relacion de paciente/split
            patient_a = rec_a["patient_id"]
            patient_b = rec_b["patient_id"]
            split_a = rec_a["split"]
            split_b = rec_b["split"]
            
            same_patient = (patient_a == patient_b)
            cross_split = (split_a != split_b)
            
            # Clasificacion inicial
            if cos_sim >= 0.985 and (dh_dist <= 2 or ph_dist <= 2):
                classification = "A. DUPLICADO EVIDENTE"
            elif cos_sim >= 0.96 or (dh_dist <= 4 or ph_dist <= 4):
                classification = "B. POSIBLE DUPLICADO"
            else:
                classification = "C. FALSO POSITIVO PROBABLE"
                
            if cross_split:
                priority = "P1 - CRITICAL (Dev vs Holdout)"
                reason = "CRITICAL — POSSIBLE HOLDOUT CONTAMINATION"
            elif not same_patient:
                priority = "P2 - HIGH (Cross-Patient Duplicate)"
                reason = "CROSS-PATIENT DUPLICATE"
            else:
                priority = "P3 - MEDIUM (Same Patient Similarity)"
                reason = "SAME_PATIENT_SIMILARITY"
                
            candidates.append({
                "image_a": rec_a["filename"],
                "image_b": rec_b["filename"],
                "patient_a": patient_a,
                "patient_b": patient_b,
                "split_a": split_a,
                "split_b": split_b,
                "dhash_distance": int(dh_dist),
                "phash_distance": int(ph_dist),
                "cosine_similarity": round(cos_sim, 4),
                "classification": classification,
                "reason": reason,
                "priority": priority
            })

df_candidates = pd.DataFrame(candidates)

# Ordenar por prioridad
if not df_candidates.empty:
    df_candidates.sort_values(by=["priority", "cosine_similarity"], ascending=[True, False], inplace=True)

# Guardar CSV
cand_csv_path = os.path.join(processed_dir, "perceptual_duplicate_candidates.csv")
df_candidates.to_csv(cand_csv_path, index=False)
print(f"\n[OK] CANDIDATOS GUARDADOS EN: {cand_csv_path}")

# Resumen de Estadisticas
num_dev_holdout = len(df_candidates[df_candidates["split_a"] != df_candidates["split_b"]]) if not df_candidates.empty else 0
num_cross_patient = len(df_candidates[df_candidates["patient_a"] != df_candidates["patient_b"]]) if not df_candidates.empty else 0
num_same_patient = len(df_candidates[df_candidates["patient_a"] == df_candidates["patient_b"]]) if not df_candidates.empty else 0

num_evidente = len(df_candidates[df_candidates["classification"] == "A. DUPLICADO EVIDENTE"]) if not df_candidates.empty else 0
num_posible = len(df_candidates[df_candidates["classification"] == "B. POSIBLE DUPLICADO"]) if not df_candidates.empty else 0
num_falso_pos = len(df_candidates[df_candidates["classification"] == "C. FALSO POSITIVO PROBABLE"]) if not df_candidates.empty else 0

summary_data = {
    "total_images_analyzed": len(records),
    "total_candidate_pairs": len(candidates),
    "candidates_same_patient": num_same_patient,
    "candidates_cross_patient": num_cross_patient,
    "candidates_dev_holdout": num_dev_holdout,
    "classified_evident_duplicate": num_evidente,
    "classified_possible_duplicate": num_posible,
    "classified_probable_false_positive": num_falso_pos,
    "holdout_compromised": num_dev_holdout > 0,
    "cross_patient_candidates": num_cross_patient > 0
}

summary_json_path = os.path.join(processed_dir, "perceptual_duplicate_summary.json")
with open(summary_json_path, "w") as f:
    json.dump(summary_data, f, indent=2)

print(f"[OK] RESUMEN GUARDADO EN: {summary_json_path}")

print("\n--- RESUMEN AUDITADO DE FASE 1.5 ---")
print(f"Total imagenes analizadas (Benchmark): {len(records)}")
print(f"Total pares candidatos detectados  : {len(candidates)}")
print(f" - Candidatos Mismo Paciente        : {num_same_patient}")
print(f" - Candidatos Cross-Patient          : {num_cross_patient}")
print(f" - Candidatos Dev <-> Holdout       : {num_dev_holdout}")
print(f" - Clasificados Duplicado Evidente  : {num_evidente}")
print(f" - Clasificados Posible Duplicado   : {num_posible}")
print(f" - Clasificados Falso Pos Probable  : {num_falso_pos}")

print("==================================================")
