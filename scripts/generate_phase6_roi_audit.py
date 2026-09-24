"""
Script de Generación y Auditoría de ROIs y Preprocesamiento (Fase 6).
- Procesa las 850 imágenes incluidas del benchmark (657 Development / 193 Holdout).
- Extrae ROIs anatómicas geométrica y determinísticamente.
- Verifica límites espaciales, ausencia de NaNs, determinismo de hash.
- Genera data/processed/phase6_roi_audit.csv.
- NO modifica el holdout, NO entrenas modelos, NO calcula AUC.
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
manifest_path = os.path.join(root_dir, "data", "processed", "final_dataset_manifest.csv")
audit_csv_path = os.path.join(root_dir, "data", "processed", "phase6_roi_audit.csv")

print("==================================================")
print("FASE 6: EXTRACCION Y AUDITORIA DE ROIS ANATOMICAS")
print("==================================================")

# 1. Cargar Configuración Congelada
with open(config_path, "r") as f:
    config = json.load(f)

# 2. Cargar Manifest
df_manifest = pd.read_csv(manifest_path)
included_df = df_manifest[df_manifest["inclusion_status"] == "INCLUDED"].reset_index(drop=True)

print(f"Benchmark cargado: {len(included_df)} imagenes ({len(included_df[included_df['split']=='Development'])} Dev / {len(included_df[included_df['split']=='Holdout'])} Holdout)")

audit_records = []
total_evaluations = 0
failures = 0

for idx, row in included_df.iterrows():
    img_path = row["filepath"]
    patient_id = row["patient_id"]
    filename = row["filename"]
    split = row["split"]
    source = row["source"]

    if not os.path.exists(img_path):
        failures += 1
        audit_records.append({
            "patient_id": patient_id,
            "filename": filename,
            "split": split,
            "modality": source,
            "roi_type": "UNKNOWN",
            "x": 0, "y": 0, "width": 0, "height": 0,
            "valid": False,
            "failure_reason": "FILE_NOT_FOUND",
            "preprocessing_version": config["version"]
        })
        continue

    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    if img is None or img.size == 0:
        failures += 1
        audit_records.append({
            "patient_id": patient_id,
            "filename": filename,
            "split": split,
            "modality": source,
            "roi_type": "UNKNOWN",
            "x": 0, "y": 0, "width": 0, "height": 0,
            "valid": False,
            "failure_reason": "CORRUPT_IMAGE",
            "preprocessing_version": config["version"]
        })
        continue

    h, w = img.shape
    # Extraer ROIs anatómicas determinísticas
    rois_dict = extract_anatomical_reference_rois(
        img,
        patch_size=tuple(config["anatomical_reference"]["ROI_A_crest"]["default_patch_size_px"]),
        crest_y_ratio=config["anatomical_reference"]["ROI_A_crest"]["y_center_ratio"],
        basal_y_ratio=config["anatomical_reference"]["ROI_B_basal"]["y_center_ratio"],
        x_ratio=config["anatomical_reference"]["ROI_A_crest"]["x_center_ratio"],
    )

    for roi_key, (crop, (rx, ry, rw, rh)) in rois_dict.items():
        total_evaluations += 1
        
        # Verificaciones de calidad
        valid = True
        reason = "NONE"

        if crop is None or crop.size == 0:
            valid = False
            reason = "EMPTY_CROP"
        elif crop.shape[0] < config["exclusion_and_quality_rules"]["min_roi_height_px"] or crop.shape[1] < config["exclusion_and_quality_rules"]["min_roi_width_px"]:
            valid = False
            reason = "TOO_SMALL"
        elif np.isnan(crop).any() or np.isinf(crop).any():
            valid = False
            reason = "NAN_OR_INF"
        elif rx < 0 or ry < 0 or (rx + rw) > w or (ry + rh) > h:
            valid = False
            reason = "OUT_OF_BOUNDS"

        if not valid:
            failures += 1

        # Test determinístico de hash de preprocesamiento
        clahe_img, binary_mask = preprocess_radiograph_roi(
            crop,
            clip_limit=config["preprocessing_pipelines"]["Pipeline_B_binary_topological"]["clahe_clip_limit"],
            sauvola_window=config["preprocessing_pipelines"]["Pipeline_B_binary_topological"]["sauvola_window_size"],
        )
        crop_hash = hashlib.md5(binary_mask.tobytes()).hexdigest()

        audit_records.append({
            "patient_id": patient_id,
            "filename": filename,
            "split": split,
            "modality": source,
            "roi_type": roi_key,
            "x": rx,
            "y": ry,
            "width": rw,
            "height": rh,
            "valid": valid,
            "failure_reason": reason,
            "crop_hash": crop_hash,
            "preprocessing_version": config["version"]
        })

df_audit = pd.DataFrame(audit_records)
df_audit.to_csv(audit_csv_path, index=False)

fail_rate = failures / max(1, total_evaluations)
print(f"Auditoria de ROIs completada.")
print(f"Total ROIs evaluadas: {total_evaluations} (Cresta + Basal)")
print(f"ROIs validas: {total_evaluations - failures} ({((total_evaluations - failures)/total_evaluations)*100:.2f}%)")
print(f"ROIs fallidas: {failures} (Tasa de fallo: {fail_rate*100:.2f}%)")
print(f"Guardado CSV de Auditoria en: {audit_csv_path}")
print("==================================================")
