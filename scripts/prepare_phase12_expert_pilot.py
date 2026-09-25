"""
Script de Preparación del Expert Pilot (Fase 12).
- Muestra 50 imágenes del Development Included mediante muestreo aleatorio estratificado por fuente (seed=42).
- Genera paneles de evaluación cegados (Panel A: Imagen Original; Panel B: Superposición de ROI Cresta y Basal).
- Selecciona subconjunto de repetibilidad (20%, 10 imágenes, seed=1042).
- Anonimiza los identificadores (PILOT_IMG_001..050, REPEAT_IMG_001..010).
- Garantiza el cegamiento total (sin valores de features, sin etiquetas clínicas, sin origen de dataset).
- Guarda la manifestación del piloto en data/processed/phase12_pilot_manifest.csv.
Nota: ASCII estricto para compatibilidad Windows cp1252.
"""

import os
import sys
import json
import cv2
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.insert(0, root_dir)

from src.preprocessing.roi_segmentation import extract_anatomical_reference_rois

config_path = os.path.join(root_dir, "configs", "phase12_expert_pilot.json")
manifest_path = os.path.join(root_dir, "data", "processed", "final_dataset_manifest.csv")
panels_dir = os.path.join(root_dir, "data", "processed", "phase12_expert_panels")
pilot_manifest_path = os.path.join(root_dir, "data", "processed", "phase12_pilot_manifest.csv")

os.makedirs(panels_dir, exist_ok=True)

with open(config_path, "r") as f:
    config = json.load(f)

print("==================================================")
print("FASE 12: PREPARACION DEL EXPERT PILOT")
print("==================================================")

# 1. Cargar Manifest y filtrar Development Included
df_manifest = pd.read_csv(manifest_path)
dev_inc = df_manifest[(df_manifest["split"] == "Development") & (df_manifest["inclusion_status"] == "INCLUDED")].reset_index(drop=True)

print(f"Pool de Development Included cargado: {len(dev_inc)} imagenes ({len(dev_inc['patient_id'].unique())} pacientes)")

# 2. Muestreo estratificado por fuente (N = 50, seed = 42)
sample_size = config["sampling_protocol"]["sample_size"]
seed = config["sampling_protocol"]["random_seed"]

# Stratified sample by source
pilot_samples = []
sources = dev_inc["source"].unique()
np.random.seed(seed)

for src in sources:
    src_df = dev_inc[dev_inc["source"] == src]
    n_src = int(np.round(sample_size * (len(src_df) / len(dev_inc))))
    if n_src > 0:
        sample_indices = np.random.choice(src_df.index, size=min(n_src, len(src_df)), replace=False)
        pilot_samples.append(dev_inc.loc[sample_indices])

df_pilot = pd.concat(pilot_samples).reset_index(drop=True)

# Ajustar a exactamente 50 si hay diferencia de redondeo
if len(df_pilot) < sample_size:
    rem_df = dev_inc[~dev_inc["filename"].isin(df_pilot["filename"])]
    extra_indices = np.random.choice(rem_df.index, size=sample_size - len(df_pilot), replace=False)
    df_pilot = pd.concat([df_pilot, dev_inc.loc[extra_indices]]).reset_index(drop=True)
elif len(df_pilot) > sample_size:
    df_pilot = df_pilot.iloc[:sample_size].reset_index(drop=True)

# Randomizar orden
df_pilot = df_pilot.sample(frac=1.0, random_state=seed).reset_index(drop=True)

# Anonimizar IDs
df_pilot["pilot_image_id"] = [f"PILOT_IMG_{i+1:03d}" for i in range(len(df_pilot))]
print(f"[PASS] Muestreo aleatorio estratificado completado: {len(df_pilot)} imagenes seleccionadas.")

# 3. Generar Paneles de Evaluación Visual Cegados
for idx, row in df_pilot.iterrows():
    img_path = row["filepath"]
    pilot_id = row["pilot_image_id"]

    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        continue

    # Extraer ROIs geométricas congeladas (F6)
    rois = extract_anatomical_reference_rois(img, patch_size=(64, 64), crest_y_ratio=0.45, basal_y_ratio=0.80, x_ratio=0.50)
    crop_crest, bbox_crest = rois["crest"]
    crop_basal, bbox_basal = rois["basal"]

    # Crear panel de superposición
    img_color = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    
    # Dibujar ROI Cresta (Rojo)
    x1_c, y1_c, w_c, h_c = bbox_crest
    cv2.rectangle(img_color, (x1_c, y1_c), (x1_c + w_c, y1_c + h_c), (255, 0, 0), 2)
    cv2.putText(img_color, "ROI Cresta (A)", (x1_c, y1_c - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)

    # Dibujar ROI Basal (Verde)
    x1_b, y1_b, w_b, h_b = bbox_basal
    cv2.rectangle(img_color, (x1_b, y1_b), (x1_b + w_b, y1_b + h_b), (0, 255, 0), 2)
    cv2.putText(img_color, "ROI Basal (B)", (x1_b, y1_b - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)

    # Renderizar figura con Panel A (Original) y Panel B (Overlay)
    fig, axes = plt.subplots(1, 2, figsize=(10, 5))
    axes[0].imshow(img, cmap='gray')
    axes[0].set_title(f"{pilot_id} — Panel A: Radiografia Original")
    axes[0].axis('off')

    axes[1].imshow(img_color)
    axes[1].set_title(f"{pilot_id} — Panel B: ROIs Anatómicas Superpuestas")
    axes[1].axis('off')

    plt.tight_layout()
    panel_path = os.path.join(panels_dir, f"{pilot_id}_panel.png")
    plt.savefig(panel_path, dpi=120)
    plt.close()

print(f"[PASS] Generados {len(df_pilot)} paneles de evaluación cegados en: {panels_dir}")

# 4. Generar Subconjunto de Repetibilidad (20%, 10 imágenes, seed = 1042)
np.random.seed(config["repeatability_subset"]["repeat_seed"])
repeat_indices = np.random.choice(df_pilot.index, size=10, replace=False)
df_repeat = df_pilot.loc[repeat_indices].copy().reset_index(drop=True)
df_repeat["repeat_image_id"] = [f"REPEAT_IMG_{i+1:03d}" for i in range(len(df_repeat))]

# Unir manifest final del piloto
df_manifest_pilot = df_pilot[["pilot_image_id", "filename", "patient_id", "source", "filepath"]].copy()
repeat_map = dict(zip(df_repeat["pilot_image_id"], df_repeat["repeat_image_id"]))
df_manifest_pilot["repeat_image_id"] = df_manifest_pilot["pilot_image_id"].map(repeat_map).fillna("N/A")

df_manifest_pilot.to_csv(pilot_manifest_path, index=False)
print(f"[PASS] Manifestación del piloto guardada en: {pilot_manifest_path}")
print(f"Subconjunto de repetibilidad: {len(df_repeat)} imágenes configuradas.")
print("==================================================")
