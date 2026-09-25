# FASE 12.1 — SCIENTIFIC REVIEW, CORRECTION & COMPUTATIONAL REFERENCE AUDIT

## 1. EXECUTIVE SUMMARY

La **Fase 12.1 (Scientific Review, Correction & Computational Reference Audit)** constituye la auditoría científica integral de las Fases F0–F12 de **Lattice Bio** previa al inicio de la Fase 13 (Paper / Reproducibilidad).

### Objetivo
Establecer un rigor metrológico y epistemológico absoluto sobre todo el pipeline de investigación, asegurando que:
1. Ninguna afirmación en el futuro paper exceda la evidencia empírica disponible.
2. Se distinga formalmente la **reproducibilidad computacional** de una referencia geométrica fija frente a la **localización anatómica adaptativa**.
3. Se demuestre que la baja concordancia fina en F12 no invalida los hallazgos computacionales y out-of-sample de F11.
4. Se delimite exactamente el alcance científico de Lattice Bio como un estudio metrológico y caracterizador de diferencias estructurales en radiografías 2D, descartando cualquier claim de diagnóstico clínico, patología, densidad ósea 3D o biomarcador de enfermedad.

```text
F12.1 STATUS = READY_WITH_REQUIRED_CORRECTIONS
HOLDOUT_HASH = 85e3a856e5a1334d53084f242fff50a92c1c662fe1d4c8797053261578d2b335 (INTACT)
PIPELINE_MODIFIED = NO (0 changes to F10 lock)
HOLDOUT_RERUN = NO (0 re-evaluations of F11)
ROIS_MODIFIED = NO (Fixed 0.45h Crest / 0.80h Basal intact)
CLAIMS_AUDITED = 13 phases (F0–F12)
```

---

## 2. EVIDENCE HIERARCHY (JERARQUÍA DE EVIDENCIA EN 7 NIVELES)

Para evitar sobre-afirmaciones en la redacción del paper, se establece la siguiente jerarquía formal de evidencia:

```text
[Nivel 7] Preliminary Anatomical Interpretability (F12)
   └─ Evalúa reconocibilidad humana y modas de falla (88% Crest / 95% Basal usables). NO demuestra validación clínica ni diagnóstico.
[Nivel 6] Independent Out-of-Sample Reproduction (F11)
   └─ Demuestra que el contraste estructural (Crest vs Basal) se reproduce fuera de muestra (N=162 pacientes). NO demuestra ausencia total de overfitting clínico.
[Nivel 5] Feature Selection & Pipeline Lock (F9/F10)
   └─ Congela SET_G_LOCKED {D0, DM, Δα, β0} por redundancia (VIF>380) e inestabilidad. NO demuestra que SET_G sea óptimo para tareas clínicas.
[Nivel 4] Structural Contrast & Robustness (F7/F8)
   └─ Demuestra que la posición Crest vs Basal no es intercambiable bajo permutación (p < 0.001). NO demuestra causa biológica ni diagnóstico.
[Nivel 3] ROI Reproducibility & Computational Reference (F6/F6.1)
   └─ Demuestra determinismo bitwise (100%) y validez computacional (0 NaN/Inf). NO demuestra localización anatómica adaptativa por landmarks.
[Nivel 2] Computational Feature Stability (F5)
   └─ Demuestra resistencia de D0, DM y Δα ante ruido de gauss, contraste y rotaciones menores. NO demuestra invariabilidad clínica absoluta.
[Nivel 1] Mathematical Validity & Exact Implementation (F4/F4.1)
   └─ Demuestra corrección formal y convergencia matemática de las ecuaciones fractales y topológicas. NO demuestra utilidad médica por sí sola.
```

---

## 3. CLAIM AUDIT ACROSS ALL PHASES (AUDITORÍA COMPLETA DE AFIRMACIONES F0–F12)

