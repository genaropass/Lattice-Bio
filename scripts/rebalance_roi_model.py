"""
Re-entrenamiento y Evaluacion Desequilibrada de Sesgo usando ROIs Trabeculares Puras.
Extrae parches trabeculares de 64x64 px de ambas fuentes y calcula métricas libres de artefactos.
Nota: ASCII estricto en los print statements para Windows.
"""

import os
import sys
import glob
import cv2
import numpy as np
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score, accuracy_score, precision_score, recall_score
from xgboost import XGBClassifier

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from src.preprocessing.roi_segmentation import extract_interdental_rois
from src.preprocessing.contrast_normalization import apply_clahe, adaptive_trabecular_binarization
from src.fractal.feature_extractor import FractalFeatureExtractor

print("==================================================")
print("EXTRACCION Y ENTRENAMIENTO EN ROIS TRABECULARES PURAS")
print("==================================================")

# Buscar imagenes en raw/
ctrl_dir = os.path.join(root_dir, "data", "raw", "panoramic_radiography_yolo_dataset_14_classes", "*", "images")
perio_dir = os.path.join(root_dir, "data", "raw", "Periodontal bone loss.v8i.yolov8", "*", "images")

ctrl_files = glob.glob(os.path.join(ctrl_dir, "*.*"))
perio_files = glob.glob(os.path.join(perio_dir, "*.*"))

print(f"Archivos encontrados: Control={len(ctrl_files)}, Periodontitis={len(perio_files)}")

# Muestra balanceada de 200 imagenes por clase para velocidad
np.random.seed(42)
ctrl_sub = np.random.choice(ctrl_files, min(200, len(ctrl_files)), replace=False)
perio_sub = np.random.choice(perio_files, min(200, len(perio_files)), replace=False)

extractor = FractalFeatureExtractor(box_min=2, lacunarity_scales=8)

X_list = []
y_list = []

feat_cols = [
    'fractal_D0', 'fractal_r2', 'lapidus_oscillation', 'minkowski_dimension',
    'minkowski_r2', 'lacunarity_mean', 'lacunarity_slope', 'multifractal_delta_alpha',
    'multifractal_D1', 'multifractal_D2', 'tda_beta_0', 'tda_beta_1',
    'tda_betti_ratio'
]

def process_file(img_path):
    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return None
    
    rois = extract_interdental_rois(img, roi_size=(64, 64), max_rois=1)
    if not rois:
        return None
    
    crop, _ = rois[0]
    clahe_crop = apply_clahe(crop, clip_limit=2.5)
    bin_crop = adaptive_trabecular_binarization(clahe_crop, window_size=15, k=0.2)
    
    feats = extractor.extract_features(bin_crop, roi_grayscale=clahe_crop)
    vec = [feats.get(c, 0.0) for c in feat_cols]
    return vec

print("Procesando ROIs trabeculares (Control)...")
count_ctrl = 0
for f in ctrl_sub:
    vec = process_file(f)
    if vec is not None:
        X_list.append(vec)
        y_list.append(0)
        count_ctrl += 1

print(f"Exito: {count_ctrl} ROIs de Control extraidas.")

print("Procesando ROIs trabeculares (Periodontitis)...")
count_perio = 0
for f in perio_sub:
    vec = process_file(f)
    if vec is not None:
        X_list.append(vec)
        y_list.append(1)
        count_perio += 1

print(f"Exito: {count_perio} ROIs de Periodontitis extraidas.")

X_roi = np.array(X_list)
y_roi = np.array(y_list)

print(f"\nMatriz Trabecular Pura: N = {len(y_roi)} parches (64x64 px).")

# Cross Validation
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
aucs, accs, precs, recs = [], [], [], []

for fold, (tr_idx, va_idx) in enumerate(skf.split(X_roi, y_roi)):
    X_tr, y_tr = X_roi[tr_idx], y_roi[tr_idx]
    X_va, y_va = X_roi[va_idx], y_roi[va_idx]
    
    clf = XGBClassifier(n_estimators=100, max_depth=3, learning_rate=0.05, random_state=42)
    clf.fit(X_tr, y_tr)
    
    probs = clf.predict_proba(X_va)[:, 1]
    preds = (probs >= 0.5).astype(int)
    
    aucs.append(roc_auc_score(y_va, probs))
    accs.append(accuracy_score(y_va, preds))
    precs.append(precision_score(y_va, preds))
    recs.append(recall_score(y_va, preds))

print("\n--- RESULTADOS DEL MODELO EN PARCHES TRABECULARES PURAS (LIBRE DE SESGO) ---")
print(f"ROC-AUC  : {np.mean(aucs):.4f} +/- {np.std(aucs):.4f}")
print(f"Accuracy : {np.mean(accs):.4f} +/- {np.std(accs):.4f}")
print(f"Precision: {np.mean(precs):.4f} +/- {np.std(precs):.4f}")
print(f"Recall   : {np.mean(recs):.4f} +/- {np.std(recs):.4f}")

final_roi_model = XGBClassifier(n_estimators=100, max_depth=3, learning_rate=0.05, random_state=42)
final_roi_model.fit(X_roi, y_roi)
roi_model_path = os.path.join(root_dir, "data", "processed", "latticebio_roi_model.json")
final_roi_model.save_model(roi_model_path)
print(f"\nModelo trabecular puro guardado en: {roi_model_path}")
print("==================================================")
