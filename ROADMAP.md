# ROADMAP DE INVESTIGACIÓN Y RECONSTRUCCIÓN EXPERIMENTAL (VERSIÓN DEFINITIVA V2.0)
## PROYECTO: LATTICE BIO
**Objetivo:** Construir una base experimental reproducible, metodológicamente defendible y alineada con los estándares internacionales de reporte (**STARD-AI / TRIPOD+AI**), para evaluar rigurosamente la hipótesis de Lattice Bio y determinar su potencial de publicación científica.

---

## 🎯 REFORMULACIÓN DE LA HIPÓTESIS CENTRAL Y CADENA DE VALIDEZ

### Formulación Defendible de la Hipótesis:
> **"Las alteraciones de la estructura trabecular asociadas a la rarefacción ósea pueden manifestarse como cambios cuantificables en descriptores fractales, multifractales y topológicos de radiografías dentales, aportando información complementaria a las representaciones visuales profundas auto-supervisadas."**

### Cadena de Validez Científica de Lattice Bio:
$$\text{Measurement Reliability} \longrightarrow \text{Structural Association} \longrightarrow \text{Predictive Utility} \longrightarrow \text{Clinical Value}$$

---

# 📑 SECUENCIA REESTRUCTURADA DE FASES

```text
RAW DATASET (Imágenes Dentales 2D)
   ↓
FASE 0: Freeze, Inventario e Historial (Experiment Ledger)
   ↓
FASE 1: Auditoría de Patient Identity + Deduplicación Perceptual
   ↓
🔒 CONGELAMIENTO INVIOLABLE DEL HOLDOUT SET (20% Pacientes Únicos)
   ↓
┌─────────────────────────────────────────────────────────────┐
│ CONJUNTO DE DESARROLLO (80% Pacientes Únicos)              │
│                                                             │
│ FASE 2: Definición de Pregunta de Investigación             │
│ FASE 3: Ground Truth / Fenotipo Estructural No-Circular    │
│ FASE 4: Verificación Matemática de Descriptores             │
│ FASE 5: Estabilidad Computacional y Confiabilidad (ICC)     │
│ FASE 6: ROI y Preprocesamiento Estandarizado                │
│ FASE 7: Clean Benchmark (DINOv2 vs Math vs Fusion)          │
│ FASE 8: Diagnóstico de Sesgo, Shortcut y Permutation Test   │
│ FASE 9: Estudio de Ablación (Ablation Study)                │
│ FASE 10: Bloqueo y Congelamiento del Modelo Final           │
└─────────────────────────────────────────────────────────────┘
   ↓
FASE 11: EVALUACIÓN ÚNICA EN HOLDOUT CONGELADO (Paired Bootstrap ΔAUC)
   ↓
FASE 12: Evaluación Piloto Cualitativa con Odontólogo (Pilot Expert Review)
   ↓
FASE 13: Redacción del Manuscrito bajo Guía STARD-AI / TRIPOD+AI
```

---

## FASE 0 — Freeze, Inventario e Historial (*Experiment Ledger*)

**Objetivo:** Crear un registro inmutable que documente la historia científica del proyecto, conservando el resultado $AUC \approx 0.999$ como el experimento histórico que reveló el fenómeno de *Shortcut Learning / Domain Leakage*.

### EXPERIMENT LEDGER

| Exp ID | Fecha | Dataset | Preprocessing / ROI | Feature Set | Model | Patient Split | Target | Resultado | Estado | Razón de Clasificación |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :--- | :--- |
| `EXP-001` | 2026-09-21 | Imagen Completa (2.795) | CLAHE / Sauvola | Math (16) | XGBoost | Random 5-Fold | `source_dataset` | AUC = 0.9937 | 🔴 **HISTÓRICO / INVÁLIDO** | Domain shortcut bias + Patient leakage |
| `EXP-002` | 2026-09-21 | Imagen Completa (2.795) | DINOv2 140x140 | DINOv2 (384) | XGBoost | Random 5-Fold | `source_dataset` | AUC = 0.9980 | 🔴 **HISTÓRICO / INVÁLIDO** | Shortcut bias por resolución y sensor |
| `EXP-003` | 2026-09-21 | Imagen Completa (2.795) | Concatenado | Hybrid (400) | XGBoost | Random OOF | `source_dataset` | AUC = 0.9996 | 🔴 **HISTÓRICO / INVÁLIDO** | DeLong en OOF conc. + Data leakage |
| `EXP-004` | 2026-09-22 | Imagen Completa (2.795) | Full Image | Hybrid (400) | XGBoost | 100% Train | `source_dataset` | AUC = 0.9997 | 🔴 **HISTÓRICO / INVÁLIDO** | Evaluación sobre datos de entrenamiento |
| `EXP-005` | 2026-09-22 | ROIs 64x64 (400) | Parche Interdental | Math (13) | XGBoost | Random 5-Fold | `source_dataset` | AUC = 0.7437 | 🟠 **PROVISIONAL / EXPLORATORIO**| Muestra reducción de sesgo macro, requiere GroupKFold |