| Fase | Claim Transmitido / Actual | Evidencia Empírica Real | Estado de la Afirmación | Corrección y Lenguaje Exigido |
| :--- | :--- | :--- | :---: | :--- |
| **F0** | "Dataset totalmente congelado y trazable." | Ledger con 100% de hashes SHA256 y manfiestos guardados. | **`SUPPORTED`** | Mantener claim de trazabilidad computacional. |
| **F1 / F1.5** | "Eliminación total de duplicados de pacientes y perceptuales." | Deduplicación por Patient ID y Hash Perceptual (135 candidatas excluidas). | **`SUPPORTED`** | Mantener. Aclarar que aplica al dataset analizado. |
| **F2 / F3** | "Referencia estructural sin ground truth clínico." | No existen diagnósticos médicos asociados (periodontitis/osteoporosis). | **`SUPPORTED`** | Enfatizar que es un estudio metrológico y no un estudio de precisión diagnóstica. |
| **F4 / F4.1** | "Validación matemática exacta del pipeline fractal y topológico." | Auditoría de código, corrección de clamping en $D_M$ y bug en $\beta_0$. | **`SUPPORTED`** | Especificar que valida la implementación algorítmica, no la biología subyacente. |
| **F5** | "Estabilidad computacional de descriptores." | Perturbaciones sintéticas (ruido gaussiano, rotación $\pm 5^\circ$, escala). | **`SUPPORTED_WITH_LIMITATION`** | Aclarar que $D_0, D_M, \Delta\alpha$ son estables; $\beta_1$ presentó alta volatilidad. |
| **F6 / F6.1** | "Validación anatómica de ROIs fijas." | 100% ROIs válidas computacionalmente; 30/30 en auditoría operacional F6.1. | **`OVERSTATED`** | **CORREGIR**: Sustituir "validación anatómica" por "referencia computacional geométrica reproducible". |
| **F7** | "Diferenciación estructural entre Cresta y Basal." | Paired t-test y permutación $p < 0.001$ en $D_0, D_M, \Delta\alpha, \beta_0$. | **`SUPPORTED_WITH_LIMITATION`** | Aclarar que demuestra no-intercambiabilidad espacial de parches fijos, no patología. |
| **F8** | "Ausencia de shortcuts por resolución o histograma." | Sensibilidad y permutaciones no mostraron correlación espuria con resolución. | **`SUPPORTED_WITH_LIMITATION`** | Indicar que se descartaron confusores primarios de adquisición, pero persisten factores de proyección. |
| **F9** | "SET_G {D0, DM, Δα, β0} es el conjunto óptimo robusto." | Lacunaridad eliminada por colinealidad ($\rho = -0.9979, VIF > 380$); $\beta_1$ por inestabilidad. | **`NEEDS_REWORDING`** | **CORREGIR**: Aclarar que `SET_G_LOCKED` es un subconjunto no redundante candidato, no un óptimo clínico. |
| **F10** | "Pipeline congelado definitivamente." | Hash y especificación fija en `configs/final_pipeline_lock_v1.json`. | **`SUPPORTED`** | Mantener. Aclarar las limitaciones metodológicas declaradas. |
| **F11** | "Reproducción fuera de muestra y ausencia de overfitting." | 100% de los 4 descriptores reprodujeron signo y magnitud en Holdout ($N=162$). | **`SUPPORTED_WITH_LIMITATION`** | Aclarar que demuestra reproducibilidad out-of-sample del contraste, no ausencia de overfitting clínico. |
| **F12** | "Validación anatómica por expertos de las ROIs." | 88% Cresta y 95% Basal usables; Kappa inter-observador $-0.06$ a $+0.10$. | **`OVERSTATED`** | **CORREGIR**: Aclarar que F12 evalúa la interpretabilidad preliminar y expone las limitaciones de la geometría fija. |

---

## 4. AUDITORÍA ESPECÍFICA DE LA FASE 12

### Lo que F12 REALMENTE Demuestra:
1. **Interpretabilidad Operacional Elevada**: El 88% de las ROIs Cresta y el 95% de las ROIs Basal fueron consideradas "usables" (contienen tejido óseo trabecular interpretable).
2. **Identificación Transparente de Modas de Falla**: Demuestra que el solapamiento marginal con raíces dentales (38% en Cresta) y el borde cortical mandibular (14% en Basal) son las principales limitaciones de una geometría fija.
3. **Necesidad de Futuras ROIs Adaptativas**: La baja concordancia fina entre expertos ($\kappa \approx 0.00$) demuestra que el juicio humano sobre límites marginales es subjetivo y apoya la transición hacia segmentación semántica basada en landmarks en Paper 2.

### Lo que F12 NO Demuestra (y NUNCA debe afirmarse):
1. **NO demuestra "Validación Anatómica Exacta"**: No afirma que las ROIs fijas sean idénticas a landamrks anatómicos adaptativos.
2. **NO demuestra Ground Truth Clínico**: No evalúa presencia ni severidad de patología periodontal u ósea.
3. **NO demuestra Superioridad Geométrica**: No afirma que la caja de $64 \times 64$ px sea el tamaño óptimo biológico.

