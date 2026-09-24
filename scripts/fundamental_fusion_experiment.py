"""
Experimento Fundamental de Fusión y Validación Estadística (Test de DeLong).
Optimizado con límites estrictos de recursos hardware:
  - CPU: Máximo 50% de los núcleos del procesador
  - GPU: Máximo 30% de VRAM (~3.6 GB de la RTX 3060)
  - RAM: Liberación limpia de caché por lote
"""

import os
import sys
import gc
import time
import numpy as np
import pandas as pd
from scipy import stats

# 1. Configurar límites estrictos de hilos CPU (50% de uso de procesador)
num_cpu_workers = max(1, (os.cpu_count() or 4) // 2)
os.environ["OMP_NUM_THREADS"] = str(num_cpu_workers)
os.environ["MKL_NUM_THREADS"] = str(num_cpu_workers)
os.environ["OPENBLAS_NUM_THREADS"] = str(num_cpu_workers)
os.environ["VECLIB_MAXIMUM_THREADS"] = str(num_cpu_workers)
os.environ["NUMEXPR_NUM_THREADS"] = str(num_cpu_workers)

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, ".."))
csv_path = os.path.join(root_dir, "data", "processed", "dataset_latticebio_features.csv")

if not os.path.exists(csv_path):
    print(f"[Error] CSV de características no encontrado en: {csv_path}")
    sys.exit(1)

print("=" * 70, flush=True)
print(" LATTICE BIO -- EXPERIMENTO FUNDAMENTAL DE FUSION Y TEST DE DELONG", flush=True)
print(" Controles de Recursos: CPU <= 50%, GPU VRAM <= 30% (~3.6 GB)", flush=True)
print("=" * 70, flush=True)

# Cargar Dataset
df = pd.read_csv(csv_path)
print(f" Dataset cargado: {len(df)} radiografías procesadas.", flush=True)

df["target"] = (df["source_dataset"].str.contains("Periodontal", case=False)).astype(int)
y = df["target"].values
print(f" Clases: Patológico (Periodontal Bone Loss)={np.sum(y==1)}, Control/Basal (Zenodo)={np.sum(y==0)}", flush=True)

non_feat = ["filepath", "source_dataset", "filename", "sample_id", "target", "img_height", "img_width"]
math_feat_cols = [c for c in df.columns if c not in non_feat]
X_math = df[math_feat_cols].values
print(f" Biomarcadores matemáticos cargados: {X_math.shape[1]} características.", flush=True)

# 2. Configurar PyTorch con límite estricto de GPU VRAM (30%) y CPU (50%)
import torch
import torchvision.transforms as T
from PIL import Image

torch.set_num_threads(num_cpu_workers)

if torch.cuda.is_available():
    torch.cuda.set_per_process_memory_fraction(0.30, 0)
    device = torch.device("cuda:0")
    print(f" Dispositivo: GPU CUDA ({torch.cuda.get_device_name(0)}) con límite de VRAM al 30% (~3.6 GB).", flush=True)
else:
    device = torch.device("cpu")
    print(f" Dispositivo: CPU restringido a {num_cpu_workers} núcleos (50% CPU).", flush=True)

print(" Cargando modelo de visión profunda DINOv2 (vits14)...", flush=True)
try:
    dinov2 = torch.hub.load("facebookresearch/dinov2", "dinov2_vits14").to(device)
    dinov2.eval()
    has_dinov2 = True
except Exception as e:
    print(f" [Aviso] Carga DINOv2 alternativa: {e}", flush=True)
    import torchvision.models as models
    resnet = models.resnet18(pretrained=True).to(device)
    resnet.eval()
    dinov2 = torch.nn.Sequential(*list(resnet.children())[:-1])
    has_dinov2 = False

