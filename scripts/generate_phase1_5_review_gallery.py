"""
Script de Re-clasificación y Generación de Galería Visual de Auditoría (Fase 1.5).
Genera comparaciones visuales lado a lado en data/processed/phase1_5_review_gallery/
sin modificar ningún archivo de dataset, mapping o split.
Nota: ASCII estricto para compatibilidad Windows cp1252.
"""

import os
import sys
import json
import cv2
import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, ".."))
processed_dir = os.path.join(root_dir, "data", "processed")
gallery_dir = os.path.join(processed_dir, "phase1_5_review_gallery")

os.makedirs(gallery_dir, exist_ok=True)

cand_csv_path = os.path.join(processed_dir, "perceptual_duplicate_candidates.csv")
mapping_path = os.path.join(processed_dir, "patient_mapping.csv")

if not os.path.exists(cand_csv_path):
    print(f"ERROR: No se encuentra {cand_csv_path}")
    sys.exit(1)

df_cand = pd.read_csv(cand_csv_path)
df_map = pd.read_csv(mapping_path)

print("==================================================")
print("RE-CLASIFICACION Y GENERACION DE GALERIA VISUAL (FASE 1.5)")
print("==================================================")

# 1. RE-CLASIFICACION DETALLADA DE LOS 176 "A. DUPLICADO EVIDENTE"
df_evident = df_cand[df_cand["classification"] == "A. DUPLICADO EVIDENTE"].copy()

same_patient_same_img = []
same_patient_diff_img = []
diff_patient_same_img = []
diff_patient_diff_img = []
dev_holdout_evident = []

for idx, row in df_evident.iterrows():
    p_a = str(row["patient_a"])
    p_b = str(row["patient_b"])
    s_a = str(row["split_a"])
    s_b = str(row["split_b"])
    c_sim = float(row["cosine_similarity"])
    dh = int(row["dhash_distance"])
    ph = int(row["phash_distance"])
    
    if s_a != s_b:
        dev_holdout_evident.append(row)
        
    if p_a == p_b:
        if c_sim >= 0.999 and dh == 0 and ph == 0:
            same_patient_same_img.append(row)
        else:
            same_patient_diff_img.append(row)
    else:
        if c_sim >= 0.995 and dh == 0 and ph == 0:
            diff_patient_same_img.append(row)
        else:
            diff_patient_diff_img.append(row)

print("\n--- 1. DESGLOSE DETALLADO DE CANDIDATOS A. DUPLICADO EVIDENTE (176) ---")
print(f" - Mismo paciente + Misma imagen (casi idéntica)   : {len(same_patient_same_img)}")
print(f" - Mismo paciente + Imágenes distintas             : {len(same_patient_diff_img)}")
print(f" - Pacientes distintos + Misma imagen (Conflicto)  : {len(diff_patient_same_img)}")
print(f" - Pacientes distintos + Imágenes distintas        : {len(diff_patient_diff_img)}")
print(f" - Development <-> Holdout en esta categoría        : {len(dev_holdout_evident)}")

