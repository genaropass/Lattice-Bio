"""
Script de Auditoría y Verificación Matemática de la Fase 4.
Prueba todos los descriptores fractales, multifractales y topológicos sobre:
1. Geometrías sintéticas con propiedades teóricas conocidas (Plano, Sierpinski, Línea, Ruido).
2. Evaluación multirango de q para el espectro multifractal ([-5,5], [-3,3], [-1,3], [0,5]).
3. Muestras de desarrollo reales de data/processed/patient_mapping.csv.
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

from src.fractal.box_counting import compute_box_counting_dimension, compute_lapidus_oscillation
from src.fractal.minkowski import compute_minkowski_blanket_dimension
from src.fractal.lacunarity import compute_lacunarity_spectrum
from src.fractal.multifractal import compute_multifractal_spectrum
from src.fractal.tda_features import compute_topological_features
from src.fractal.feature_extractor import FractalFeatureExtractor

print("==================================================")
print("FASE 4: AUDITORIA NUMERICA Y VERIFICACION MATEMATICA")
print("==================================================")

# 1. GENERACION DE GEOMETRIAS SINTETICAS CONOCIDAS

def generate_sierpinski_carpet(order=4):
    """Genera la alfombra de Sierpinski (D0 teorico = log(8)/log(3) = 1.8928)"""
    size = 3 ** order
    matrix = np.ones((size, size), dtype=np.uint8)
    
    def remove_center(x, y, s):
        if s < 1:
            return
        sub = s // 3
        matrix[x + sub : x + 2 * sub, y + sub : y + 2 * sub] = 0
        for i in range(3):
            for j in range(3):
                if i != 1 or j != 1:
                    remove_center(x + i * sub, y + j * sub, sub)
                    
    remove_center(0, 0, size)
    return matrix

# Sintético 1: Alfombra de Sierpinski 81x81 (D0 teórico ≈ 1.8928)
sierpinski = generate_sierpinski_carpet(order=4)

# Sintético 2: Plano uniforme lleno 64x64 (D0 teórico = 2.0, DM = 2.0)
plane = np.ones((64, 64), dtype=np.uint8)

# Sintético 3: Línea diagonal de 1px (D0 teórico = 1.0)
line = np.zeros((64, 64), dtype=np.uint8)
np.fill_diagonal(line, 1)

# Sintético 4: Ruido Blanco Gaussiano 64x64
np.random.seed(42)
white_noise = (np.random.rand(64, 64) > 0.5).astype(np.uint8)
gray_noise = (np.random.rand(64, 64) * 255).astype(np.uint8)

print("\n--- 1. VERIFICACION EN GEOMETRIAS SINTETICAS TEORICAS ---")

# Test 1: Box-Counting D0
bc_sierp = compute_box_counting_dimension(sierpinski)
bc_plane = compute_box_counting_dimension(plane)
bc_line = compute_box_counting_dimension(line)

print(f"Sierpinski D0 Teórico: 1.8928  | Obtenido D0: {bc_sierp['D0']:.4f} (R2={bc_sierp['r_squared']:.4f})")
print(f"Plano Lleno D0 Teórico: 2.0000  | Obtenido D0: {bc_plane['D0']:.4f} (R2={bc_plane['r_squared']:.4f})")
print(f"Línea 1D   D0 Teórico: 1.0000  | Obtenido D0: {bc_line['D0']:.4f} (R2={bc_line['r_squared']:.4f})")

# Test 2: Manta de Minkowski DM
mk_plane = compute_minkowski_blanket_dimension(plane * 255)
mk_noise = compute_minkowski_blanket_dimension(gray_noise)

print(f"Plano Minkowski DM Teórico: 2.0000 | Obtenido DM: {mk_plane['minkowski_dimension']:.4f} (R2={mk_plane['r_squared']:.4f})")
print(f"Ruido Minkowski DM (Rugoso)       | Obtenido DM: {mk_noise['minkowski_dimension']:.4f} (R2={mk_noise['r_squared']:.4f})")

# 2. EVALUACION MULTIRANGO DE MOMENTOS q PARA MULTIFRACTAL Delta_alpha

print("\n--- 2. EVALUACION MULTIRANGO DE MOMENTOS q PARA MULTIFRACTAL Delta_alpha ---")

q_ranges = {
    "q in [-5, 5]": np.linspace(-5.0, 5.0, 21),
    "q in [-3, 3]": np.linspace(-3.0, 3.0, 19),
    "q in [-1, 3]": np.linspace(-1.0, 3.0, 17),
    "q in [ 0, 5]": np.linspace(0.0, 5.0, 16),
}

q_results = []
for name, q_vec in q_ranges.items():
    res = compute_multifractal_spectrum(gray_noise, q_range=q_vec)
    q_results.append({
        "Rango q": name,
        "Delta_alpha Obtenido": round(res["delta_alpha"], 4),
        "tau(q) R2 Medio": round(res["tau_r2_mean"], 4),
        "D0": round(res["D0"], 4),
        "D1": round(res["D1"], 4),
        "D2": round(res["D2"], 4),
    })

df_q = pd.DataFrame(q_results)
print(df_q.to_string(index=False))

# 3. EVALUACION DE TDA DETERMINISTA
print("\n--- 3. VERIFICACION DE TDA DETERMINISTA ---")
tda_sierp = compute_topological_features(sierpinski)
tda_noise = compute_topological_features(white_noise)

print(f"Sierpinski TDA: beta0={tda_sierp['beta_0']}, beta1={tda_sierp['beta_1']}, H0_Entropy={tda_sierp['persistence_entropy_h0']:.4f}")
print(f"Ruido Blanco TDA: beta0={tda_noise['beta_0']}, beta1={tda_noise['beta_1']}, H0_Entropy={tda_noise['persistence_entropy_h0']:.4f}")

# 4. EVALUACION SOBRE MUESTRAS REALES DE DESARROLLO (80% DEV ONLY)
print("\n--- 4. EXTRACTION EN MUESTRAS REALES DE DESARROLLO (DEV ONLY) ---")

mapping_path = os.path.join(root_dir, "data", "processed", "final_dataset_manifest.csv")
split_path = os.path.join(root_dir, "data", "processed", "holdout_test_split.json")

df_map = pd.read_csv(mapping_path)
dev_included = df_map[(df_map["split"] == "Development") & (df_map["inclusion_status"] == "INCLUDED")]

print(f"Muestras de Development disponibles: {len(dev_included)}")

extractor = FractalFeatureExtractor(use_tda=True, use_minkowski=True)
sample_rows = dev_included.head(5)

extracted_samples = []
for idx, row in sample_rows.iterrows():
    img_path = row["filepath"]
    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    if img is not None:
        # Extraer parche de 64x64 central
        h, w = img.shape
        cy, cx = h // 2, w // 2
        patch = img[max(0, cy - 32):min(h, cy + 32), max(0, cx - 32):min(w, cx + 32)]
        patch_bin = (patch > np.median(patch)).astype(np.uint8)
        
        feats = extractor.extract_features(roi_mask=patch_bin, roi_grayscale=patch)
        extracted_samples.append({
            "patient_id": row["patient_id"],
            "D0": round(feats["fractal_D0"], 4),
            "D0_R2": round(feats["fractal_r2"], 4),
            "DM": round(feats["minkowski_dimension"], 4),
            "DM_R2": round(feats["minkowski_r2"], 4),
            "Lacunarity_Mean": round(feats["lacunarity_mean"], 4),
            "Multifractal_Delta_Alpha": round(feats["multifractal_delta_alpha"], 4),
            "beta_0": feats["tda_beta_0"],
            "beta_1": feats["tda_beta_1"]
        })

df_samples = pd.DataFrame(extracted_samples)
print("\nEjemplo de Muestras de Desarrollo Procesadas:")
print(df_samples.to_string(index=False))

print("\n==================================================")
print("AUDITORIA DE FASE 4 COMPLETADA")
print("==================================================")
