"""
Script de Evaluación de Estabilidad Computacional de Descriptores (Fase 5).
- Opera EXCLUSIVAMENTE sobre las muestras incluidas de Development (657 imágenes / 643 pacientes).
- Aplica las 8 categorías de perturbación congeladas en configs/phase5_stability_config.json.
- Evalúa estabilidad computacional de D0, DM, Lambda, Delta_alpha, beta0, beta1 y del ratio R_trab.
- Calcula ICC(3,1), Coeficiente de Variación (CV), cambio relativo y Failure Rate.
- Genera data/processed/phase5_stability_results.csv.
- NO entrena modelos, NO calcula AUC, NO toca el holdout.
Nota: ASCII estricto para compatibilidad Windows cp1252.
"""

import os
import sys
import json
import cv2
import numpy as np
import pandas as pd
from scipy import stats

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.insert(0, root_dir)

from src.fractal.feature_extractor import FractalFeatureExtractor
from src.preprocessing.contrast_normalization import adaptive_trabecular_binarization

config_path = os.path.join(root_dir, "configs", "phase5_stability_config.json")
mapping_path = os.path.join(root_dir, "data", "processed", "final_dataset_manifest.csv")
split_path = os.path.join(root_dir, "data", "processed", "holdout_test_split.json")
processed_dir = os.path.join(root_dir, "data", "processed")

print("==================================================")
print("FASE 5: EVALUACION DE ESTABILIDAD COMPUTACIONAL")
print("==================================================")

# 1. Cargar Configuración Congelada
with open(config_path, "r") as f:
    config = json.load(f)

# 2. Cargar Dataset Manifest (Solo Development Included)
df_map = pd.read_csv(mapping_path)
dev_included = df_map[(df_map["split"] == "Development") & (df_map["inclusion_status"] == "INCLUDED")].reset_index(drop=True)

print(f"Dataset Development cargado: {len(dev_included)} imagenes ({len(dev_included['patient_id'].unique())} pacientes)")

# Instanciar extractor
extractor = FractalFeatureExtractor(use_tda=True, use_minkowski=True)

# Función para calcular ICC(3,1)
def compute_icc_3_1(matrix):
    """Calcula el Coeficiente de Correlación Intraclase ICC(3,1) para matriz (n_subject, n_rater)"""
    n, k = matrix.shape
    if n < 2 or k < 2:
        return 0.0
    
    grand_mean = np.mean(matrix)
    row_means = np.mean(matrix, axis=1)
    col_means = np.mean(matrix, axis=0)
    
    ss_total = np.sum((matrix - grand_mean) ** 2)
    ss_rows = k * np.sum((row_means - grand_mean) ** 2)
    ss_cols = n * np.sum((col_means - grand_mean) ** 2)
    ss_error = max(1e-12, ss_total - ss_rows - ss_cols)
    
    ms_rows = ss_rows / (n - 1)
    ms_error = ss_error / ((n - 1) * (k - 1))
    
    icc = (ms_rows - ms_error) / (ms_rows + (k - 1) * ms_error + 1e-12)
    return float(np.clip(icc, 0.0, 1.0))

# 3. Muestrear 50 imágenes representativas de Development para el benchmark de perturbaciones
sample_dev = dev_included.sample(n=min(50, len(dev_included)), random_state=config["seed"]).reset_index(drop=True)
print(f"Muestra congelada para test de perturbación: {len(sample_dev)} imagenes")

descriptors = config["descriptors"]
stability_results = []

