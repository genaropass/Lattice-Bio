# FASE 5 — ESTABILIDAD COMPUTACIONAL DE LOS DESCRIPTORES

## 1. Contexto y Objetivos

Las Fases 0–4.1 demostraron la validez teórica y sintética de las implementaciones matemáticas de los descriptores ($D_0, D_M, \Lambda, \Delta\alpha, \beta_0, \beta_1$).

El objetivo de la **Fase 5** es determinar si los descriptores matemáticos producen mediciones suficientemente estables y reproducibles cuando se aplican a imágenes radiográficas reales ante perturbaciones computacionales controladas.

---

# 2. Dataset y Ámbito de Evaluación

- **Dataset de Referencia**: `data/processed/final_dataset_manifest.csv`
- **Muestras Evaluadas**: Exclusivamente muestras `INCLUDED` del grupo `Development` (657 imágenes / 643 pacientes).
- **Muestra Congelada para Perturbaciones**: 50 imágenes seleccionadas aleatoriamente con `seed=42`.
- **Holdout Set**: Totalmente congelado y no accedido (SHA256: `85e3a856e5a1334d53084f242fff50a92c1c662fe1d4c8797053261578d2b335`).

---

# 3. Categorías de Perturbación Computacional Evalua

Se aplicaron 8 categorías de perturbación sintética controlada a los recortes de ROI:

1. **Ruido Gaussiano**: $\sigma \in \{0.01, 0.02, 0.05, 0.10\}$
2. **Escalamiento de Contraste**: Multiplicación por factores $c \in \{0.8, 1.0, 1.2\}$
3. **Offset de Brillo**: Modificación de intensidad $\Delta I \in \{-10, 0, 10\}$
4. **Variación de CLAHE**: Clip Limit $CL \in \{1.5, 2.0, 3.0\}$
5. **Ventana de Binarización (Sauvola)**: Ventana $W \in \{11, 15, 25\}$
6. **Resolución Espacial**: Re-muestreo a factores $\{1.0, 0.75, 0.50\}$
7. **Rotación Rígida**: Ángulos $\theta \in \{0^\circ, 90^\circ, 180^\circ, 270^\circ\}$
8. **Traslación de ROI**: Enmascaramiento con desplazamientos de $\{\pm 2, \pm 5\}$ px

---

# 4. Métricas de Estabilidad Evaluadas

1. **ICC(3,1) (Coeficiente de Correlación Intraclase)**:
   Medida de consistencia bajo perturbación (modelo de efectos mixtos de dos vías, consistencia).
   - $\text{ICC} \ge 0.85$: Excelente reproducibilidad.
   - $0.70 \le \text{ICC} < 0.85$: Estabilidad aceptable con limitaciones.
   - $0.50 \le \text{ICC} < 0.70$: Sensible pero interpretable.
   - $\text{ICC} < 0.50$: Inestable.

2. **Coeficiente de Variación (CV)**:
   $$\text{CV} = \frac{\sigma}{\mu}$$

3. **Cambio Relativo Medio**:
   $$\Delta_{\text{rel}} = \frac{|X_{\text{perturbed}} - X_{\text{base}}|}{Format(|X_{\text{base}}|) + 1e-8}$$

4. **Tasa de Fallos (Failure Rate)**:
   Proporción de evaluadas que fallaron o produjeron valores no numéricos.

5. **Estabilidad de $R_{\text{trab}}$**:
   Preservación del ratio estructural inter-regional $R_{\text{trab}} = \frac{\text{Descriptor}(\text{Cresta})}{\text{Descriptor}(\text{Basal})}$.

---

# 5. Criterios de Clasificación de Estabilidad

- `ROBUST`: $\text{ICC} \ge 0.85$ y Failure Rate $< 2\%$.
- `ROBUST_WITH_LIMITATIONS`: $0.70 \le \text{ICC} < 0.85$.
- `SENSITIVE_BUT_INTERPRETABLE`: $0.50 \le \text{ICC} < 0.70$.
- `UNSTABLE`: $\text{ICC} < 0.50$ o Failure Rate $\ge 5\%$.

---

# 6. Estado de Verificación y Resultados Empíricos

Resultados calculados por `scripts/run_phase5_stability_evaluation.py` y auditados por `scripts/audit_phase5_stability.py`:

| Descriptor | ICC (Ruido) | ICC (Rotación) | Cambio Relativo Medio | Coef. Variación (CV) | Tasa de Fallo | $R_{\text{trab}}$ Medio | $R_{\text{trab}}$ Std | Clasificación |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `fractal_D0` | **0.8857** | **1.0000** | 0.0006 | 0.0070 | 0.0% | 1.0477 | 0.0935 | `ROBUST` |
| `lacunarity_mean` | **0.9395** | **1.0000** | 0.0008 | 0.0335 | 0.0% | 0.8420 | 0.2581 | `ROBUST` |
| `multifractal_delta_alpha` | **0.9274** | **1.0000** | 0.0388 | 1.5199 | 0.0% | 1.1095 | 1.6872 | `ROBUST` |
| `minkowski_dimension` | 0.4454 | **1.0000** | 0.0581 | 0.0495 | 0.0% | 1.0297 | 0.0593 | `UNSTABLE` |
| `tda_beta_0` | 0.3834 | **1.0000** | 0.4167 | 0.5590 | 0.0% | 0.9688 | 0.5870 | `UNSTABLE` |
| `tda_beta_1` | 0.0000 | **1.0000** | $4 \times 10^6$ | 0.8459 | 0.0% | 3.1898 | 6.6914 | `UNSTABLE` |

---

# 7. Síntesis Científica de Fase 5

1. **Descriptores Estables y Recomendados para Benchmarking (`ROBUST`)**:
   - **Box-counting ($D_0$)**: Demostró altísima reproducibilidad ante ruido ($\text{ICC} = 0.8857$) e invariancia rotacional ($\text{ICC} = 1.0$).
   - **Lacunaridad ($\Lambda$)**: Excelente estabilidad frente a perturbaciones de intensidad y ruido ($\text{ICC} = 0.9395$).
   - **Multifractal ($\Delta\alpha$)**: Estable frente a ruido ($\text{ICC} = 0.9274$), aunque presenta mayor dispersión biológica ($CV = 1.5199$).

2. **Descriptores Inestables (`UNSTABLE`)**:
   - **Dimensión de Minkowski ($D_M$)**: Tal como anticipó la auditoría de Fase 4.1, la formulación de dilación/cubrimiento por manta es altamente sensible al ruido Gaussiano ($\text{ICC} = 0.4454$).
   - **TDA ($\beta_0, \beta_1$)**: Los números de Betti sufren de inestabilidad topológica ante ruido continuo en escala de grises.

3. **Preservación del Integredad**:
   - Holdout congelado verificado intacto ($\text{SHA256} = \text{85e3a856e5a1334d53084f242fff50a92c1c662fe1d4c8797053261578d2b335}$).
   - Manifest de datasets sin alteraciones en los 850 casos de benchmark (657 Development / 193 Holdout).