# 2. GENERACION DE COMPOSICIONES VISUALES
def create_side_by_side_image(img_path_a, img_path_b, metadata, output_filename):
    img_a = cv2.imread(img_path_a)
    img_b = cv2.imread(img_path_b)
    
    if img_a is None or img_b is None:
        return
        
    # Resize a altura estandar de 400px
    target_h = 400
    h_a, w_a = img_a.shape[:2]
    h_b, w_b = img_b.shape[:2]
    
    w_a_new = int(w_a * (target_h / float(h_a)))
    w_b_new = int(w_b * (target_h / float(h_b)))
    
    res_a = cv2.resize(img_a, (w_a_new, target_h), interpolation=cv2.INTER_AREA)
    res_b = cv2.resize(img_b, (w_b_new, target_h), interpolation=cv2.INTER_AREA)
    
    # Crear lienzo combinado con header para metadatos
    canvas_w = w_a_new + w_b_new + 30
    header_h = 160
    canvas_h = target_h + header_h + 20
    
    canvas = np.full((canvas_h, canvas_w, 3), 255, dtype=np.uint8)
    
    # Pegar imagenes
    canvas[header_h:header_h + target_h, 10:10 + w_a_new] = res_a
    canvas[header_h:header_h + target_h, 20 + w_a_new:20 + w_a_new + w_b_new] = res_b
    
    # Dibujar metadatos con cv2.putText
    cv2.putText(canvas, f"PAIR: {metadata['priority']}", (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 180), 2)
    cv2.putText(canvas, f"STATUS: {metadata['tag']}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (180, 0, 0), 2)
    
    meta_a1 = f"A: {metadata['image_a'][:35]}..."
    meta_a2 = f"   Patient: {metadata['patient_a']} | Split: {metadata['split_a']}"
    cv2.putText(canvas, meta_a1, (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 0), 1)
    cv2.putText(canvas, meta_a2, (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (50, 50, 50), 1)
    
    meta_b1 = f"B: {metadata['image_b'][:35]}..."
    meta_b2 = f"   Patient: {metadata['patient_b']} | Split: {metadata['split_b']}"
    cv2.putText(canvas, meta_b1, (20 + w_a_new, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 0), 1)
    cv2.putText(canvas, meta_b2, (20 + w_a_new, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (50, 50, 50), 1)
    
    stats_str = f"Metrics: Cosine={metadata['cosine_similarity']:.4f} | dHash={metadata['dhash_distance']} | pHash={metadata['phash_distance']}"
    cv2.putText(canvas, stats_str, (10, 135), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 100, 0), 2)
    
    out_path = os.path.join(gallery_dir, output_filename)
    cv2.imwrite(out_path, canvas)

print("\nGenerando galeria visual en data/processed/phase1_5_review_gallery/...")

# 3. GENERAR CASO PRIORITARIO P3: khatibi-danah vs NOBODY
row_nobody = df_cand[(df_cand["image_a"].str.contains("khatibi")) & (df_cand["image_b"].str.contains("NOBODY"))]
if not row_nobody.empty:
    r = row_nobody.iloc[0]
    path_a = df_map[df_map["filename"] == r["image_a"]]["filepath"].values[0]
    path_b = df_map[df_map["filename"] == r["image_b"]]["filepath"].values[0]
    
    meta = {
        "priority": "P3 - PRIORITY DUPLICATE CASE",
        "tag": "CONFIRMED_DUPLICATE_REQUIRES_MANUAL_ACTION",
        "image_a": r["image_a"],
        "image_b": r["image_b"],
        "patient_a": r["patient_a"],
        "patient_b": r["patient_b"],
        "split_a": r["split_a"],
        "split_b": r["split_b"],
        "cosine_similarity": float(r["cosine_similarity"]),
        "dhash_distance": int(r["dhash_distance"]),
        "phash_distance": int(r["phash_distance"])
    }
    create_side_by_side_image(path_a, path_b, meta, "P3_khatibi_vs_NOBODY.png")
    print(" [OK] P3_khatibi_vs_NOBODY.png generado.")

# 4. GENERAR CASOS P1: DEV vs HOLDOUT (6 pares B. POSIBLE DUPLICADO)
dev_holdout_posible = df_cand[(df_cand["split_a"] != df_cand["split_b"]) & (df_cand["classification"] == "B. POSIBLE DUPLICADO")]
print(f"\nGenerando {len(dev_holdout_posible)} casos P1 Dev <-> Holdout...")

for idx, r in dev_holdout_posible.reset_index(drop=True).iterrows():
    path_a = df_map[df_map["filename"] == r["image_a"]]["filepath"].values[0]
    path_b = df_map[df_map["filename"] == r["image_b"]]["filepath"].values[0]
    
    meta = {
        "priority": "P1 - CRITICAL (Dev vs Holdout Candidate)",
        "tag": "REQUIRES_MANUAL_REVIEW",
        "image_a": r["image_a"],
        "image_b": r["image_b"],
        "patient_a": r["patient_a"],
        "patient_b": r["patient_b"],
        "split_a": r["split_a"],
        "split_b": r["split_b"],
        "cosine_similarity": float(r["cosine_similarity"]),
        "dhash_distance": int(r["dhash_distance"]),
        "phash_distance": int(r["phash_distance"])
    }
    create_side_by_side_image(path_a, path_b, meta, f"P1_Dev_vs_Holdout_Candidate_{idx+1}.png")

print(f" [OK] {len(dev_holdout_posible)} imagenes P1 generadas.")

# 5. GENERAR CASOS P2: CROSS-PATIENT EVIDENTES (Misma Imagen en Distintos Pacientes)
df_diff_patient_same_img = pd.DataFrame(diff_patient_same_img)
print(f"\nGenerando {len(df_diff_patient_same_img)} casos P2 Cross-Patient Evidentes...")

for idx, r in df_diff_patient_same_img.reset_index(drop=True).iterrows():
    path_a = df_map[df_map["filename"] == r["image_a"]]["filepath"].values[0]
    path_b = df_map[df_map["filename"] == r["image_b"]]["filepath"].values[0]
    
    meta = {
        "priority": "P2 - CROSS-PATIENT DUPLICATE CONFLICT",
        "tag": "CONFIRMED_DUPLICATE_REQUIRES_MANUAL_ACTION",
        "image_a": r["image_a"],
        "image_b": r["image_b"],
        "patient_a": r["patient_a"],
        "patient_b": r["patient_b"],
        "split_a": r["split_a"],
        "split_b": r["split_b"],
        "cosine_similarity": float(r["cosine_similarity"]),
        "dhash_distance": int(r["dhash_distance"]),
        "phash_distance": int(r["phash_distance"])
    }
    create_side_by_side_image(path_a, path_b, meta, f"P2_Cross_Patient_Conflict_{idx+1}.png")

print(f" [OK] {len(df_diff_patient_same_img)} imagenes P2 generadas.")

print("\n==================================================")
print("GALERIA VISUAL CREADA CON EXITO")
print("==================================================")
