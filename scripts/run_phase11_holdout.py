"""
Script Principal de Evaluación del Holdout (Fase 11 — One-Time Holdout Evaluation).
- Opera EXCLUSIVAMENTE sobre las muestras INCLUDED del Holdout (193 imágenes / 162 pacientes).
- Se ejecuta UNA SOLA VEZ sobre el Holdout congelado según la regla estricta de cortafuegos de F10.
- Verifica el hash SHA256 (85e3a856e5a1334d53084f242fff50a92c1c662fe1d4c8797053261578d2b335) antes de acceder a cualquier imagen.
- Extrae la serie congelada SET_G_LOCKED: {fractal_D0, minkowski_dimension, multifractal_delta_alpha, tda_beta_0}.
- Calcula diferencias pareadas intra-paciente (Cresta vs Basal), Cohen's dz out-of-sample y bootstrap CIs (95%, 1000 iteraciones).
- Compara los tamaños de efecto (Cohen's dz) de F11 Holdout vs F10 Development.
- Genera data/processed/phase11_holdout_results.csv y data/processed/phase11_holdout_summary.csv.
- Registra la entrada EXP-F11-001 en data/processed/experiment_ledger.csv.
Nota: ASCII estricto para compatibilidad Windows cp1252.
"""

import os
import sys
import json
import hashlib
import cv2
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.insert(0, root_dir)

from src.preprocessing.roi_segmentation import extract_anatomical_reference_rois
from src.preprocessing.contrast_normalization import preprocess_radiograph_roi, normalize_intensity
from src.fractal.feature_extractor import FractalFeatureExtractor

config_path = os.path.join(root_dir, "configs", "phase11_holdout_evaluation.json")
lock_config_path = os.path.join(root_dir, "configs", "final_pipeline_lock_v1.json")
manifest_path = os.path.join(root_dir, "data", "processed", "final_dataset_manifest.csv")
holdout_path = os.path.join(root_dir, "data", "processed", "holdout_test_split.json")
results_csv_path = os.path.join(root_dir, "data", "processed", "phase11_holdout_results.csv")
summary_csv_path = os.path.join(root_dir, "data", "processed", "phase11_holdout_summary.csv")
figures_dir = os.path.join(root_dir, "data", "processed", "phase11_figures")
ledger_path = os.path.join(root_dir, "data", "processed", "experiment_ledger.csv")

os.makedirs(figures_dir, exist_ok=True)

EXPECTED_HOLDOUT_HASH = "85e3a856e5a1334d53084f242fff50a92c1c662fe1d4c8797053261578d2b335"

# Development Baselines from F10 Final Lock
DEV_BASELINES = {
    "fractal_D0": {"dz": -0.1988, "mean_diff": -0.0145, "crest_mean": 1.3789, "basal_mean": 1.3934},
    "minkowski_dimension": {"dz": -0.8161, "mean_diff": -0.0450, "crest_mean": 2.4578, "basal_mean": 2.5028},
    "multifractal_delta_alpha": {"dz": 0.5177, "mean_diff": 0.0791, "crest_mean": 0.5841, "basal_mean": 0.5050},
    "tda_beta_0": {"dz": 0.3609, "mean_diff": 26.25, "crest_mean": 214.35, "basal_mean": 188.10}
}

print("==================================================")
print("FASE 11: ONE-TIME HOLDOUT EVALUATION")
print("==================================================")

# 1. Firewall Security Check: Holdout SHA256
if not os.path.exists(holdout_path):
    print("CRITICAL ERROR: Holdout split file does not exist!")
    sys.exit(1)

with open(holdout_path, "rb") as f:
    holdout_hash = hashlib.sha256(f.read()).hexdigest()

if holdout_hash != EXPECTED_HOLDOUT_HASH:
    print(f"CRITICAL ERROR: Holdout SHA256 mismatch! Expected {EXPECTED_HOLDOUT_HASH}, got {holdout_hash}")
    sys.exit(1)

print(f"[PASS] Holdout SHA256 firewall verified: {holdout_hash}")

# 2. Cargar Manifest (Solo Holdout Included)
df_manifest = pd.read_csv(manifest_path)
holdout_df = df_manifest[(df_manifest["split"] == "Holdout") & (df_manifest["inclusion_status"] == "INCLUDED")].reset_index(drop=True)

print(f"Dataset Holdout cargado: {len(holdout_df)} imagenes ({len(holdout_df['patient_id'].unique())} pacientes)")

