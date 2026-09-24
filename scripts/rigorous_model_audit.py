"""
Auditoria Rigurosa del Modelo XGBoost de Lattice Bio.
Evaluacion de métricas, calibación, importancia de características (Gain/SHAP) y testeo de casos sintéticos.
Nota: Output en ASCII estricto para compatibilidad con Windows cp1252.
"""

import os
import sys
import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import (
    roc_auc_score,
    average_precision_score,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    brier_score_loss,
    confusion_matrix,
)
from scipy.stats import ttest_ind, mannwhitneyu

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

csv_path = os.path.join(root_dir, "data", "processed", "dataset_latticebio_features.csv")
model_json_path = os.path.join(root_dir, "data", "processed", "latticebio_model.json")

print("==================================================")
print("AUDITORIA RIGUROSA DE PERFORMANCE DEL MODELO")
print("==================================================")

if not os.path.exists(csv_path):
    print("ERROR: Dataset CSV no encontrado en:", csv_path)
    sys.exit(1)

df = pd.read_csv(csv_path)
print(f"Dataset cargado: {len(df)} muestras.")

# Definir target
target_col = "target"
if target_col not in df.columns:
    if "source_dataset" in df.columns:
        df["target"] = df["source_dataset"].str.contains("Periodontal", case=False).astype(int)
    else:
        print("ERROR: Columna target no encontrada.")
        sys.exit(1)

feat_cols = [
    'fractal_D0', 'fractal_r2', 'lapidus_oscillation', 'minkowski_dimension',
    'minkowski_r2', 'lacunarity_mean', 'lacunarity_slope', 'multifractal_delta_alpha',
    'multifractal_D1', 'multifractal_D2', 'tda_beta_0', 'tda_beta_1',
    'tda_betti_ratio', 'tda_persistence_entropy_h0', 'tda_persistence_entropy_h1',
    'tda_mean_persistence_h1'
]

X = df[feat_cols].values
y = df["target"].values

print(f"Distribucion de clases: Control (0) = {np.sum(y == 0)}, Periodontitis (1) = {np.sum(y == 1)}")

# 1. ANALISIS DE SEPARABILIDAD ESTADISTICA DE LAS CARACTERISTICAS
print("\n--- 1. ANALISIS ESTADISTICO INDIVIDUAL DE CARACTERISTICAS ---")
print(f"{'Feature':<28} | {'Mean (Ctrl)':<11} | {'Mean (Perio)':<11} | {'p-value (MannW)':<15} | {'Cohen d':<8}")
print("-" * 82)

feature_stats = []
for feat in feat_cols:
    val_ctrl = df[df["target"] == 0][feat].values
    val_perio = df[df["target"] == 1][feat].values
    
    m_ctrl = np.mean(val_ctrl)
    m_perio = np.mean(val_perio)
    std_ctrl = np.std(val_ctrl, ddof=1)
    std_perio = np.std(val_perio, ddof=1)
    
    # Mann-Whitney U test
    stat, pval = mannwhitneyu(val_ctrl, val_perio, alternative='two-sided')
    
    # Cohen's d effect size
    pooled_std = np.sqrt(((len(val_ctrl)-1)*std_ctrl**2 + (len(val_perio)-1)*std_perio**2) / (len(val_ctrl) + len(val_perio) - 2))
    cohen_d = (m_perio - m_ctrl) / (pooled_std + 1e-12) if pooled_std > 0 else 0.0
    
    feature_stats.append({
        "feature": feat,
        "m_ctrl": m_ctrl,
        "m_perio": m_perio,
        "pval": pval,
        "cohen_d": cohen_d
    })
    
    pval_str = f"{pval:.2e}" if pval < 0.001 else f"{pval:.4f}"
    sig = "*" if pval < 0.05 else " "
    print(f"{feat:<28} | {m_ctrl:<11.4f} | {m_perio:<11.4f} | {pval_str:<15} {sig} | {cohen_d:<+8.3f}")

# 2. EVALUACION DE CROSS-VALIDATION Y CALIBRACION CON XGBOOST
from xgboost import XGBClassifier

print("\n--- 2. EVALUACION CON VALIDACION CRUZADA (5-FOLD CV) ---")
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

aucs, pr_aucs, accs, precs, recs, f1s, briers = [], [], [], [], [], [], []

for fold, (train_idx, val_idx) in enumerate(skf.split(X, y)):
    X_tr, y_tr = X[train_idx], y[train_idx]
    X_va, y_va = X[val_idx], y[val_idx]
    
    model = XGBClassifier(
        n_estimators=150,
        max_depth=4,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        eval_metric="logloss",
        random_state=42,
        use_label_encoder=False
    )
    model.fit(X_tr, y_tr)
    
    preds_prob = model.predict_proba(X_va)[:, 1]
    preds_bin = (preds_prob >= 0.5).astype(int)
    
    aucs.append(roc_auc_score(y_va, preds_prob))
    pr_aucs.append(average_precision_score(y_va, preds_prob))
    accs.append(accuracy_score(y_va, preds_bin))
    precs.append(precision_score(y_va, preds_bin))
    recs.append(recall_score(y_va, preds_bin))
    f1s.append(f1_score(y_va, preds_bin))
    briers.append(brier_score_loss(y_va, preds_prob))