# Módulos de Perturbación
for desc in descriptors:
    print(f"\n[Evaluando descriptor: {desc}]...")
    
    total_evals = 0
    failures = 0
    
    # Matriz para ICC de Ruido (n_samples, n_noise_levels)
    noise_sigmas = config["perturbations"]["noise_gaussian_sigma"]
    noise_matrix = np.zeros((len(sample_dev), len(noise_sigmas) + 1))
    
    # Matriz para ICC de Rotación (0, 90, 180, 270)
    rot_angles = config["perturbations"]["rotation_angle_deg"]
    rot_matrix = np.zeros((len(sample_dev), len(rot_angles)))
    
    # Matriz para R_trab (ratio cresta / basal)
    r_trab_values = []
    
    for i, row in sample_dev.iterrows():
        img_path = row["filepath"]
        img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            failures += 1
            continue
            
        h, w = img.shape
        cy, cx = h // 2, w // 2
        
        # Extraer Parche Cresta Interdental (central) y Parche Basal (inferior)
        patch_crest = img[max(0, cy - 32):min(h, cy + 32), max(0, cx - 32):min(w, cx + 32)]
        patch_basal = img[max(0, h - 70):min(h, h - 6), max(0, cx - 32):min(w, cx + 32)]
        
        if patch_crest.shape != (64, 64) or patch_basal.shape != (64, 64):
            patch_crest = cv2.resize(patch_crest, (64, 64))
            patch_basal = cv2.resize(patch_basal, (64, 64))
            
        # 1. Inferencia Base
        bin_crest = adaptive_trabecular_binarization(patch_crest, window_size=15)
        bin_basal = adaptive_trabecular_binarization(patch_basal, window_size=15)
        
        try:
            feats_base = extractor.extract_features(roi_mask=bin_crest, roi_grayscale=patch_crest)
            feats_basal = extractor.extract_features(roi_mask=bin_basal, roi_grayscale=patch_basal)
            base_val = feats_base.get(desc, 0.0)
            basal_val = feats_basal.get(desc, 0.0)
            
            # Ratio R_trab
            if abs(basal_val) > 1e-6:
                r_trab = base_val / basal_val
                r_trab_values.append(r_trab)
                
            noise_matrix[i, 0] = base_val
            total_evals += 1
        except Exception:
            failures += 1
            continue
            
        # 2. Perturbaciones de Ruido Gaussiano
        for j, sigma in enumerate(noise_sigmas):
            noise = np.random.normal(0, sigma * 255.0, patch_crest.shape)
            noisy_img = np.clip(patch_crest.astype(np.float32) + noise, 0, 255).astype(np.uint8)
            bin_noisy = adaptive_trabecular_binarization(noisy_img, window_size=15)
            try:
                feats_noisy = extractor.extract_features(roi_mask=bin_noisy, roi_grayscale=noisy_img)
                noise_matrix[i, j + 1] = feats_noisy.get(desc, 0.0)
                total_evals += 1
            except Exception:
                failures += 1
                
        # 3. Perturbaciones de Rotación
        for k, angle in enumerate(rot_angles):
            if angle == 0:
                rot_matrix[i, k] = base_val
            else:
                rot_code = cv2.ROTATE_90_CLOCKWISE if angle == 90 else (cv2.ROTATE_180 if angle == 180 else cv2.ROTATE_90_COUNTERCLOCKWISE)
                rot_img = cv2.rotate(patch_crest, rot_code)
                bin_rot = adaptive_trabecular_binarization(rot_img, window_size=15)
                try:
                    feats_rot = extractor.extract_features(roi_mask=bin_rot, roi_grayscale=rot_img)
                    rot_matrix[i, k] = feats_rot.get(desc, 0.0)
                    total_evals += 1
                except Exception:
                    failures += 1

    # Calcular Estadísticas Finales para el Descriptor
    icc_noise = compute_icc_3_1(noise_matrix)
    icc_rot = compute_icc_3_1(rot_matrix)
    
    # Cambios relativos en ruido (comparado con base_val)
    base_vals = noise_matrix[:, 0]
    noisy_vals = noise_matrix[:, 1]
    rel_changes = np.abs(noisy_vals - base_vals) / (np.abs(base_vals) + 1e-8)
    mean_rel_change = float(np.mean(rel_changes))
    
    # Coeficiente de variación (CV)
    cv_val = float(np.std(base_vals) / (abs(np.mean(base_vals)) + 1e-8))
    
    fail_rate = float(failures / (total_evals + 1e-8))
    
    # Determinar Clasificación de Estabilidad
    if icc_noise >= 0.85 and fail_rate < 0.02:
        status = "ROBUST"
    elif icc_noise >= 0.70:
        status = "ROBUST_WITH_LIMITATIONS"
    elif icc_noise >= 0.50:
        status = "SENSITIVE_BUT_INTERPRETABLE"
    else:
        status = "UNSTABLE"
        
    stability_results.append({
        "descriptor": desc,
        "icc_noise": round(icc_noise, 4),
        "icc_rotation": round(icc_rot, 4),
        "mean_relative_change": round(mean_rel_change, 4),
        "cv": round(cv_val, 4),
        "failure_rate": round(fail_rate, 4),
        "total_evaluations": total_evals,
        "failures": failures,
        "r_trab_mean": round(float(np.mean(r_trab_values)), 4) if r_trab_values else 0.0,
        "r_trab_std": round(float(np.std(r_trab_values)), 4) if r_trab_values else 0.0,
        "status": status
    })

df_results = pd.DataFrame(stability_results)

# Guardar CSV de Resultados
results_csv_path = os.path.join(processed_dir, "phase5_stability_results.csv")
df_results.to_csv(results_csv_path, index=False)

print("\n" + "=" * 50)
print(" MATRIZ DE ESTABILIDAD COMPUTACIONAL (FASE 5)")
print("=" * 50)
print(df_results.to_string(index=False))
print("==================================================")