if len(holdout_df) != 193 or len(holdout_df['patient_id'].unique()) != 162:
    print(f"WARNING: Holdout size differs from expectation (193 img / 162 pts). Found: {len(holdout_df)} img / {len(holdout_df['patient_id'].unique())} pts.")

# 3. Extracción de Features Congeladas SET_G_LOCKED
extractor = FractalFeatureExtractor(use_tda=True, use_minkowski=True)
locked_descriptors = ["fractal_D0", "minkowski_dimension", "multifractal_delta_alpha", "tda_beta_0"]

feature_rows = []

for idx, row in holdout_df.iterrows():
    if (idx + 1) % 50 == 0 or (idx + 1) == len(holdout_df):
        print(f"Procesando Holdout imagen {idx+1}/{len(holdout_df)}...")
        
    img_path = row["filepath"]
    patient_id = row["patient_id"]
    filename = row["filename"]
    source = row["source"]

    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        print(f"ERROR: No se pudo cargar la imagen {img_path}")
        continue

    # Extracción anatómica determinística congelada F6
    rois = extract_anatomical_reference_rois(img, patch_size=(64, 64), crest_y_ratio=0.45, basal_y_ratio=0.80, x_ratio=0.50)
    crop_crest, _ = rois["crest"]
    crop_basal, _ = rois["basal"]

    # Preprocessing Pipeline-A (Grayscale MinMax)
    norm_crest_a = normalize_intensity(crop_crest, method="minmax")
    norm_basal_a = normalize_intensity(crop_basal, method="minmax")

    # Preprocessing Pipeline-B (CLAHE 2.5 + Sauvola W=15, k=0.2)
    clahe_crest_b, bin_crest_b = preprocess_radiograph_roi(crop_crest, clip_limit=2.5, sauvola_window=15)
    clahe_basal_b, bin_basal_b = preprocess_radiograph_roi(crop_basal, clip_limit=2.5, sauvola_window=15)

    # Extracción de Descriptores
    feats_crest = extractor.extract_features(roi_mask=bin_crest_b, roi_grayscale=crop_crest)
    feats_basal = extractor.extract_features(roi_mask=bin_basal_b, roi_grayscale=crop_basal)

    record = {
        "patient_id": patient_id,
        "filename": filename,
        "source": source,
        "filepath": img_path
    }

    for desc in locked_descriptors:
        val_crest = feats_crest.get(desc, 0.0)
        val_basal = feats_basal.get(desc, 0.0)
        
        record[f"{desc}_crest"] = val_crest
        record[f"{desc}_basal"] = val_basal
        
        if abs(val_basal) > 1e-6:
            record[f"{desc}_r_trab"] = val_crest / val_basal
        else:
            record[f"{desc}_r_trab"] = 0.0

    feature_rows.append(record)

df_holdout_feats = pd.DataFrame(feature_rows)
df_holdout_feats.to_csv(results_csv_path, index=False)
print(f"[PASS] Extraidas y guardadas features del Holdout en: {results_csv_path}")

# 4. Agrupar por paciente (Unidad de Análisis: PATIENT)
patient_df = df_holdout_feats.groupby("patient_id").mean(numeric_only=True).reset_index()
n_pts = len(patient_df)

print("\n" + "=" * 50)
print(f" RESULTADOS CIENTIFICOS DEL HOLDOUT (N = {n_pts} PACIENTES)")
print("=" * 50)

np.random.seed(42)
n_boot = 1000
summary_rows = []

