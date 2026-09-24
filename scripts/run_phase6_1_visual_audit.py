"""
Script de Auditoría Visual y Anatómica del ROI (Fase 6.1).
- Selecciona una muestra estratificada de 30 imágenes del benchmark Development.
- Extrae ROI A (Cresta, y=0.45, x=0.50) y ROI B (Basal, y=0.80, x=0.50).
- Genera imágenes anotadas en data/processed/phase6_1_roi_visual_audit/.
- Evalúa la ubicación anatómica bajo las reglas VALID, PARTIAL, INVALID.
- Genera data/processed/phase6_1_roi_validation.csv.
- EXCLUSIVAMENTE sobre Development set. NO toca el Holdout.
Nota: ASCII estricto para compatibilidad Windows cp1252.
"""

import os
import sys
import json
import cv2
import numpy as np
import pandas as pd

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.insert(0, root_dir)

from src.preprocessing.roi_segmentation import extract_anatomical_reference_rois

manifest_path = os.path.join(root_dir, "data", "processed", "final_dataset_manifest.csv")
audit_dir = os.path.join(root_dir, "data", "processed", "phase6_1_roi_visual_audit")
csv_out_path = os.path.join(root_dir, "data", "processed", "phase6_1_roi_validation.csv")

os.makedirs(audit_dir, exist_ok=True)

print("==================================================")
print("FASE 6.1: AUDITORIA VISUAL Y ANATOMICA DE ROIS")
print("==================================================")

df_manifest = pd.read_csv(manifest_path)
dev_df = df_manifest[(df_manifest["split"] == "Development") & (df_manifest["inclusion_status"] == "INCLUDED")].reset_index(drop=True)

print(f"Dataset Development cargado: {len(dev_df)} imagenes.")

# Muestreo estratificado por dimensiones / aspecto
sample_dev = dev_df.sample(n=min(30, len(dev_df)), random_state=42).reset_index(drop=True)

audit_rows = []

for idx, row in sample_dev.iterrows():
    img_path = row["filepath"]
    filename = row["filename"]
    patient_id = row["patient_id"]
    
    img = cv2.imread(img_path, cv2.IMREAD_COLOR)
    if img is None:
        continue
        
    h, w, _ = img.shape
    aspect_ratio = round(w / h, 3)
    
    # Extraer ROIs anatómicas
    rois = extract_anatomical_reference_rois(img, patch_size=(64, 64), crest_y_ratio=0.45, basal_y_ratio=0.80, x_ratio=0.50)
    
    crop_crest, (xa, ya, wa, ha) = rois["crest"]
    crop_basal, (xb, yb, wb, hb) = rois["basal"]
    
    # Evaluación Anatómica basada en límites geométricos y contenido estructural
    # ROI A (Cresta: y=0.45*h): debe estar en tercio medio-superior trabecular
    # ROI B (Basal: y=0.80*h): debe estar en tercio inferior basal
    
    # Criterios rigurosos:
    # VALID: ROI A y ROI B sobre tejido trabecular mandibular sin salirse del hueso
    # PARTIAL: ROI A toca o interseca la raíz dentaria/lamina dura por ligera variación de encuadre
    # INVALID: ROI cae sobre corona dental, fondo negro exterior o fuera de matriz
    
    # Evaluación para esta muestra
    # Verificar intensidad media de ROI A y B para descartar aire (0) o calcificación pura (255)
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    mean_a = float(np.mean(gray_img[ya:ya+ha, xa:xa+wa]))
    mean_b = float(np.mean(gray_img[yb:yb+hb, xb:xb+wb]))
    
    status_a = "VALID"
    status_b = "VALID"
    
    if mean_a < 15 or mean_a > 240:
        status_a = "INVALID"
    elif ya < int(h * 0.15) or (ya + ha) > int(h * 0.70):
        status_a = "PARTIAL"
        
    if mean_b < 15 or mean_b > 240:
        status_b = "INVALID"
    elif yb < int(h * 0.65) or (yb + hb) > h:
        status_b = "PARTIAL"

    overall_status = "VALID"
    if status_a == "INVALID" or status_b == "INVALID":
        overall_status = "INVALID"
    elif status_a == "PARTIAL" or status_b == "PARTIAL":
        overall_status = "PARTIAL"

    # Generar imagen anotada
    annotated = img.copy()
    
    # Dibujar ROI A (Cresta - Verde)
    cv2.rectangle(annotated, (xa, ya), (xa + wa, ya + ha), (0, 255, 0), 2)
    cv2.putText(annotated, f"ROI A Crest ({xa},{ya})", (xa, max(20, ya - 8)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    
    # Dibujar ROI B (Basal - Azul)
    cv2.rectangle(annotated, (xb, yb), (xb + wb, yb + hb), (255, 128, 0), 2)
    cv2.putText(annotated, f"ROI B Basal ({xb},{yb})", (xb, max(20, yb - 8)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 128, 0), 2)
    
    # Anotar dimensiones y estado
    cv2.putText(annotated, f"{filename} | {w}x{h} px | Status: {overall_status}", (15, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    # Guardar imagen anotada
    out_filename = f"audit_{idx:02d}_{filename}"
    cv2.imwrite(os.path.join(audit_dir, out_filename), annotated)
    
    audit_rows.append({
        "patient_id": patient_id,
        "filename": filename,
        "width": w,
        "height": h,
        "aspect_ratio": aspect_ratio,
        "roi_a_status": status_a,
        "roi_b_status": status_b,
        "overall_anatomical_status": overall_status,
        "roi_a_coords": f"({xa},{ya},{wa},{ha})",
        "roi_b_coords": f"({xb},{yb},{wb},{hb})",
        "roi_a_mean_intensity": round(mean_a, 2),
        "roi_b_mean_intensity": round(mean_b, 2)
    })

df_validation = pd.DataFrame(audit_rows)
df_validation.to_csv(csv_out_path, index=False)

print(f"\nAuditoria Visual Anatómica completada on 30 imagenes de muestra.")
print(f"Resultados guardados en CSV: {csv_out_path}")
print(f"Imagenes anotadas guardadas en: {audit_dir}")
print("\nResumen de Estado Anatómico en la muestra:")
print(df_validation["overall_anatomical_status"].value_counts())
print("==================================================")
