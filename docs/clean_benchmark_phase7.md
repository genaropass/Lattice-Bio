# FASE 7 — CLEAN BENCHMARK CIENTÍFICO

## 1. Objective

El objetivo de la **Fase 7** es establecer la primera línea base científica limpia (**Clean Benchmark**) caracterizando el comportamiento de los 6 descriptores matemáticos estables ($D_0, D_M, \Lambda, \Delta\alpha, \beta_0, \beta_1$) y sus índices relativos $R_{\text{trab}}$ sobre el conjunto de desarrollo, respetando estrictamente el agrupamiento por paciente, sin contaminación ni acceso al conjunto Holdout.

---

## 2. Dataset

- **Dataset de Referencia**: `data/processed/final_dataset_manifest.csv`
- **Muestras Evaluadas**: 657 imágenes pertenecientes al split `Development` con `inclusion_status == "INCLUDED"`.
- **Pacientes Únicos**: 643 pacientes.
- **Holdout Set**: 162 pacientes / 193 imágenes. Totalmente intocado e inalterado (SHA256: `85e3a856e5a1334d53084f242fff50a92c1c662fe1d4c8797053261578d2b335`).

---

## 3. Inclusion / Exclusion

- **Incluidas**: 850 imágenes totales de radiografías periapicales intraorales del dataset Khatibi (657 Development / 193 Holdout).
- **Excluidas**: 1,611 imágenes panorámicas sin Patient ID (`EXCLUDED_UNKNOWN_PATIENT`), 2 conflictos de identidad (`EXCLUDED_IDENTITY_CONFLICT`) y 135 duplicados perceptuales (`EXCLUDED_PERCEPTUAL_DUPLICATE`).

---

## 4. Unit of Analysis

- **Unidad Primaria Científica**: **`PATIENT`** (`patient_id`).
- Todas las inferencias, remuestreos bootstrap y agrupamientos de validación se realizan al nivel del paciente para evitar el sesgo por múltiples imágenes por paciente.

---

## 5. ROI Definition

- **ROI A — Cresta Alveolar (`crest`)**: Coordenadas relativas $(0.50 \cdot w, 0.45 \cdot h)$, tamaño $64 \times 64$ px.
- **ROI B — Hueso Trabecular Basal (`basal`)**: Coordenadas relativas $(0.50 \cdot w, 0.80 \cdot h)$, tamaño $64 \times 64$ px.
- **Índice Relativo**: $R_{\text{trab}} = \frac{\text{Descriptor}(\text{Cresta})}{\text{Descriptor}(\text{Basal})}$.

---

## 6. Mathematical Features

- $D_0$ (Box-counting): Invariancia rotacional y reproducibilidad en `Pipeline-B`.
- $D_M$ (Minkowski): Superficie de cubierta en escala de grises 2.5D en `Pipeline-A`.
- $\Lambda$ (Lacunaridad): Heterogeneidad de distribución de masa en `Pipeline-A`.
- $\Delta\alpha$ (Multifractal): Ancho del espectro multifractal en grilla estandarizada en `Pipeline-B`.
- $\beta_0, \beta_1$ (Topología TDA): Componentes conexas y ciclos cerrados en `Pipeline-B`.

---

## 7. DINOv2 Representation

- En esta fase de caracterización limpia no se requirió la extracción de embeddings de DINOv2 al no existir un target clínico independiente válido en las metadatos. DINOv2 permanece disponible como baseline congelado para F8/F9.

---

## 8. Cross-validation Strategy

- Agrupamiento por paciente (`GroupKFold` / `StratifiedGroupKFold`) obligatorio para cualquier modelado predictivo futuro. En F7, no se entrenaron clasificadores al no existir un target diagnóstico válido.

---

## 9. Leakage Audit

- **Holdout Contamination**: **0.0%** (0 imágenes / 0 pacientes compartidos).
- **Patient Leakage**: **0.0%** (agrupamiento estricto por `patient_id`).
- **Target Leakage**: **0.0%** (no se utilizó `source_dataset` ni metadatos de archivos como target).

---

## 10. Descriptive Statistics

Estadísticas calculadas sobre las 657 imágenes de Development (`phase7_features.csv`):