* **Prioridad:** 🔴 BLOQUEANTE.
* **Output:** `data/processed/experiment_ledger.csv`.

---

## FASE 1 — *Patient Identity*, Deduplicación Perceptual y Congelamiento del Holdout

**Objetivo:** Agrupar imágenes por paciente, eliminar duplicados idénticos o casi idénticos y aislar el **Holdout Test Set** de forma estricta antes de iniciar cualquier análisis de desarrollo.

### Protocolo Ejecutado:
1. **Inferencia de `patient_id`:** Mediante parsing de nombres de archivo (ej. `ahmed_fares_1899...`, `Tawfik_Layan...-3-`).
2. **Deduplicación Perceptual:** Detección de imágenes duplicadas o re-escaladas mediante hash perceptual (*pHash*) y similitud de coseno en embeddings de alta dimensión.
3. **Tratamiento de Pacientes no Identificables:** Las imágenes sin `patient_id` confiable **se excluyen del análisis principal** y se reservan para experimentos secundarios.
4. **🔒 CONGELAMIENTO DEL HOLDOUT TEST SET:**
   * Reservar el **20% de pacientes únicos** en `data/processed/holdout_test_split.json`.
   * **REGLA ABSOLUTA:** El Holdout jamás se toca durante la Fase 2 a la Fase 10 (cero optimización, cero feature selection, cero visualización).

* **Prioridad:** 🔴 BLOQUEANTE.
* **Outputs:** `data/processed/patient_mapping.csv`, `data/processed/holdout_test_split.json`.

---

## FASE 2 — Definición de Pregunta de Investigación y Alcance

**Objetivo:** Acotar formalmente el alcance de la línea de investigación.

### Programa de Publicaciones por Tracks:
* **Paper 1 (Estudio Actual - Metodológico / Estructural):**  
  > *¿Las características matemáticas cuantifican de forma reproducible diferencias estructurales en regiones trabeculares de radiografías dentales y aportan información complementaria a representaciones visuales auto-supervisadas?*
* **Paper 2 (Estudio Clínico Secundario):**  
  > *Asociación cuantitativa con Pérdida Ósea Radiográfica (RBL %) y estadificación periodontal (AAP Staging).*
* **Paper 3 (Exactitud Diagnóstica y Aplicación Clínica):**  
  > *Evaluación de utilidad clínica y exactitud diagnóstica en entorno real.*

* **Prioridad:** 🔴 BLOQUEANTE.

---

## FASE 3 — Definición de Ground Truth / Fenotipo Estructural No-Circular

**Objetivo:** Definir etiquetas objetivas e independientes evitando la circularidad visual.

### Tracks de Clasificación:
* **Track A — Structural Phenotype (Paper 1):** Comparación entre parches anatómicos independientes estandarizados (ej. **Cresta Alveolar Interdental** vs. **Hueso Trabecular Basal Denso**) sin etiquetado subjetivo por apariencia visual.
* **Track B — Clinical Phenotype (Paper 2):** Quantificación de Pérdida Ósea Radiográfica (*RBL %*) validada por panel odontológico.

* **Prioridad:** 🔴 BLOQUEANTE.

---

## FASE 4 — Verificación Matemática de Descriptores

**Objetivo:** Auditar la formulación matemática para asegurar validez física.

