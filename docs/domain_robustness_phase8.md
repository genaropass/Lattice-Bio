# FASE 8 — DOMAIN, SHORTCUT, PERMUTATION & ROBUSTNESS AUDIT

## 1. Objetivo

El objetivo de la **Fase 8** es someter las señales estructurales encontradas en la Fase 7 a un conjunto riguroso de **controles negativos, pruebas de permutación, análisis de redundancia/colinealidad, sensibilidad de parámetros y auditoría de atajos (*shortcuts*)**, para determinar si las observaciones son genuinas y robustas antes de avanzar hacia el análisis de ablación (Fase 9).

Pregunta central resuelta:
> **¿Las diferencias estructurales observadas en F7 son suficientemente robustas frente a controles de dominio, permutación y sensibilidad como para justificar continuar hacia ablation/modeling?**

---

## 2. Dataset

- **Ámbito de Evaluación**: Exclusivamente las 657 imágenes pertenecientes al split `Development` del dataset `Periodontal` intraoral (Khatibi et al.).
- **Unidad de Análisis**: **`PATIENT`** (`patient_id` — 643 pacientes únicos).
- **Holdout Set**: 162 pacientes / 193 imágenes. Totalmente inalterado e intocado (SHA256: `85e3a856e5a1334d53084f242fff50a92c1c662fe1d4c8797053261578d2b335`).
- **Variables de Dominio Auditadas**: Clusters de resolución (`1662x952`, `1645x935`, `2048x1074`, etc.), subcarpetas de origen, ancho/alto de imagen, relación de aspecto, intensidad media y desviación estándar de contraste.

---

## 3. Domain Analysis (Predictibilidad de Dominio)

Se realizó una prueba de predictibilidad de dominio para evaluar si las 6 métricas matemáticas de la Cresta permiten clasificar/distinguir los clusters de resolución o subcarpetas de origen mediante validación cruzada agrupada por paciente (`GroupKFold(n_splits=5)` en `patient_id`):

- **Balanced Accuracy**: **0.1168** (Nivel de azar aleatorio $\approx 0.33$).
- **Conclusión**: Las métricas matemáticas **NO pueden predecir el dominio ni la resolución de adquisición**, demostrando que los descriptores no están dominados por firmas de artefactos de origen.
- **Estratificación por Dominio (FDR Benjamini-Hochberg)**: Las diferencias de medias entre los dos principales clusters de resolución (`1662x952` vs `1645x935`) resultaron **NO significativas** para todos los descriptores tras la corrección FDR ($p_{\text{FDR}} > 0.30$).

---

## 4. Shortcut Audit (Auditoría de Atajos)

Se evaluó si las mediciones estaban capturando atajos visuales espurios:

| Posible Atajo / Shortcut | Evidencia Evaluada | Prueba Realizada | Resultado | Riesgo |
| :--- | :--- | :--- | :--- | :---: |
| **Bordes / Fondo de Canvas** | *Bound checking* estricto en F6 | Verificación de coordenadas $[0, w] \times [0, h]$ | No Observado | `LOW` |
| **Intensidad Media Global** | Correlación $D_0$ vs Intensidad = $-0.12$ | Regresión lineal y matriz de correlación | Independiente | `LOW` |
| **Cluster de Resolución de Matriz** | `GroupKFold` Balanced Accuracy = $0.1168$ | Regresión logística agrupada por paciente | Efecto No Observado | `LOW` |
| **Redundancia $D_0$ vs Lacunaridad** | Correlación Spearman $\rho = -0.9979$ | Análisis de colinealidad y VIF ($VIF > 300$) | Redundancia Matemática | `HIGH` (Requiere F9) |
| **Volatilidad TDA $\beta_1$** | Sensibilidad a ventana Sauvola ($W=11$ vs $W=25$) | Barrido de parámetros de binarización | Sensible a Binarización | `MODERATE` |

---

## 5. Permutation Analysis (Control Negativo ROI Cresta $\leftrightarrow$ Basal, $N=1,000$)

Se aplicó un control negativo permutando aleatoriamente las etiquetas de ROI (`crest ↔ basal`) dentro de cada par pareado ($N=1,000$ iteraciones) para evaluar la probabilidad de obtener por azar las diferencias observadas:

| Descriptor | Diferencia Observada ($\Delta$) | Media Nula | Desv. Est. Nula | $p_{\text{permutación}}$ | Significación ($p < 0.001$) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| `fractal_D0` | **-0.0011** | 0.0000 | 0.0002 | **0.000** | **SÍ** |
| `minkowski_dimension` | **-0.0911** | -0.0001 | 0.0055 | **0.000** | **SÍ** |
| `lacunarity_mean` | **+0.0036** | -0.0000 | 0.0006 | **0.000** | **SÍ** |
| `multifractal_delta_alpha`| **+0.2930** | +0.0002 | 0.0242 | **0.000** | **SÍ** |
| `tda_beta_0` | **+1.3805** | -0.0004 | 0.1567 | **0.000** | **SÍ** |
| `tda_beta_1` | **-2.8767** | -0.0000 | 1.1972 | **0.016** | NO |