for desc in locked_descriptors:
    col_crest = f"{desc}_crest"
    col_basal = f"{desc}_basal"
    
    vals_c = patient_df[col_crest].values
    vals_b = patient_df[col_basal].values
    diffs = vals_c - vals_b
    
    mean_c = float(np.mean(vals_c))
    mean_b = float(np.mean(vals_b))
    mean_diff = float(np.mean(diffs))
    sd_diff = float(np.std(diffs, ddof=1))
    
    cohens_dz = mean_diff / (sd_diff + 1e-8)
    
    ttest_res = stats.ttest_rel(vals_c, vals_b)
    wilcoxon_res = stats.wilcoxon(vals_c, vals_b)
    
    # Bootstrap CIs 95% a nivel paciente
    boot_indices = np.random.choice(n_pts, size=(n_boot, n_pts), replace=True)
    boot_means = np.mean(diffs[boot_indices], axis=1)
    boot_dzs = np.mean(diffs[boot_indices], axis=1) / (np.std(diffs[boot_indices], axis=1, ddof=1) + 1e-8)
    
    ci_diff_lower = float(np.percentile(boot_means, 2.5))
    ci_diff_upper = float(np.percentile(boot_means, 97.5))
    ci_dz_lower = float(np.percentile(boot_dzs, 2.5))
    ci_dz_upper = float(np.percentile(boot_dzs, 97.5))
    
    dev_dz = DEV_BASELINES[desc]["dz"]
    dir_match = (np.sign(cohens_dz) == np.sign(dev_dz))
    ratio_dz = cohens_dz / dev_dz if dev_dz != 0 else 0.0
    
    summary_rows.append({
        "descriptor": desc,
        "n_patients": n_pts,
        "holdout_mean_crest": round(mean_c, 4),
        "holdout_mean_basal": round(mean_b, 4),
        "holdout_mean_diff": round(mean_diff, 4),
        "holdout_cohens_dz": round(cohens_dz, 4),
        "holdout_dz_ci_95": f"[{round(ci_dz_lower, 4)}, {round(ci_dz_upper, 4)}]",
        "p_val_ttest": f"{ttest_res.pvalue:.4e}",
        "p_val_wilcoxon": f"{wilcoxon_res.pvalue:.4e}",
        "dev_cohens_dz": dev_dz,
        "direction_reproduced": "YES" if dir_match else "NO",
        "magnitude_ratio_holdout_vs_dev": round(ratio_dz, 4)
    })

df_summary = pd.DataFrame(summary_rows)
df_summary.to_csv(summary_csv_path, index=False)
print(df_summary.to_string(index=False))

# 5. Generar Gráficos Comparativos Development vs Holdout
fig, axes = plt.subplots(2, 2, figsize=(12, 10))
axes = axes.flatten()

for i, desc in enumerate(locked_descriptors):
    ax = axes[i]
    col_c = f"{desc}_crest"
    col_b = f"{desc}_basal"
    
    dev_c = DEV_BASELINES[desc]["crest_mean"]
    dev_b = DEV_BASELINES[desc]["basal_mean"]
    ho_c = float(np.mean(patient_df[col_c]))
    ho_b = float(np.mean(patient_df[col_b]))
    
    x = np.arange(2)
    width = 0.35
    
    rects1 = ax.bar(x - width/2, [dev_c, dev_b], width, label='Dev (N=643 pts)', color='#3498db', alpha=0.85)
    rects2 = ax.bar(x + width/2, [ho_c, ho_b], width, label='Holdout (N=162 pts)', color='#e74c3c', alpha=0.85)
    
    ax.set_title(f"{desc}\nDev dz={DEV_BASELINES[desc]['dz']} | Holdout dz={df_summary.loc[df_summary['descriptor']==desc, 'holdout_cohens_dz'].values[0]}", fontsize=10)
    ax.set_xticks(x)
    ax.set_xticklabels(['ROI Cresta', 'ROI Basal'])
    ax.legend()
    ax.grid(axis='y', linestyle='--', alpha=0.5)

plt.suptitle("FASE 11: Reproducibilidad del Contraste Estructural en Holdout Independiente", fontsize=14, y=0.98)
plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.savefig(os.path.join(figures_dir, "f11_holdout_vs_dev_comparison.png"), dpi=150)
plt.close()

print(f"\n[PASS] Grafico guardado en: {os.path.join(figures_dir, 'f11_holdout_vs_dev_comparison.png')}")

# 6. Registrar entrada EXP-F11-001 en experiment_ledger.csv
ledger_entry = {
    "exp_id": "EXP-F11-001",
    "date": "2026-09-24",
    "dataset": "Holdout Included (193 img / 162 pts)",
    "preprocessing": "Pipeline-A/Pipeline-B (v1.0 Frozen)",
    "feature_set": "SET_G_LOCKED (D0, DM, Delta_alpha, beta0)",
    "model": "One-Time Out-of-Sample Holdout Evaluation",
    "split": "Holdout Only (Firewall Cleared)",
    "target": "Paired Intra-patient Structural Contrast Generalizability",
    "auc": "N/A",
    "status": "VALID",
    "reason": "One-time holdout evaluation completed with zero parameter tuning or post-hoc adjustments."
}

if os.path.exists(ledger_path):
    df_ledger = pd.read_csv(ledger_path)
    df_ledger = pd.concat([df_ledger, pd.DataFrame([ledger_entry])], ignore_index=True)
else:
    df_ledger = pd.DataFrame([ledger_entry])

df_ledger.to_csv(ledger_path, index=False)
print(f"[PASS] Entrada EXP-F11-001 registrada exitosamente en experiment_ledger.csv.")
print("==================================================")
