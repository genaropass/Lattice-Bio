# FASE 11 — ONE-TIME HOLDOUT EVALUATION

## RESUMEN EJECUTIVO

La **Fase 11 (One-Time Holdout Evaluation)** evaluó por **única vez** el pipeline metodológico congelado en la Fase 10 (`v1.0_final_lock`) sobre el conjunto de datos **Holdout congelado e independiente** (193 imágenes intraorales periapicales / 162 pacientes únicos).

### Resultado Principal
El contraste estructural intra-paciente pareado (ROI Cresta Alveolar vs ROI Basal Mandibular) **se reprodujo al 100% fuera de muestra (out-of-sample)** en los 4 descriptores matemáticos primarios de `SET_G_LOCKED`. No se observó degradación ni atenuación del tamaño de efecto en pacientes independientes.

```text
STATUS = CLOSED (PASS)
VERDICT = REPRODUCED_OUT_OF_SAMPLE
HOLDOUT_HASH = 85e3a856e5a1334d53084f242fff50a92c1c662fe1d4c8797053261578d2b335 (PASS)
FIREWALL_VIOLATIONS = 0
POST_HOC_ADJUSTMENTS = 0
```

---

## 1. CORTAFUEGOS CIENTÍFICO Y PROTOCOLO DE EVALUACIÓN ÚNICA

De acuerdo con el protocolo estricto establecido en F10:
1. El archivo de split `data/processed/holdout_test_split.json` permaneció sellado criptográficamente hasta el inicio de F11.
2. Se verificó que el hash SHA256 fuera exactamente `85e3a856e5a1334d53084f242fff50a92c1c662fe1d4c8797053261578d2b335`.
3. Ningún parámetro de preprocesamiento, definición de ROI, fórmula matemática, criterio de inclusión ni prueba estadística fue modificado durante o después de la evaluación del Holdout.
4. No se realizó ajuste de hiperparámetros, re-entrenamiento ni selección iterativa de características.

---

## 2. DESCRIPCIÓN DE LA MUESTRA HOLDOUT

* **Imágenes procesadas**: 193 radiografías intraorales periapicales.
* **Pacientes independientes**: 162 pacientes únicos.
* **Solapamiento con Development**: 0 pacientes (Aislamiento 100% verificado).
* **Unidad de análisis**: `patient_id` (promediando imágenes de un mismo paciente cuando corresponde).

---

## 3. PIPELINE Y FEATURE SET CONGELADO (`SET_G_LOCKED`)

El pipeline evaluado corresponde exactamente al congelado en F10:

```text
SET_G_LOCKED =
{
    fractal_D0: Box-Counting Dimension (Pipeline-B),
    minkowski_dimension: Surface Blanket 2.5D Dimension (Pipeline-A),
    multifractal_delta_alpha: Singularity Spectrum Width (Pipeline-B),
    tda_beta_0: Connected Components Betti-0 (Pipeline-B)
}
```

* **ROI Cresta (ROI A)**: Centro $(0.50w, 0.45h)$, parche $64 \times 64$ px.
* **ROI Basal (ROI B)**: Centro $(0.50w, 0.80h)$, parche $64 \times 64$ px.
* **Pipeline-A**: Grayscale Lanczos4 $35\ \mu\text{m/px}$ nominal (sin CLAHE).
* **Pipeline-B**: Lanczos4 $35\ \mu\text{m/px}$ nominal + CLAHE $2.5$ ($8 \times 8$) + Binarización Sauvola ($W=15, k=0.2$).

---

## 4. RESULTADOS CUANTITATIVOS OUT-OF-SAMPLE (HOLDOUT N = 162 PACIENTES)

### Tabla 1: Comparación de Contraste Estructural Pareado en Holdout

