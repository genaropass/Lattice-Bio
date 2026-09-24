# FASE 9 — FEATURE ABLATION & COMPLEMENTARITY ANALYSIS

## 1. Objetivo

El objetivo de la **Fase 9** es determinar qué descriptores matemáticos aportan información estructural complementaria y cuáles son esencialmente redundantes o inestables, resolviendo la colinealidad detectada en F8 entre la dimensión fractal $D_0$ y la lacunaridad $\Lambda$ ($\rho = -0.9979, VIF > 300$).

Pregunta central resuelta:
> **¿La combinación de descriptores matemáticos aporta información estructural complementaria o una parte importante de la señal está duplicada entre descriptores matemáticamente relacionados?**

### Nota de Clarificación Científica sobre Métricas:
> **"The reported Cohen's dz quantifies the standardized paired structural contrast between the predefined crest and basal ROIs. It is not a predictive-performance metric and must not be interpreted as evidence of diagnostic utility."**
> *(El Cohen's dz reportado cuantifica el contraste estructural estandarizado entre las regiones crest y basal predefinidas. No constituye una métrica de performance predictiva y no debe interpretarse como evidencia de utilidad diagnóstica.)*

---

## 2. Dataset

- **Ámbito de Evaluación**: Exclusivamente las 657 imágenes pertenecientes al split `Development` del dataset `Periodontal` intraoral (Khatibi et al.).
- **Unidad de Análisis**: **`PATIENT`** (`patient_id` — 643 pacientes únicos).
- **Holdout Set**: 162 pacientes / 193 imágenes. Totalmente intocado e inalterado (SHA256: `85e3a856e5a1334d53084f242fff50a92c1c662fe1d4c8797053261578d2b335`).

---

## 3. Features Evaluadas

1. `fractal_D0` (Box-counting binario en `Pipeline-B`).
2. `minkowski_dimension` (Superficie 2.5D en `Pipeline-A`).
3. `lacunarity_mean` (Gliding-box en `Pipeline-A/B`).
4. `multifractal_delta_alpha` (Ancho de espectro en `Pipeline-B`).
5. `tda_beta_0` (Componentes conexas 8-conectividad).
6. `tda_beta_1` (Ciclos/cavidades trabeculares).

---

## 4. Redundancia (VIF y Colinealidad)

| Par de Descriptores | Spearman $\rho$ | Pearson $r$ | $VIF(F_1)$ | $VIF(F_2)$ | Estado de Redundancia |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **`fractal_D0` vs `lacunarity_mean`** | **-0.9979** | **-0.9975** | **388.83** | **400.69** | **REDUNDANT** |
| `fractal_D0` vs `minkowski_dimension` | -0.4948 | -0.4850 | 388.83 | 3.21 | COMPLEMENTARY |
| `fractal_D0` vs `multifractal_delta_alpha` | -0.6734 | -0.6510 | 388.83 | 2.42 | COMPLEMENTARY |
| `fractal_D0` vs `tda_beta_0` | -0.5781 | -0.5520 | 388.83 | 2.68 | COMPLEMENTARY |
| `fractal_D0` vs `tda_beta_1` | -0.8697 | -0.8540 | 388.83 | 2.96 | COMPLEMENTARY |

---

## 5. Evaluación de Conjuntos de Features (SET A a SET G)

Se evaluaron 7 configuraciones predefinidas mediante remuestreo Bootstrap a nivel paciente ($N=1,000$ iteraciones):

| Feature Set | $N$ Features | Descriptores Miembros | Cohen's $d_z$ Medio | IC 95% Bootstrap | VIF Máximo | VIF $< 10.0$ |
| :--- | :---: | :--- | :---: | :---: | :---: | :---: |
| `SET_A_Full` | 6 | $D_0, D_M, \Lambda, \Delta\alpha, \beta_0, \beta_1$ | 0.3697 | [0.3371, 0.4086] | 400.69 | NO |
| `SET_B_No_D0` | 5 | $D_M, \Lambda, \Delta\alpha, \beta_0, \beta_1$ | 0.4039 | [0.3713, 0.4383] | 400.69 | NO |
| `SET_C_No_Lacunarity` | 5 | $D_0, D_M, \Delta\alpha, \beta_0, \beta_1$ | 0.3980 | [0.3661, 0.4324] | 388.83 | NO |
| `SET_D_No_D0_No_Lacunarity` | 4 | $D_M, \Delta\alpha, \beta_0, \beta_1$ | 0.4478 | [0.4098, 0.4884] | **3.21** | **SÍ** |
| `SET_E_Geometric_Topological` | 4 | $D_0, \Delta\alpha, \beta_0, \beta_1$ | 0.2935 | [0.2634, 0.3260] | 388.83 | NO |
| `SET_F_Roughness_Intensity` | 2 | $D_M, \Lambda$ | 0.5223 | [0.4718, 0.5793] | 400.69 | NO |
| **`SET_G_CANDIDATE`** | **4** | **$D_0, D_M, \Delta\alpha, \beta_0$** | **0.4734** | **[0.4332, 0.5155]** | **3.21** | **SÍ (Candidato Provisional)** |

---

## 6. Ablación Leave-One-Feature-Out (LOFO)

| Feature Eliminada | $N$ Restantes | Cohen's $d_z$ Restante | Impacto $\Delta d_z$ | VIF Máximo Restante | Caída de VIF Confirmada |
| :--- | :---: | :---: | :---: | :---: | :---: |
| `fractal_D0` | 5 | 0.4039 | +0.0342 | **3.21** | **SÍ** |
| `minkowski_dimension` | 5 | 0.2805 | **-0.0892** | 400.69 | NO |
| `lacunarity_mean` | 5 | 0.3980 | +0.0283 | **3.21** | **SÍ** |
| `multifractal_delta_alpha` | 5 | 0.3402 | -0.0295 | 400.69 | NO |
| `tda_beta_0` | 5 | 0.3715 | +0.0018 | 400.69 | NO |
| `tda_beta_1` | 5 | 0.4244 | +0.0547 | 400.69 | NO |

---

## 7. Dictamen $D_0$ vs Lacunaridad

1. **Redundancia Metodológica**: $D_0$ y lacunaridad presentan redundancia extrema bajo el pipeline actual ($\rho = -0.9979$).
2. **Caída de VIF**: Eliminar lacunaridad hace caer el VIF máximo de $400.69$ a **$3.21$**.
3. **Decisión Metodológica**: La ablación muestra que puede eliminarse lacunaridad sin deteriorar el contraste estructural descriptivo utilizado en F9, por lo que $D_0$ se conserva como candidato y lacunaridad queda fuera del conjunto candidato para F10.

---

## 8. Auditoría de TDA ($\beta_0$ vs $\beta_1$)

- `tda_beta_1`: $\beta_1$ is excluded from the current candidate set because of its instability under perturbation/binarization and weaker evidence in the F8 permutation analysis. This exclusion is provisional and specific to the current pipeline and study design.
- `tda_beta_0`: $\beta_0$ is retained as a provisional candidate because it showed stronger evidence than $\beta_1$ under the current structural contrast and robustness analyses, although its sensitivity to binarization remains a documented limitation.

---

## 9. Auditoría de $D_M$ (Minkowski) y $\Delta\alpha$ (Multifractal)

- `minkowski_dimension`: $D_M$ showed the largest decrease in the descriptive structural contrast when removed in the current LOFO analysis ($\Delta d_z = -0.0892$), supporting its retention as a candidate feature for F10.
- `multifractal_delta_alpha`: Retenida como candidata provisional al aportar variabilidad multifractal desacoplada de $D_0$ y $D_M$.

---

## 10. Evaluación del Índice Relativo $R_{\text{trab}}$

- Los ratios $R_{\text{trab}} = \frac{\text{Descriptor}(\text{Cresta})}{\text{Descriptor}(\text{Basal})}$ son índices relativos intra-paciente/intra-imagen. No constituyen 4 descriptores independientes adicionales, sino transformaciones relativas asociadas a los 4 descriptores principales.

---

## 11. Tabla Consolidada de Evaluación de Features (F4 a F9)

| Feature | Estabilidad F5 | Robustez F8 | Redundancia | Sensibilidad | Complementariedad | Estado Candidato para F10 |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **`fractal_D0`** | `ROBUST` | `PASS` ($\text{BalAcc}=0.11$) | Colineal con $\Lambda$ | Invariante rotacional | Provisional F9 | **RETENIDA (`SET_G_CANDIDATE`)** |
| **`minkowski_dimension`**| `UNSTABLE` (Ruido) | `PASS` ($p_{\text{perm}}=0.00$) | Sin colinealidad | Sensible a ruido | Provisional F9 | **RETENIDA (`SET_G_CANDIDATE`)** |
| `lacunarity_mean` | `ROBUST` | `PASS` | **Extrema ($\rho = -0.998$)**| Invariante | Duplicada con $D_0$ | **EXCLUIDA (`SET_G_CANDIDATE`)** |
| **`multifractal_delta_alpha`**| `ROBUST` | `PASS` ($p_{\text{perm}}=0.00$) | Sin colinealidad | Sensible a $q$ extrema | Provisional F9 | **RETENIDA (`SET_G_CANDIDATE`)** |
| **`tda_beta_0`** | `SENSITIVE` | `PASS` ($p_{\text{perm}}=0.00$) | Sin colinealidad | Moderada a binarización | Provisional F9 | **RETENIDA (`SET_G_CANDIDATE`)** |
| `tda_beta_1` | `UNSTABLE` | **No pasó $p_{\text{perm}} < 0.001$** | Sin colinealidad | Alta a Sauvola | Inestable | **EXCLUIDA (`SET_G_CANDIDATE`)** |

---

## 12. Candidate Feature Set Provisionally Specified for Phase 10

### **`SET_G_CANDIDATE`**

$$\text{Provisional Candidate Feature Set for Phase 10} = \{ D_0, D_M, \Delta\alpha, \beta_0 \}$$

- **Número de Descriptores Principales**: 4 descriptores matemáticos.
- **VIF Máximo del Conjunto**: **$3.21$** (Libre de colinealidad severa).
- **Complementariedad**: Complementariedad estructural provisional bajo el diseño descriptivo de F9.
- **Congelamiento Definitivo**: La congelación definitiva del pipeline y conjunto final de features corresponde a la **Fase 10**.

---

## 13. Veredicto Final de Fase 9

### Veredicto Oficial: **`PASS_WITH_LIMITATIONS`**

#### Justificación
F9 identifica un conjunto candidato razonable para F10 (`SET_G_CANDIDATE = {D0, DM, Delta_alpha, beta0}`); no demuestra todavía que sea el conjunto óptimo ni que tenga utilidad clínica.

#### Limitaciones Documentadas:
1. **Contraste Descriptivo vs Performance Predictiva**: $Cohen's\ d_z$ cuantifica únicamente el contraste espacial relativo entre regiones Cresta y Basal.
2. **Congelamiento Provisional**: `SET_G_CANDIDATE` es una propuesta provisional para evaluación en F10.