---

## 5. EVIDENCIA ACUMULATIVA DE LA GEOMETRÍA FIJA COMO REFERENCIA COMPUTACIONAL REPRODUCIBLE

Se establece la siguiente sección formal que fundamenta el uso de la geometría fija en el paper:

> **"Evidence Supporting the Fixed ROI Geometry as a Computational Reference"**
>
> *Across phases F6–F11, the fixed geometric ROI layout (Crest at 0.50w, 0.45h; Basal at 0.50w, 0.80h; patch size 64x64 px) provided an operational, deterministic, and fully reproducible spatial framework for evaluating intra-patient trabecular differences. The geometry is completely independent of texture intensity and mathematical descriptor values, eliminating feedback loops during extraction.*
>
> *While F12 highlights the inherent limitations of fixed coordinates in accounting for individual root morphology (inter-rater kappa -0.06 to 0.10), F11 demonstrates that the resulting paired structural contrast reproduces consistently out-of-sample across independent held-out patients (100% sign agreement and effect magnitude ratio 0.915–1.168). Consequently, the fixed ROI geometry is retained and reported strictly as a **reproducible computational reference** rather than an anatomically adaptive landmarking method.*

---

## 6. RECONCILIACIÓN ENTRE F11 Y F12

### ¿La baja concordancia de expertos en F12 invalida la reproducibilidad observada en F11?

**Respuesta Científica: NO.**

1. **Preguntas Distintas**: F11 responde a una pregunta **matemático-computacional** (*¿Es reproducible el contraste numérico entre la región superior e inferior de la imagen en pacientes independientes?*), mientras que F12 responde a una pregunta **anatómico-perceptual** (*¿Hasta qué punto dos observadores humanos coinciden exactamente en si un solapamiento del 10% con una raíz invalida una ROI?*).
2. **Independencia Algorítmica**: El pipeline matemático extrae características de forma determinista basándose en la rejilla de píxeles sin verse afectado por la variabilidad del juicio inter-observador.
3. **Conclusión**: F12 limita la interpretación de la resolución anatómica microscópica de cada parche, pero **no invalida la validez matemática ni la reproducibilidad computacional out-of-sample de F11**.

---

## 7. EVALUACIÓN DE NOVEDAD (NOVELTY AUDIT)

### Lo que NO es novedoso por sí solo:
* La dimensión fractal por Box-Counting ($D_0$).
* La dimensión de manta de Minkowski ($D_M$).
* El espectro multifractal ($\Delta\alpha$) o la homología persistente (TDA $\beta_0$).
* El análisis de textura en radiografías dentales.

### La Contribución Metodológica Real de Lattice Bio:
La contribución científica de este trabajo reside en la **cadena metodológica de control metrológico y reproducibilidad out-of-sample**, que incluye:
1. Un marco estricto de control de identidad de pacientes y deduplicación perceptual en benchmarks 2D.
2. Un protocolo de auditoría matemática de algoritmos fractales/topológicos con corrección de sesgos de escala y colinealidad.
3. Un diseño de contraste estructural intra-paciente pareado relativo ($R_{\text{trab}}$) controlado por permutación espacial.
4. El congelamiento definitivo del pipeline previo al acceso de un Holdout reservado con firewall criptográfico.
5. La caracterización explícita y transparente de las limitaciones de interpretabilidad anatómica mediante un piloto experto cegado.

---

## 8. LÍMITES DE LAS AFIRMACIONES DEL PAPER (PAPER CLAIM BOUNDARIES)

Se proponen tres versiones del claim central del paper. **Se adopta oficialmente la Versión B (Balanceada)**:

* **Versión A (Conservadora)**:
  > *"We present a reproducible computational framework for extracting paired structural descriptors in 2D intraoral radiographs, showing consistent regional differences between upper and lower image patches in an independent held-out dataset."*
* **Versión B (Balanceada — RECOMENDADA PARA EL PAPER)**:
  > *"Lattice Bio establishes a rigorous computational pipeline for paired structural characterization of trabecular bone patterns in intraoral periapical radiographs. Using a locked set of validated fractal and topological descriptors under a fixed spatial reference, we demonstrate out-of-sample reproducibility across independent patients while systematically documenting the anatomical interpretability limitations of non-adaptive geometric ROIs."*