1. **Box-Counting ($D_0$):** Escalas en progresión geométrica estricta base 2 ($2, 4, 8, 16, 32$).
2. **Manta de Minkowski ($D_M$):** Superficie de Peleg sobre grises continuo. Desactivar el *clamp* silencioso $[2.0, 3.0]$ y eliminar el resampleado ficticio a "35 μm/px" (usar resolución nativa estandarizada).
3. **Espectro Multifractal ($\Delta\alpha$):** Evaluar momentos $q \in [-5,5], [-3,3], [-1,3], [0,5]$. Seleccionar el rango basado en **criterios matemáticos predefinidos e independientes del clasificador** (estabilidad numérica, ausencia de Inf/NaN, linealidad de $\tau(q)$ con $R^2 > 0.95$).
4. **Topología de Datos (TDA):** Cálculo determinista sobre componentes conexas y ciclos en lugar de sub-muestreos aleatorios.

* **Prioridad:** 🟠 NECESARIA.

---

## FASE 5 — Estabilidad Computacional y Confiabilidad (*Feature Computational Stability*)

**Objetivo:** Medir la estabilidad computacional de cada descriptor ante perturbaciones numéricas y físicas en el conjunto de desarrollo.

### Protocolo de Perturbación Computacional:
Someter cada parche trabecular a perturbaciones sintéticas suaves (ruido Gaussiano $\sigma=0.01$, traslación de 2 px, rotación $\pm 3^\circ$, variación de contraste $\pm 5\%$) y medir:
* Coeficiente de Correlación Intraclase ($\text{ICC}(3,1)$).
* Coeficiente de Variación ($\text{CV}$).
* Gráficos de Bland-Altman y porcentaje de fallos numéricos.

> **Nota:** El valor $\text{ICC} > 0.75$ se utiliza como umbral orientativo, no como ley rígida de descarte.

* **Prioridad:** 🔴 BLOQUEANTE (Previo al benchmark).

---

## FASE 6 — ROI y Preprocesamiento Estandarizado

**Objetivo:** Extraer parches trabeculares estandarizados aislados de raíces, coronas y aire mediante `src/preprocessing/roi_segmentation.py`.

* **Prioridad:** 🟠 NECESARIA.

---

## FASE 7 — Clean Benchmark en Conjunto de Desarrollo

**Objetivo:** Evaluar la capacidad predictiva en Cross-Validation Agrupada por Paciente (`StratifiedGroupKFold`, $K=5$) exclusivamente dentro del 80% de desarrollo.

### Modelos del Benchmark:
* **Modelo M0 (Texture Baseline):** GLCM + LBP.
* **Modelo M1 (Vision Only):** DINOv2 (`dinov2_vits14`, 384 embeddings).
* **Modelo M2 (Math Only):** Descriptores estandarizados estables de la Fase 5.
* **Modelo M3 (Hybrid Fusion):** DINOv2 + Descriptores Matemáticos.

* **Prioridad:** 🔴 BLOQUEANTE.

---

## FASE 8 — Diagnóstico de Sesgo, *Shortcut* y *Label Permutation Test*

**Objetivo:** Someter el pipeline a pruebas diagnósticas de integridad computacional y fuga de dominio.

1. **Label Permutation Test (Sanity Check Crítico):** Permutar aleatoriamente las etiquetas ($y$). Si el clasificador obtiene $AUC > 0.55$, indica la presencia de *data leakage* o bugs en el código.
2. **Source Risk Classifier:** Evaluar la capacidad de clasificar la fuente del dataset sobre las ROIs para diagnosticar el riesgo de sesgo de dominio.

* **Prioridad:** 🟠 NECESARIA.

---

## FASE 9 — Estudio de Ablación (*Ablation Study*)

**Objetivo:** Medir la contribución individual de cada familia matemática ($D_0, D_M, \Lambda, \Delta\alpha, \beta_0, \beta_1$) al espacio latente de DINOv2 dentro del conjunto de desarrollo.

* **Prioridad:** 🟠 NECESARIA.

---

## FASE 10 — Bloqueo y Congelamiento del Modelo Final

**Objetivo:** Fijar de manera inmutable el preprocesamiento, la lista final de descriptores y los hiperparámetros del clasificador $M3$ entrenado en el 80% de desarrollo.

* **Prioridad:** 🔴 BLOQUEANTE.

---

## FASE 11 — Evaluación Única en Holdout Congelado (*One-Time Evaluation*)

**Objetivo:** Ejecutar la evaluación final **UNA SOLA VEZ** sobre el 20% del Holdout congelado desde la Fase 1.