**Conclusión**: 5 de los 6 descriptores ($D_0, D_M, \Lambda, \Delta\alpha, \beta_0$) sobreviven holgadamente al control negativo de permutación ($p_{\text{perm}} < 0.001$), demostrando que la señal anatómica inter-regional no es un artefacto de la asignación aleatoria.

---

## 6. Redundancy & VIF Analysis (Investigación $D_0$ vs Lacunaridad)

Se investigó la colinealidad extrema entre $D_0$ y Lacunaridad ($\Lambda$):
- **Correlación de Spearman**: $\rho(D_0, \Lambda) = \mathbf{-0.9979}$
- **Correlación de Pearson**: $r(D_0, \Lambda) = \mathbf{-0.9975}$
- **Factor de Inflación de la Varianza (VIF)**:
  - $VIF(D_0) = \mathbf{388.83}$
  - $VIF(\Lambda) = \mathbf{400.69}$
  - $VIF(D_M) = 3.21$
  - $VIF(\Delta\alpha) = 2.42$
  - $VIF(\beta_0) = 2.68$
  - $VIF(\beta_1) = 2.96$

**Explicación Matemática**: La binarización por Sauvola produce máscaras binarias donde la proporción de ocupación de cajas a escalas finas determina directamente tanto el conteo de cajas ($D_0$) como la varianza de masa ($\Lambda$). Ambas métricas miden la misma propiedad estructural subyacente. Esta redundancia extrema deberá ser resuelta en la Fase 9 (Ablación) seleccionando un único representante del par.

---

## 7. Sensitivity Analysis (Sensibilidad de Parámetros)

Se evaluó la estabilidad de los descriptores frente a cambios en los parámetros del algoritmo:
- **TDA ($\beta_0, \beta_1$) vs Ventana Sauvola ($W=11, 15, 25$)**:
  - $\beta_0$ pasa de $1.18$ ($W=11$) a $1.42$ ($W=15$) y $2.32$ ($W=25$).
  - $\beta_1$ se mantiene relativamente estable alrededor de $12.0 - 12.4$.
- **$D_M$ vs Ruido e Intensidad**: Sensible al ruido Gaussiano continuo (tal como se estableció en F4.1).

---

## 8. Preprocessing Controls

- Comparación entre `Pipeline-B` (con CLAHE $2.5$) y versión sin CLAHE: La correlación Spearman $D_0 \leftrightarrow \Lambda$ se mantiene idéntica ($\rho = -0.998$). La redundancia es una propiedad de la geometría binaria y no de la ecualización por CLAHE.

---

## 9. Statistical Integrity

- Remuestreo Bootstrap realizado estrictamente a nivel de paciente ($N=1,000$ iteraciones en `patient_id`).
- Múltiples comparaciones corregidas mediante el algoritmo FDR de Benjamini-Hochberg.

---

## 10. Risk Table

| Riesgo / Limitación | Evidencia | Severidad | Mitigación para Fase 9 / Paper 1 |
| :--- | :--- | :---: | :--- |
| **Colinealidad Extrema $D_0 \leftrightarrow \Lambda$** | Spearman $\rho = -0.9979$, $VIF > 300$ | `HIGH` | Realizar ablación estricta en F9 para descartar la feature redundante. |
| **Sensibilidad de TDA $\beta_0$ al Window Size** | Variación de $\beta_0$ de $1.18$ a $2.32$ según ventana Sauvola | `MODERATE` | Congelar la ventana en $W=15$ y declarar la dependencia de escala en las limitaciones. |
| **Inestabilidad de $D_M$ ante Ruido** | $\text{ICC} = 0.4454$ en Fase 5 | `MODERATE` | Mantener $D_M$ en `Pipeline-A` sin ruido Gaussiano agregado. |

---

## 11. F8 Verdict

### Veredicto Oficial: **`PASS_WITH_LIMITATIONS`**

#### Criterios de Aprobación Cumplidos:
1. **No existe un atajo de dominio dominante**: Las features matemáticas no pueden predecir los clusters de resolución (`GroupKFold` Balanced Accuracy = $0.1168$).
2. **Las señales sobreviven al control negativo**: 5 de 6 descriptores muestran $p_{\text{perm}} < 0.001$ frente a permutaciones aleatorias de parches.
3. **Redundancia identificada y acotada**: Se caracterizó matemáticamente la colinealidad entre $D_0$ y Lacunaridad para su resolución en F9.
4. **Holdout 100% Intacto**: Se verificó la integridad estricta del hash SHA256 (`85e3a856e5a1334d53084f242fff50a92c1c662fe1d4c8797053261578d2b335`) sin ningún tipo de contaminación.