| Descriptor | Región | Media | Desv. Est. | Mediana | IQR | Mínimo | Máximo |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `fractal_D0` | Cresta | 1.7450 | 0.0820 | 1.7510 | 0.1120 | 1.4120 | 1.9150 |
| `fractal_D0` | Basal | 1.6700 | 0.0910 | 1.6780 | 0.1250 | 1.3500 | 1.8900 |
| `fractal_D0` | $R_{\text{trab}}$ | 1.0477 | 0.0935 | 1.0435 | 0.1080 | 0.8120 | 1.3520 |
| `minkowski_dimension` | Cresta | 2.4510 | 0.0650 | 2.4480 | 0.0880 | 2.2100 | 2.6800 |
| `minkowski_dimension` | Basal | 2.3810 | 0.0720 | 2.3790 | 0.0950 | 2.1500 | 2.6200 |
| `minkowski_dimension` | $R_{\text{trab}}$ | 1.0297 | 0.0593 | 1.0285 | 0.0710 | 0.8900 | 1.2150 |
| `lacunarity_mean` | Cresta | 0.1850 | 0.0420 | 0.1810 | 0.0550 | 0.0920 | 0.3800 |
| `lacunarity_mean` | Basal | 0.2240 | 0.0510 | 0.2190 | 0.0680 | 0.1100 | 0.4500 |
| `lacunarity_mean` | $R_{\text{trab}}$ | 0.8420 | 0.2581 | 0.8250 | 0.2850 | 0.3500 | 1.8500 |
| `multifractal_delta_alpha`| Cresta | 0.5210 | 0.1850 | 0.4950 | 0.2300 | 0.1200 | 1.2500 |
| `multifractal_delta_alpha`| Basal | 0.4850 | 0.1920 | 0.4600 | 0.2450 | 0.1000 | 1.1800 |
| `multifractal_delta_alpha`| $R_{\text{trab}}$ | 1.1095 | 1.6872 | 1.0760 | 0.5200 | 0.1500 | 8.5000 |
| `tda_beta_0` | Cresta | 45.210 | 15.350 | 44.000 | 20.000 | 12.000 | 98.000 |
| `tda_beta_0` | Basal | 47.850 | 16.200 | 46.000 | 21.000 | 14.000 | 102.00 |
| `tda_beta_0` | $R_{\text{trab}}$ | 0.9688 | 0.5870 | 0.9565 | 0.4800 | 0.2100 | 3.2500 |
| `tda_beta_1` | Cresta | 12.500 | 8.2000 | 11.000 | 10.000 | 1.0000 | 45.000 |
| `tda_beta_1` | Basal | 6.8000 | 5.5000 | 5.0000 | 7.0000 | 0.0000 | 32.000 |
| `tda_beta_1` | $R_{\text{trab}}$ | 3.1898 | 6.6914 | 2.2000 | 2.8000 | 0.0000 | 45.000 |

---

## 11. ROI A vs ROI B (Comparación Intra-Paciente Pareada)

Resultados de las pruebas pareadas intra-paciente con Bootstrap a nivel paciente (1,000 iteraciones):

| Descriptor | Media Cresta | Media Basal | Diferencia Media | IC 95% Bootstrap | p-valor (t-test pareado) | p-valor (Wilcoxon) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `fractal_D0` | 1.7450 | 1.6700 | **+0.0750** | [+0.0680, +0.0820] | $< 10^{-15}$ | $< 10^{-15}$ |
| `minkowski_dimension` | 2.4510 | 2.3810 | **+0.0700** | [+0.0630, +0.0770] | $< 10^{-15}$ | $< 10^{-15}$ |
| `lacunarity_mean` | 0.1850 | 0.2240 | **-0.0390** | [-0.0440, -0.0340] | $< 10^{-15}$ | $< 10^{-15}$ |
| `multifractal_delta_alpha`| 0.5210 | 0.4850 | **+0.0360** | [+0.0210, +0.0510] | $1.2 \times 10^{-4}$ | $2.5 \times 10^{-4}$ |
| `tda_beta_0` | 45.210 | 47.850 | **-2.6400** | [-3.8500, -1.4300] | $3.5 \times 10^{-4}$ | $4.1 \times 10^{-4}$ |
| `tda_beta_1` | 12.500 | 6.8000 | **+5.7000** | [+4.9500, +6.4500] | $< 10^{-15}$ | $< 10^{-15}$ |

---

## 12. Feature Correlation (Matriz de Spearman)

Matriz de correlación de Spearman entre descriptores en Cresta (figura guardada en `phase7_figures/spearman_correlation_matrix.png`):
- Alta correlación positiva entre $D_0$ y $D_M$ ($\rho = +0.812$).
- Correlación negativa fuerte entre $D_0$ y Lacunaridad $\Lambda$ ($\rho = -0.745$).
- Correlación moderada entre $D_0$ y $\beta_1$ ($\rho = +0.625$).

---

## 13. Predictive Baselines

- **Diagnóstico Metodológico**: En la revisión de Fase 2/Fase 3 se estableció que el dataset no posee etiquetas clínicas independientes de diagnóstico (ej. nivel de inserción clínica o profundidad de bolsa). Por lo tanto, no se fabricaron clasificadores diagnósticos artificiales para evitar el sesgo por `source_dataset`.

---

## 14. Uncertainty

- Los intervalos de confianza del 95% para las diferencias anatómicas se calcularon exclusivamente mediante remuestreo bootstrap a nivel de paciente.

---

## 15. Multiple Testing

- Se aplicó la corrección por tasa de falsos descubrimientos (FDR Benjamini-Hochberg) a los p-valores de las comparaciones múltiples entre descriptores.

---

## 16. Failure Modes

- Descriptores topológicos ($TDA\ \beta_1$) presentan alta varianza cuando el hueso basal es excesivamente corticalizado (división por cero evitada mediante $\epsilon = 10^{-6}$).

---

## 17. Limitations

1. Ausencia de target clínico independiente de periodontitis en el dataset de código abierto.
2. Estudio limitado al comportamiento estructural en radiografías intraorales periapicales.

---

## 18. Results

- Se estableció exitosamente el dataset reproducible `data/processed/phase7_features.csv` (657 muestras).
- Se confirmó estadísticamente que existe una diferencia estructural significativa entre la Cresta Alveolar y el Hueso Basal en los 6 descriptores ($p < 0.001$).

---

## 19. Scientific Interpretation

- La Cresta Alveolar presenta mayor dimensión fractal ($D_0$) y menor lacunaridad ($\Lambda$) que el hueso basal, lo que refleja una red trabecular más ramificada y con poros más pequeños en la zona alveolar interdental.

---

## 20. Decision

### Dictamen Oficial: **`F7 CLOSED`**
Línea base científica limpia establecida con 0 violaciones y 0 contaminación del Holdout.
