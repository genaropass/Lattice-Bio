# FASE 10 — FINAL PIPELINE & MODEL LOCK

## 1. Scope

El objetivo de la **Fase 10** es congelar formal y definitivamente el **pipeline metodológico metrológico y estructural** que será evaluado por única vez en la Fase 11 sobre el conjunto congelado Holdout, sin haber realizado ninguna observación ni inferencia sobre dicho conjunto.

Pregunta metodológica congelada para el estudio:
> **¿Los descriptores matemáticos proporcionan mediciones reproducibles de diferencias estructurales entre regiones anatómicas definidas independientemente en radiografías dentales 2D?**

---

## 2. Dataset

- **Dataset de Desarrollo (Development)**: Exclusivamente las 657 imágenes pertenecientes al split `Development` con `inclusion_status == "INCLUDED"` del dataset `Periodontal` intraoral (Khatibi et al.).
- **Unidad de Análisis**: **`PATIENT`** (`patient_id` — 643 pacientes únicos).
- **Holdout Set**: 162 pacientes / 193 imágenes. Totalmente inalterado e intocado (SHA256: `85e3a856e5a1334d53084f242fff50a92c1c662fe1d4c8797053261578d2b335`).

---

## 3. ROI Definition (Congelada)

- **ROI A — Cresta Alveolar Interdental (`crest`)**:
  - Coordenadas relativas centroides: $(x, y) = (0.50 \cdot w, 0.45 \cdot h)$
  - Dimensiones: $64 \times 64$ píxeles
  - Definición: Región anatómico-geométrica de referencia intra-paciente en hueso trabecular alveolar coronal.
- **ROI B — Hueso Trabecular Basal (`basal`)**:
  - Coordenadas relativas centroides: $(x, y) = (0.50 \cdot w, 0.80 \cdot h)$
  - Dimensiones: $64 \times 64$ píxeles
  - Definición: Región anatómico-geométrica de referencia intra-paciente en hueso trabecular basal mandibular.

---

## 4. Preprocessing (Congelado)

### Pipeline-A (Escala de Grises Preservada / 2.5D)
- **Uso**: Descriptor de rugosidad de superficie $D_M$.
- **Parámetros**: Re-muestreo espacial Lanczos4 ($\sim 35\ \mu\text{m/px}$ nominal) + Normalización MinMax $[0, 1]$. Sin ecualización CLAHE ni binarización.

### Pipeline-B (Binarización Adaptativa / Grilla Estandarizada)
- **Uso**: Descriptores binarios y topológicos $D_0, \Delta\alpha, \beta_0$.
- **Parámetros**: Re-muestreo Lanczos4 ($\sim 35\ \mu\text{m/px}$ nominal) + CLAHE (clip limit $2.5$, grid $8 \times 8$) + Binarización adaptativa local de Sauvola (ventana $15$, $k=0.2$).

---

## 5. Locked Feature Set (`SET_G_LOCKED`)

Se congela el conjunto candidate definitivo de 4 descriptores matemáticos primarios:

1. **`fractal_D0`** (Dimensión fractal de Hausdorff-Besicovitch por box-counting en `Pipeline-B`).
2. **`minkowski_dimension`** (Dimensión de cubierta de superficie 2.5D en `Pipeline-A`).
3. **`multifractal_delta_alpha`** (Ancho de espectro de singularidad multifractal en `Pipeline-B`).
4. **`tda_beta_0`** (Número de Betti 0: componentes conexas trabeculares en `Pipeline-B`).

---

## 6. Excluded Features (Exclusiones Fundamentadas)

1. **`lacunarity_mean`**: Excluida metodológicamente por colinealidad y redundancia extrema con $D_0$ ($\rho = -0.9979, VIF > 380$). Su eliminación purga la colinealidad a $VIF < 3.5$.
2. **`tda_beta_1`**: Excluida provisionalmente por inestabilidad de binarización Sauvola y menor significación en la prueba de permutación de F8 ($p_{\text{perm}} = 0.016$).

---

## 7. Relative Index $R_{\text{trab}}$

- Se define el índice relativo intra-paciente/intra-imagen:
  $$R_{\text{trab}} = \frac{\text{Descriptor}(\text{Cresta})}{\text{Descriptor}(\text{Basal})}$$
  para cada uno de los 4 descriptores congelados.
- **Naturaleza**: Transformación relativa estandarizada intra-paciente, no constituyendo 4 descriptores independientes adicionales.

---

## 8. Statistical Protocol

- **Unidad Estadística**: **`PATIENT`** (`patient_id`).
- **Remuestreo Bootstrap**: $N = 1,000$ iteraciones aleatorias con reemplazo agrupadas estrictamente por paciente.
- **Nivel de Confianza**: Intervalos de confianza del 95% ($2.5\%$ y $97.5\%$ percentiles bootstrap).
- **Semilla Aleatoria Congelada**: `seed = 42`.
- **Politica de Outliers**: Retener todas las observaciones válidas en escala natural. Reportar mediana, IQR y percentiles. Sin trinchado ni winsorización arbitraria.
- **Politica de Escalado**: Mantener las variables en sus unidades matemáticas naturales sin z-score ni min-max global entre pacientes.

---

## 9. Primary Endpoint

- **Endpoint Primario**: El contraste estandarizado pareado intra-paciente ($Cohen's\ d_z$ e intervalos de confianza bootstrap del 95%) entre la ROI Cresta y la ROI Basal sobre el conjunto congelado `SET_G_LOCKED = {D0, DM, Delta_alpha, beta0}`.

---

## 10. Secondary Endpoints

1. Comportamiento pareado individual de cada descriptor ($D_0, D_M, \Delta\alpha, \beta_0$).
2. Distribución y dispersión de los índices relativos $R_{\text{trab}}$.
3. Estructura de correlaciones de Spearman entre los 4 descriptores congelados.

---

## 11. Holdout Firewall Rule

> **"After F10 lock, no methodological parameter, preprocessing choice, feature definition, exclusion criterion, statistical endpoint, or model configuration may be changed based on any observation from the holdout in F11."**

Si la evaluación de Fase 11 produce un resultado inesperado, el protocolo prohíbe reajustar hiperparámetros o modificar el pipeline para volver a evaluar el Holdout.

---

## 12. Reproducibility

- **Configuración Congelada**: [final_pipeline_lock_v1.json](file:///e:/Genaro/Desktop/Nueva%20carpeta/configs/final_pipeline_lock_v1.json)
- **Script de Ejecución**: [run_final_pipeline_lock.py](file:///e:/Genaro/Desktop/Nueva%20carpeta/scripts/run_final_pipeline_lock.py)
- **Script de Auditoría Automática**: [audit_final_pipeline_lock.py](file:///e:/Genaro/Desktop/Nueva%20carpeta/scripts/audit_final_pipeline_lock.py)
- **Registro en Experiment Ledger**: Entrada `EXP-F10-001` agregada en `data/processed/experiment_ledger.csv`.

---

## 13. Limitations Documentadas

1. **Escala Digital Nominal**: La resolución `35 μm/px` se declara como *"Standardized Digital Resampling Grid Target"* bajo el supuesto de $150$ DPI nominales, no como escala métrica física calibrada.
2. **Ausencia de Target Clínico**: El estudio es metrológico y descriptivo de estructura trabecular en radiografías periapicales intraorales; no constituye un modelo de clasificación ni diagnóstico clínico.

---

## 14. Final Lock Status

### Estado Oficial: **`LOCKED_WITH_LIMITATIONS`**

El pipeline metodológico queda oficialmente congelado y blindado para la evaluación única sobre el conjunto Holdout en la **Fase 11**.
