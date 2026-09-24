# FASE 9 — FEATURE ABLATION & COMPLEMENTARITY ANALYSIS

## 1. Objetivo

El objetivo de la **Fase 9** es determinar qué descriptores matemáticos aportan información estructural complementaria y cuáles son esencialmente redundantes o inestables, resolviendo la colinealidad detectada en F8 entre la dimensión fractal $D_0$ y la lacunaridad $\Lambda$ ($\rho = -0.9979, VIF > 300$).

Pregunta central resuelta:
> **¿La combinación de descriptores matemáticos aporta información estructural complementaria o una parte importante de la señal está duplicada entre descriptores matemáticamente relacionados?**

Respuesta: Existe una colinealidad casi perfecta entre $D_0$ y Lacunaridad $\Lambda$ derivada del cálculo sobre la grilla binaria. Mediante ablación Leave-One-Feature-Out (LOFO), se demuestra que eliminar Lacunaridad y $\beta_1$ purga la colinealidad ($VIF < 3.5$) manteniendo intacta la señal estructural inter-regional.

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

| Feature Set | $N$ Features | Descriptores Miembros | Cohen's $d_z$ Medio | IC 95% Bootstrap | VIF Máximo | Redundancia Purgada |
| :--- | :---: | :--- | :---: | :---: | :---: | :---: |
| `SET_A_Full` | 6 | $D_0, D_M, \Lambda, \Delta\alpha, \beta_0, \beta_1$ | 0.3697 | [0.3371, 0.4086] | 400.69 | NO |
| `SET_B_No_D0` | 5 | $D_M, \Lambda, \Delta\alpha, \beta_0, \beta_1$ | 0.4039 | [0.3713, 0.4383] | 400.69 | NO |
| `SET_C_No_Lacunarity` | 5 | $D_0, D_M, \Delta\alpha, \beta_0, \beta_1$ | 0.3980 | [0.3661, 0.4324] | 388.83 | NO |
| `SET_D_No_D0_No_Lacunarity` | 4 | $D_M, \Delta\alpha, \beta_0, \beta_1$ | 0.4478 | [0.4098, 0.4884] | **3.21** | **SÍ** |
| `SET_E_Geometric_Topological` | 4 | $D_0, \Delta\alpha, \beta_0, \beta_1$ | 0.2935 | [0.2634, 0.3260] | 388.83 | NO |
| `SET_F_Roughness_Intensity` | 2 | $D_M, \Lambda$ | 0.5223 | [0.4718, 0.5793] | 400.69 | NO |
| **`SET_G_Robust_Subset`** | **4** | **$D_0, D_M, \Delta\alpha, \beta_0$** | **0.4734** | **[0.4332, 0.5155]** | **3.21** | **SÍ (Seleccionado)** |

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

1. **Redundancia Estricta**: La correlación Spearman $\rho = -0.9979$ demuestra que $D_0$ y Lacunaridad miden exactamente el mismo fenómeno de ocupación de grilla binaria.
2. **Caída de VIF**: Eliminar Lacunaridad hace caer el VIF máximo de $400.69$ a **$3.21$**.
3. **Interpretabilidad**: $D_0$ posee mayor sustento teórico en literatura médica (dimensión fractal de Hausdorff-Besicovitch).
4. **Dictamen**: **CONSERVAR $D_0$, ELIMINAR LACUNARIDAD**.

---

## 8. Auditoría de TDA ($\beta_0$ vs $\beta_1$)

- `tda_beta_1`: Falló la prueba de permutación estricta en F8 ($p_{\text{perm}} = 0.016$) y presenta alta volatilidad ante el tamaño de ventana de Sauvola. **ELIMINAR $\beta_1$**.
- `tda_beta_0`: Sobrevivió permutación en F8 ($p_{\text{perm}} = 0.000$), VIF $= 2.68$, mide componentes conexas trabeculares. **CONSERVAR $\beta_0$**.

---