### Protocolo Infecrencial:
1. **Métrica Primaria ($\Delta \text{AUC}$):** Evaluada mediante **Paired Patient-Level Bootstrap** ($B = 2.000$ re-muestreos agrupados por paciente) con Intervalos de Confianza al 95%.
2. **Análisis Secundario (DeLong):** Aplicado como análisis secundario solo si su validez metodológica en modelos anidados está totalmente justificada.
3. **Métricas Complementarias:** PR-AUC, Sensibilidad a especificidad del 90%, Brier Score.

* **Prioridad:** 🔴 BLOQUEANTE.

---

## FASE 12 — Evaluación Piloto Cualitativa con Odontólogo (*Pilot Expert Review*)

**Objetivo:** Evaluación exploratoria cualitativa del modelo.

* **Protocolo:** Revisión cegada de 30 ROIs trabeculares por parte de un profesional odontólogo, reportada estrictamente como ***Pilot Expert Review / Qualitative Feasibility Assessment***.

* **Prioridad:** 🟠 NECESARIA.

---

## FASE 13 — Síntesis y Redacción del Manuscrito Científico

**Objetivo:** Redactar el manuscrito formal bajo los estándares **STARD-AI / TRIPOD+AI** según corresponda al diseño final.

* **Prioridad:** 🔴 BLOQUEANTE (Post-experimentos).

---

# 🚥 MATRIZ DE PRIORIZACIÓN

| Tarea / Actividad | Clasificación | Razón |
| :--- | :---: | :--- |
| **Parseo `patient_id` y deduplicación pHash** | 🔴 **BLOQUEANTE** | Garantiza la independencia biológica de observaciones. |
| **🔒 Congelamiento Inviolable del Holdout (Fase 1.5)** | 🔴 **BLOQUEANTE** | Evita la contaminación de decisiones de desarrollo en test. |
| **Estabilidad Computacional de Descriptores (Fase 5)** | 🔴 **BLOQUEANTE** | Valida que las métricas midan estructura real y no ruido. |
| **Label Permutation Test (Fase 8)** | 🟠 **NECESARIA** | Sanity check obligatorio para descartar bugs/leakage. |
| **Paired Patient-Level Bootstrap $\Delta \text{AUC}$** | 🔴 **BLOQUEANTE** | Evaluación estadística rigurosa de complementariedad. |
| **Pilot Expert Review (30 ROIs)** | 🟠 **NECESARIA** | Evaluación cualitativa exploratoria con profesional. |

---

# 📦 ENTREGABLE MÍNIMO PUBLICABLE (MPE) vs. STRONG PAPER

### 1. Minimum Publishable Experiment (MPE) — *Paper 1 (Metodológico / arXiv)*
1. Grouping por paciente + Deduplicación + Holdout Congelado (20%).
2. Pruebas de confiabilidad computacional de descriptores (Fase 5).
3. Benchmark: DINOv2 vs. Math vs. Hybrid Fusion en ROIs $64 \times 64$ px.
4. Label Permutation Test ($AUC \approx 0.50$).
5. Paired Patient-Level Bootstrap $\Delta\text{AUC}$ en Holdout.

### 2. Strong Paper Version — *Paper 2/3 (Revista DMFR / IEEE TMI)*
Incluye MPE más:
1. Estudio de ablación completo por familia matemática.
2. Estudio de sensibilidad del rango $q$ multifractal.
3. Evaluación cualitativa pilotada con panel odontológico (Kappa).

---

# 📅 PLAN EJECUTIVO DE INICIO INMEDIATO

```text
SEMANA 1: Auditoría de Datos, Independencia de Pacientes y Congelamiento de Holdout
 ├── [HOY / Día 1] FASE 0 & FASE 1:
 │    ├── Inicializar experiment_ledger.csv.
 │    ├── Desarrollar script de parsing de patient_id y deduplicación pHash.
 │    └── Generar y CONGELAR data/processed/holdout_test_split.json.
 ├── [Día 2-3] FASE 4 & FASE 5:
 │    ├── Audit numérico de módulos fractales (desactivar clamp silencioso en Minkowski).
 │    └── Ejecutar test de estabilidad computacional (ICC / Coeficiente de Variación).
 └── [Día 4-5] FASE 6 & FASE 7:
      ├── Pipeline estandarizado de ROIs 64x64 px.
      └── Benchmark preliminar en 80% de desarrollo (StratifiedGroupKFold).
```
