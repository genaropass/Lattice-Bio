"""
Prueba directa de Inferencia con el Modelo Des-sesgado (latticebio_roi_model.json).
Carga 5 muestras reales de Control y 5 de Periodontitis y reporta sus probabilidades.
"""

import os
import sys
import glob
import cv2
import numpy as np
from xgboost import XGBClassifier

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from src.preprocessing.roi_segmentation import extract_interdental_rois
from src.preprocessing.contrast_normalization import apply_clahe, adaptive_trabecular_binarization
from src.fractal.feature_extractor import FractalFeatureExtractor

model_path = os.path.join(root_dir, "data", "processed", "latticebio_roi_model.json")
if not os.path.exists(model_path):
    print("ERROR: Modelo ROI no encontrado.")
    sys.exit(1)

model = XGBClassifier()
model.load_model(model_path)
extractor = FractalFeatureExtractor(box_min=2, lacunarity_scales=8)

feat_order_roi = [
    'fractal_D0', 'fractal_r2', 'lapidus_oscillation', 'minkowski_dimension',
    'minkowski_r2', 'lacunarity_mean', 'lacunarity_slope', 'multifractal_delta_alpha',
    'multifractal_D1', 'multifractal_D2', 'tda_beta_0', 'tda_beta_1',
    'tda_betti_ratio'
]

ctrl_files = glob.glob(os.path.join(root_dir, "data", "raw", "panoramic_radiography_yolo_dataset_14_classes", "*", "images", "*.*"))[:5]
perio_files = glob.glob(os.path.join(root_dir, "data", "raw", "Periodontal bone loss.v8i.yolov8", "*", "images", "*.*"))[:5]

def evaluate_file(path, label_str):
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return
    rois = extract_interdental_rois(img, roi_size=(64, 64), max_rois=1)
    if not rois:
        return
    crop, _ = rois[0]
    clahe_crop = apply_clahe(crop, clip_limit=2.5)
    bin_crop = adaptive_trabecular_binarization(clahe_crop, window_size=15, k=0.2)
    feats = extractor.extract_features(bin_crop, roi_grayscale=clahe_crop)
    x_vec = np.array([[feats.get(c, 0.0) for c in feat_order_roi]])
    prob = float(model.predict_proba(x_vec)[0, 1])
    fname = os.path.basename(path)
    print(f"[{label_str}] {fname:<30} -> Prob. Perdida Osea: {prob*100:5.1f}% | Score Salud: {(1-prob)*100:5.1f}/100")

print("==================================================")
print("INFERENCIA CON MODELO DES-SESGADO (ROI TRABECULAR)")
print("==================================================")
print("\nMUESTRAS CONTROL (PANORAMICAS):")
for f in ctrl_files:
    evaluate_file(f, "CONTROL")

print("\nMUESTRAS PERIODONTITIS (PERIAPICALES):")
for f in perio_files:
    evaluate_file(f, "PERIO  ")
print("==================================================")