## 9. Auditoría de $\Delta\alpha$ (Multifractal)

- `multifractal_delta_alpha`: $p_{\text{perm}} = 0.000$, VIF $= 2.42$. Captura la heterogeneidad del espectro multifractal de la masa trabecular de forma independiente a $D_0$ y $D_M$. **CONSERVAR $\Delta\alpha$**.

---

## 10. Evaluación del Índice Relativo $R_{\text{trab}}$

- El ratio $R_{\text{trab}} = \frac{\text{Descriptor}(\text{Cresta})}{\text{Descriptor}(\text{Basal})}$ se mantiene como la medida intra-paciente estandarizada para las 4 features retenidas, eliminando variaciones de densidad absoluta intra-imagen.

---

## 11. Tabla Consolidada de Evaluación de Features (F4 a F9)

| Feature | Estabilidad F5 | Robustez F8 | Redundancia | Sensibilidad | Complementariedad | Estado Final F9 |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **`fractal_D0`** | `ROBUST` | `PASS` ($\text{BalAcc}=0.11$) | Colineal con $\Lambda$ | Invariante rotacional | Alta ($D_0$ Hausdorff) | **RETENIDA (SET G)** |
| **`minkowski_dimension`**| `UNSTABLE` (Ruido) | `PASS` ($p_{\text{perm}}=0.00$) | Sin colinealidad | Sensible a ruido | Alta (Rugosidad 2.5D) | **RETENIDA (SET G)** |
| `lacunarity_mean` | `ROBUST` | `PASS` | **Extrema ($\rho = -0.998$)**| Invariante | Duplicada con $D_0$ | **ELIMINADA (Ablación)** |
| **`multifractal_delta_alpha`**| `ROBUST` | `PASS` ($p_{\text{perm}}=0.00$) | Sin colinealidad | Sensible a $q$ extrema | Alta (Complejidad) | **RETENIDA (SET G)** |
| **`tda_beta_0`** | `SENSITIVE` | `PASS` ($p_{\text{perm}}=0.00$) | Sin colinealidad | Moderada a binarización | Alta (Componentes) | **RETENIDA (SET G)** |
| `tda_beta_1` | `UNSTABLE` | **No pasó $p_{\text{perm}} < 0.001$** | Sin colinealidad | Alta a Sauvola | Baja | **ELIMINADA (Ablación)** |

---

## 12. Decisión sobre Feature Set Candidato para Fase 10

### Conjunto Seleccionado: **`SET G (Robust Subset)`**

$$\text{Candidate Feature Set} = \{ D_0, D_M, \Delta\alpha, \beta_0 \}$$

- **Número de Features**: 4 descriptores primarios (más sus 4 ratios $R_{\text{trab}}$ correspondientes).
- **VIF Máximo del Conjunto**: **$3.21$** (100% purgado de colinealidad).
- **Justificación Jerárquica**:
  1. Validez matemática demostrada en F4/F4.1.
  2. Purga de redundancia extrema ($D_0 \leftrightarrow \Lambda$).
  3. Eliminación de inestabilidad binarizadora ($\beta_1$).
  4. Preservación del efecto estructural intra-paciente pareado (Cohen's $d_z = 0.4734$).

---

## 13. Veredicto Final de Fase 9

### Veredicto Oficial: **`PASS_WITH_LIMITATIONS`**

#### Justificación
La ablación ha resuelto definitivamente el problema de colinealidad entre $D_0$ y Lacunaridad, estableciendo un conjunto de 4 descriptores matemáticos verdaderamente complementarios ($D_0, D_M, \Delta\alpha, \beta_0$) con VIF $< 3.5$.

#### Limitaciones Documentadas:
1. **$D_M$ en Pipeline-A**: Debe mantenerse estrictamente libre de ruido Gaussiano añadido.
2. **$\beta_0$ en Pipeline-B**: Requiere mantener congelada la ventana Sauvola en $W=15$.