* **Versión C (Fuerte pero Defendible)**:
  > *"We report a fully reproducible mathematical pipeline that quantifies paired trabecular structural contrast between alveolar crest and basal mandibular regions in 2D periapical radiographs, demonstrating out-of-sample generalizability and expert-assessed spatial usability."*

### Términos PROHIBIDOS en la Redacción:
* ❌ Diagnóstico / Diagnostic tool / Diagnostic accuracy
* ❌ Periodontitis / Osteoporosis / Bone loss disease stage
* ❌ Biomarcador clínico / Clinical biomarker
* ❌ Arquitectura 3D / Densidad ósea absoluta
* ❌ Validación anatómica perfecta / Anatomically validated ROI

---

## 9. MATRIZ DE REQUISITOS Y VACÍOS PENDIENTES PREVIOS A F13

| Categoría | Elemento | Estado | Acción para F13 |
| :--- | :--- | :---: | :--- |
| **Requerido para Paper 1** | Definiciones matemáticas formales ($D_0, D_M, \Delta\alpha, \beta_0$) | **Listo** | Incluir en la sección de Métodos. |
| **Requerido para Paper 1** | Diagrama de flujo del dataset (F1, F1.5, Dev, Holdout) | **Listo** | Generar figura principal PRISMA-style. |
| **Requerido para Paper 1** | Tabla de reproducibilidad F11 (Dev vs Holdout) | **Listo** | Incluir Tabla 1 en Resultados. |
| **Requerido para Paper 1** | Sección de limitaciones anatómicas F12 y modas de falla | **Listo** | Incluir en Discusión. |
| **Requerido para Paper 1** | Paquete de reproducibilidad de código y semillas | **Listo** | Preparar repositorio GitHub público. |
| **Importante pero Opcional** | Visualizaciones de espectros multifractales en alta resolución | **Opcional** | Agregar como Supplementary Material. |
| **Trabajo Futuro (Paper 2)** | Segmentación semántica por landmarks anatómicos | **Futuro** | Proponer formalmente en la Discusión de Paper 1. |
| **Trabajo Futuro (Paper 2)** | Validación con cohortes clínicas anotadas por enfermedad | **Futuro** | Proponer como trabajo futuro sin sobre-afirmar en Paper 1. |

---

## 10. DECISIÓN SOBRE F13 (F13 READINESS DECISION)

```text
STATUS = READY_WITH_REQUIRED_CORRECTIONS
```

### Justificación:
1. El proyecto ha completado todas las fases metodológicas (F0–F12.1) con auditoría estricta de 0 violaciones.
2. Los límites científicos y la nomenclatura están formalmente corregidos.
3. La evidencia de reproducibilidad out-of-sample (F11) y las limitaciones de interpretabilidad anatómica (F12) están reconciliadas y documentadas.
4. El pipeline se encuentra listo para la fase de redacción del manuscrito y empaquetado de reproducibilidad (F13).

---

## 11. REGISTRO EN EL EXPERIMENT LEDGER

La entrada `EXP-F12.1-001` fue agregada exitosamente a `data/processed/experiment_ledger.csv`:

```csv
exp_id,date,dataset,preprocessing,feature_set,model,split,target,auc,status,reason
EXP-F12.1-001,2026-09-25,All Phases F0-F12 Audited,Pipeline-A/Pipeline-B (v1.0 Frozen),SET_G_LOCKED (D0, DM, Delta_alpha, beta0),Scientific Audit & Computational Reference Reconciliation,Development & Holdout (0 Pipeline Changes, 0 Re-runs),Scientific Review & Claim Boundaries,N/A,VALID,Comprehensive audit completed. Fixed ROI computational reference established. F11/F12 reconciled.
```

---

## 12. VERIFICACIÓN DE REGLAS DE INTEGRIDAD (INTEGRITY CHECK)

* **Hash SHA256 del Holdout**: `85e3a856e5a1334d53084f242fff50a92c1c662fe1d4c8797053261578d2b335` (**VERIFICADO INTACTO**).
* **Modificaciones a F10 / F11**: **0**.
* **Re-evaluaciones de F11 / F12**: **0**.
* **Modificaciones de coordenadas ROI**: **0**.
* **Eliminación de observaciones incomodas**: **0**.