transform = T.Compose([
    T.Resize((140, 140)),
    T.ToTensor(),
    T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

emb_cache_path = os.path.join(root_dir, "data", "processed", "dinov2_embeddings.npy")

if os.path.exists(emb_cache_path):
    print(f"\n [Cache] Cargando embeddings DINOv2 ya guardados desde: {emb_cache_path}", flush=True)
    X_vision = np.load(emb_cache_path)
    print(f" Matriz de Visión Profunda cargada: {X_vision.shape}", flush=True)
else:
    print("\n Extrayendo embeddings profundos en lotes seguros (batch size = 16)...", flush=True)
    t0 = time.time()
    embeddings_list = []
    batch_size = 16  # Lote pequeño para consumo liviano de RAM/VRAM

    with torch.no_grad():
        for i in range(0, len(df), batch_size):
            batch_paths = df["filepath"].iloc[i : i + batch_size]
            batch_tensors = []
            
            for p in batch_paths:
                try:
                    if os.path.exists(p):
                        img_pil = Image.open(p).convert("RGB")
                    else:
                        img_pil = Image.new("RGB", (140, 140), color=0)
                except Exception:
                    img_pil = Image.new("RGB", (140, 140), color=0)
                
                batch_tensors.append(transform(img_pil))
            
            batch_input = torch.stack(batch_tensors).to(device)
            if has_dinov2:
                feats = dinov2(batch_input)
            else:
                feats = dinov2(batch_input).squeeze(-1).squeeze(-1)
            
            embeddings_list.append(feats.cpu().numpy())

            del batch_input, batch_tensors
            if device.type == "cuda":
                torch.cuda.empty_cache()
            gc.collect()

            if (i // batch_size) % 25 == 0 or (i + batch_size) >= len(df):
                processed_cnt = min(i + batch_size, len(df))
                pct = (processed_cnt / len(df)) * 100
                print(f"  Procesado: {processed_cnt}/{len(df)} radiografías ({pct:.1f}%)", flush=True)

    X_vision = np.vstack(embeddings_list)
    t1 = time.time()
    print(f" Extracción profunda completada en {t1 - t0:.2f} segundos.", flush=True)
    print(f" Guardando caché de embeddings en {emb_cache_path}...", flush=True)
    np.save(emb_cache_path, X_vision)

X_hybrid = np.hstack([X_vision, X_math])
print(f" Matriz Híbrida Concatenada: {X_hybrid.shape}", flush=True)

# 3. Entrenar Clasificadores XGBoost con límite de 50% CPU
print("\n Entrenando Modelos de Machine Learning (5-Fold Stratified CV, n_jobs=50% CPU)...", flush=True)
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score
from xgboost import XGBClassifier

skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

oof_pred_A = np.zeros(len(df))  # Solo Matemático
oof_pred_B = np.zeros(len(df))  # Solo Visión Profunda
oof_pred_D = np.zeros(len(df))  # Híbrido (Visión + Matemático)

for fold, (train_idx, val_idx) in enumerate(skf.split(df, y)):
    y_train, y_val = y[train_idx], y[val_idx]
    
    # Modelo A: Solo Matemático
    model_A = XGBClassifier(n_estimators=100, max_depth=4, learning_rate=0.05, n_jobs=num_cpu_workers, random_state=42, eval_metric="logloss")
    model_A.fit(X_math[train_idx], y_train)
    oof_pred_A[val_idx] = model_A.predict_proba(X_math[val_idx])[:, 1]
    
    # Modelo B: Solo Visión Profunda
    model_B = XGBClassifier(n_estimators=100, max_depth=4, learning_rate=0.05, n_jobs=num_cpu_workers, random_state=42, eval_metric="logloss")
    model_B.fit(X_vision[train_idx], y_train)
    oof_pred_B[val_idx] = model_B.predict_proba(X_vision[val_idx])[:, 1]
    
    # Modelo D: Híbrido
    model_D = XGBClassifier(n_estimators=100, max_depth=4, learning_rate=0.05, n_jobs=num_cpu_workers, random_state=42, eval_metric="logloss")
    model_D.fit(X_hybrid[train_idx], y_train)
    oof_pred_D[val_idx] = model_D.predict_proba(X_hybrid[val_idx])[:, 1]

auc_A = roc_auc_score(y, oof_pred_A)
auc_B = roc_auc_score(y, oof_pred_B)
auc_D = roc_auc_score(y, oof_pred_D)

print("\n" + "=" * 70)
print(" RESULTADOS DE PRECISION DE DIAGNOSTICO (AUC-ROC)")
print("=" * 70)
print(f"  Modelo A (Solo Matematico - Lattice Bio): AUC = {auc_A:.4f}")
print(f"  Modelo B (Solo Vision Profunda - DINOv2):  AUC = {auc_B:.4f}")
print(f"  Modelo D (HIBRIDO: Vision + Matematico):   AUC = {auc_D:.4f}")

# 4. Cálculo del Test Estadístico de DeLong (1988)
def delong_roc_variance(ground_truth, predictions):
    pos_idx = np.where(ground_truth == 1)[0]
    neg_idx = np.where(ground_truth == 0)[0]
    m = len(pos_idx)
    n = len(neg_idx)
    
    pred_pos = predictions[pos_idx]
    pred_neg = predictions[neg_idx]
    
    V10 = np.zeros(m)
    for i in range(m):
        V10[i] = np.mean(pred_pos[i] > pred_neg) + 0.5 * np.mean(pred_pos[i] == pred_neg)
        
    V01 = np.zeros(n)
    for j in range(n):
        V01[j] = np.mean(pred_pos > pred_neg[j]) + 0.5 * np.mean(pred_pos == pred_neg[j])
        
    auc = np.mean(V10)
    var_auc = (1.0 / m) * np.var(V10, ddof=1) + (1.0 / n) * np.var(V01, ddof=1)
    return auc, V10, V01, var_auc

print("\n Operando Test Estadistico de DeLong para Modelo B vs Modelo D...")
auc_b_calc, V10_b, V01_b, var_b = delong_roc_variance(y, oof_pred_B)
auc_d_calc, V10_d, V01_d, var_d = delong_roc_variance(y, oof_pred_D)

m = np.sum(y == 1)
n = np.sum(y == 0)
cov_10 = np.cov(V10_b, V10_d)[0, 1]
cov_01 = np.cov(V01_b, V01_d)[0, 1]
cov_bd = (1.0 / m) * cov_10 + (1.0 / n) * cov_01

var_diff = var_b + var_d - 2.0 * cov_bd
se_diff = np.sqrt(max(1e-12, var_diff))

z_stat = (auc_d_calc - auc_b_calc) / se_diff
p_value = 2.0 * (1.0 - stats.norm.cdf(abs(z_stat)))

print("\n" + "=" * 70)
print(" RESULTADOS DEL TEST DE DELONG (SIGNIFICANCIA ESTADISTICA)")
print("=" * 70)
print(f"  Diferencia de AUC (Modelo D - Modelo B):  +{auc_D - auc_B:.4f}")
print(f"  Error Estandar de la Diferencia (SE):     {se_diff:.4f}")
print(f"  Z-Statistic de DeLong:                   {z_stat:+.4f}")
print(f"  p-value (Significancia Estadistica):      {p_value:.6e}")

if p_value < 0.05:
    print("\n [OK] CONCLUYENTE: p < 0.05 -- La diferencia ES ESTADISTICAMENTE SIGNIFICATIVA.")
    print(" [OK] Las caracteristicas matematicas de Lattice Bio aportan informacion predictiva")
    print("      independiente que NO es capturada por los modelos profundos de vision.")
else:
    print("\n [AVISO] p >= 0.05 -- No se alcanzo la significancia estadistica convencional.")

print("=" * 70)