print(f"ROC-AUC  : {np.mean(aucs):.4f} +/- {np.std(aucs):.4f}")
print(f"PR-AUC   : {np.mean(pr_aucs):.4f} +/- {np.std(pr_aucs):.4f}")
print(f"Accuracy : {np.mean(accs):.4f} +/- {np.std(accs):.4f}")
print(f"Precision: {np.mean(precs):.4f} +/- {np.std(precs):.4f}")
print(f"Recall   : {np.mean(recs):.4f} +/- {np.std(recs):.4f} (Sensibilidad)")
print(f"F1-Score : {np.mean(f1s):.4f} +/- {np.std(f1s):.4f}")
print(f"Brier Sc : {np.mean(briers):.4f} +/- {np.std(briers):.4f} (Calibracion: menor es mejor)")

# 3. EVALUACION DEL MODELO GUARDADO (latticebio_model.json)
print("\n--- 3. EVALUACION DEL ARCHIVO ENTRENADO FINAL (latticebio_model.json) ---")
if os.path.exists(model_json_path):
    final_model = XGBClassifier()
    final_model.load_model(model_json_path)
    
    all_probs = final_model.predict_proba(X)[:, 1]
    all_preds = (all_probs >= 0.5).astype(int)
    
    cm = confusion_matrix(y, all_preds)
    tn, fp, fn, tp = cm.ravel()
    
    spec = tn / (tn + fp)
    sens = tp / (tp + fn)
    
    print(f"Matriz de Confusion (Full Dataset N={len(y)}):")
    print(f"  Verdaderos Negativos (Control correcto)  : {tn} ({tn/np.sum(y==0)*100:.1f}%)")
    print(f"  Falsos Positivos (Control clasif Perio) : {fp} ({fp/np.sum(y==0)*100:.1f}%)")
    print(f"  Falsos Negativos (Perio no detectado)   : {fn} ({fn/np.sum(y==1)*100:.1f}%)")
    print(f"  Verdaderos Positivos (Perio detectado)  : {tp} ({tp/np.sum(y==1)*100:.1f}%)")
    print(f"Especificidad Clinica (Control) : {spec*100:.2f}%")
    print(f"Sensibilidad Clinica (Reabsorcion): {sens*100:.2f}%")
    print(f"ROC-AUC Global                    : {roc_auc_score(y, all_probs):.4f}")
    
    # Importancia de Caracteristicas
    importances = final_model.feature_importances_
    sorted_idx = np.argsort(importances)[::-1]
    
    print("\nRanking de Importancia de Caracteristicas (XGBoost Gain Weight):")
    for rank, idx in enumerate(sorted_idx, 1):
        print(f"  {rank:2d}. {feat_cols[idx]:<28} : {importances[idx]*100:.2f}%")

else:
    print("WARNING: Archivo de modelo latticebio_model.json no existe.")

# 4. PRUEBA EN PATRONES SINTETICOS EXTREMOS (DASHBOARD TEST)
print("\n--- 4. TEST DE CASOS CONTRASTANTES SINTETICOS ---")
from scipy.ndimage import gaussian_filter
from src.preprocessing.contrast_normalization import apply_clahe, adaptive_trabecular_binarization
from src.fractal.feature_extractor import FractalFeatureExtractor

# Generar sano simulado
np.random.seed(101)
grid_sano = np.random.randn(300, 300)
smooth_sano = gaussian_filter(grid_sano, sigma=3.8)
norm_sano = (smooth_sano - smooth_sano.min()) / (smooth_sano.max() - smooth_sano.min() + 1e-8)
img_sano = (norm_sano * 255).astype(np.uint8)

# Generar periodontitis simulado
np.random.seed(202)
grid_per = np.random.randn(300, 300)
smooth_per = gaussian_filter(grid_per, sigma=6.5)
norm_per = (smooth_per - smooth_per.min()) / (smooth_per.max() - smooth_per.min() + 1e-8)
holes = gaussian_filter(np.random.randn(300, 300), sigma=18.0) > 0.4
norm_per[holes] = norm_per[holes] * 0.25
img_per = (norm_per * 255).astype(np.uint8)

extractor = FractalFeatureExtractor(box_min=2, lacunarity_scales=8)

# Procesar sano
clahe_sano = apply_clahe(img_sano, clip_limit=2.5)
bin_sano = adaptive_trabecular_binarization(clahe_sano, window_size=25, k=0.2)
feat_sano = extractor.extract_features(bin_sano, roi_grayscale=clahe_sano)
x_sano = np.array([[feat_sano.get(c, 0.0) for c in feat_cols]])
prob_sano = float(final_model.predict_proba(x_sano)[0, 1])

# Procesar periodontitis
clahe_per = apply_clahe(img_per, clip_limit=2.5)
bin_per = adaptive_trabecular_binarization(clahe_per, window_size=25, k=0.2)
feat_per = extractor.extract_features(bin_per, roi_grayscale=clahe_per)
x_per = np.array([[feat_per.get(c, 0.0) for c in feat_cols]])
prob_per = float(final_model.predict_proba(x_per)[0, 1])

print(f"Sintetico Hueso Sano    -> Probabilidad de Perdida Osea: {prob_sano*100:.2f}% | Score Salud: {(1-prob_sano)*100:.1f}/100")
print(f"Sintetico Periodontitis -> Probabilidad de Perdida Osea: {prob_per*100:.2f}% | Score Salud: {(1-prob_per)*100:.1f}/100")

print("\n==================================================")
print("AUDITORIA COMPLETADA EXITOSAMENTE")
print("==================================================")