| Descriptor | Holdout Cresta (Media) | Holdout Basal (Media) | Dif. Pareada $(\Delta)$ | Cohen's $d_z$ (Holdout) | IC 95% Bootstrap $d_z$ | p-value (t-test) | p-value (Wilcoxon) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`fractal_D0`** | 1.9191 | 1.9204 | -0.0013 | **-0.2321** | [-0.4071, -0.0857] | $3.5992 \times 10^{-3}$ | $7.3524 \times 10^{-6}$ |
| **`minkowski_dimension`** | 2.3899 | 2.4906 | -0.1006 | **-0.8656** | [-1.0559, -0.6984] | $2.1572 \times 10^{-21}$ | $1.9184 \times 10^{-18}$ |
| **`multifractal_delta_alpha`** | 0.4102 | 0.0742 | +0.3360 | **+0.5893** | [+0.4800, +0.6979] | $4.0321 \times 10^{-12}$ | $4.8798 \times 10^{-23}$ |
| **`tda_beta_0`** | 3.1111 | 1.5658 | +1.5453 | **+0.3303** | [+0.2614, +0.4674] | $4.3416 \times 10^{-5}$ | $2.7283 \times 10^{-9}$ |

---

## 5. COMPARACIÓN Y REPRODUCIBILIDAD: DEVELOPMENT VS HOLDOUT

### Tabla 2: Análisis de Reproducibilidad Out-of-Sample

| Descriptor | Cohen's $d_z$ (Dev F10) | Cohen's $d_z$ (Holdout F11) | Reprod. Direccional | Ratio de Magnitud $\left(\frac{d_{z,\text{Holdout}}}{d_{z,\text{Dev}}}\right)$ | Conclusión de Reproducibilidad |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **`fractal_D0`** | -0.1988 | **-0.2321** | **SÍ** | 1.1677 | **Reproducido** (Magnitud 116.8%) |
| **`minkowski_dimension`** | -0.8161 | **-0.8656** | **SÍ** | 1.0607 | **Reproducido** (Magnitud 106.1%) |
| **`multifractal_delta_alpha`** | +0.5177 | **+0.5893** | **SÍ** | 1.1384 | **Reproducido** (Magnitud 113.8%) |
| **`tda_beta_0`** | +0.3609 | **+0.3303** | **SÍ** | 0.9152 | **Reproducido** (Magnitud 91.5%) |

### Hallazgos Clave de Reproducibilidad:
1. **100% Reproducibilidad Direccional**: Los 4 descriptores conservaron exactamente el mismo signo y patrón fisiológico-estructural observado durante Development.
2. **Estabilidad de Magnitud de Efecto**: Los tamaños de efecto en Holdout se mantuvieron entre el 91.5% y el 116.8% de los valores observados en Development, demostrando la ausencia total de sobreajuste (overfitting).
3. **Significancia Estadística Robusta**: Todas las diferencias pareadas mantuvieron p-valores extremadamente significativos ($p < 0.004$ en test de Student y $p < 10^{-5}$ en Wilcoxon), confirmando la presencia de diferencias estructurales intrínsecas reproducibles entre el hueso trabecular crestal y basal.

---

## 6. REGISTRO EN EL EXPERIMENT LEDGER

La entrada `EXP-F11-001` fue agregada exitosamente a `data/processed/experiment_ledger.csv`:

```csv
exp_id,date,dataset,preprocessing,feature_set,model,split,target,auc,status,reason
EXP-F11-001,2026-09-24,Holdout Included (193 img / 162 pts),Pipeline-A/Pipeline-B (v1.0 Frozen),SET_G_LOCKED (D0, DM, Delta_alpha, beta0),One-Time Out-of-Sample Holdout Evaluation,Holdout Only (Firewall Cleared),Paired Intra-patient Structural Contrast Generalizability,N/A,VALID,One-time holdout evaluation completed with zero parameter tuning or post-hoc adjustments.
```

---

## 7. VERDICTO FINAL DE LA FASE 11

```text
VERDICT: PASS
REPRODUCIBILITY: 100% (4/4 descriptors reproduced out-of-sample)
DATA LEAKAGE: ZERO
POST-HOC MANIPULATION: ZERO
```

La Fase 11 queda **OFICIALMENTE CERRADA CON ÉXITO**. El pipeline metodológico de caracterización matemática de estructura trabecular ha demostrado validez out-of-sample en un conjunto de pacientes independientes no vistos durante el desarrollo.

---

## 8. RESTRICCIÓN DE FINALIZACIÓN

Como se especificó en las directrices de la Fase 11, la ejecución se detiene aquí. **NO se inicia la Fase 12**.
