# FASE 12.1 — SCIENTIFIC REVIEW, CORRECTION & COMPUTATIONAL REFERENCE AUDIT

> **Nota**: Este documento incorpora las correcciones de lenguaje científico de la Fase 12.1.1 (F12.1.1). Ningún resultado numérico fue modificado; únicamente se ajustó la terminología para que las afirmaciones no excedan la evidencia empírica disponible.

## 1. EXECUTIVE SUMMARY

La **Fase 12.1 (Scientific Review, Correction & Computational Reference Audit)** constituye la auditoría científica integral de las Fases F0–F12 de **Lattice Bio** previa al inicio de la Fase 13 (Paper / Reproducibilidad).

### Objetivo
Establecer un rigor metrológico y epistemológico sobre todo el pipeline de investigación, asegurando que:
1. Ninguna afirmación en el futuro paper exceda la evidencia empírica disponible.
2. Se distinga formalmente la **reproducibilidad computacional** de una referencia geométrica fija frente a la **localización anatómica adaptativa**.
3. Se documente que la baja concordancia fina en F12 no invalida los hallazgos empíricos out-of-sample de F11.
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
   └─ Evalúa reconocibilidad humana y modas de falla (88% Crest / 95% Basal usables).
      NO demuestra validación clínica ni diagnóstico.
      NOTA: Constituye una evaluación preliminar de interpretabilidad, no una validación anatómica.

[Nivel 6] Independent Out-of-Sample Reproduction (F11)
   └─ El Holdout independiente reprodujo de forma consistente la dirección y una magnitud
      aproximadamente similar de los contrastes estructurales observados en Development
      (N=162 pacientes independientes). NO demuestra ausencia de overfitting clínico.

[Nivel 5] Feature Selection & Pipeline Lock (F9/F10)
   └─ Congela SET_G_LOCKED {D0, DM, Δα, β0} por redundancia (VIF>380) e inestabilidad.
      NO demuestra que SET_G sea óptimo para tareas clínicas.

[Nivel 4] Structural Contrast & Robustness (F7/F8)
   └─ Demuestra que la posición Crest vs Basal no es intercambiable bajo permutación (p < 0.001).
      NO demuestra causa biológica ni diagnóstico.

[Nivel 3] ROI Reproducibility & Fixed Computational Reference (F6/F6.1)
   └─ Demuestra determinismo bitwise (100%) y validez computacional (0 NaN/Inf).
      NO demuestra localización anatómica adaptativa por landmarks.

[Nivel 2] Computational Feature Stability (F5)
   └─ Demuestra resistencia de D0, DM y Δα ante ruido de gauss, contraste y rotaciones menores.
      NO demuestra invariabilidad clínica absoluta.

[Nivel 1] Mathematical Validity & Exact Implementation (F4/F4.1)
   └─ Demuestra corrección formal de las implementaciones algorítmicas fractales y topológicas.
      NO demuestra utilidad médica por sí sola.
```

---

## 3. CLAIM AUDIT ACROSS ALL PHASES (AUDITORÍA COMPLETA DE AFIRMACIONES F0–F12)

| Fase | Claim Transmitido / Actual | Evidencia Empírica Real | Estado de la Afirmación | Corrección y Lenguaje Exigido |
| :--- | :--- | :--- | :---: | :--- |
| **F0** | "Dataset totalmente congelado y trazable." | Ledger con 100% de hashes SHA256 y manifiestos guardados. | **`SUPPORTED`** | Mantener claim de trazabilidad computacional. |
| **F1 / F1.5** | "Eliminación total de duplicados de pacientes y perceptuales." | Deduplicación por Patient ID y Hash Perceptual (135 candidatas excluidas). | **`SUPPORTED`** | Mantener. Aclarar que aplica al dataset analizado. |
| **F2 / F3** | "Referencia estructural sin ground truth clínico." | No existen diagnósticos médicos asociados (periodontitis/osteoporosis). | **`SUPPORTED`** | Enfatizar que es un estudio metrológico, no un estudio de precisión diagnóstica. |
| **F4 / F4.1** | "Validación matemática exacta del pipeline fractal y topológico." | Auditoría de código, corrección de clamping en $D_M$ y bug en $\beta_0$. | **`SUPPORTED`** | Especificar que valida la implementación algorítmica, no la biología subyacente. |
| **F5** | "Estabilidad computacional de descriptores." | Perturbaciones sintéticas (ruido gaussiano, rotación $\pm 5^\circ$, escala). | **`SUPPORTED_WITH_LIMITATION`** | Aclarar que $D_0, D_M, \Delta\alpha$ son estables; $\beta_1$ presentó alta volatilidad. |
| **F6 / F6.1** | "Validación anatómica de ROIs fijas." | 100% ROIs válidas computacionalmente; 30/30 en auditoría operacional F6.1. | **`OVERSTATED`** | **CORREGIDO**: Sustituido "validación anatómica" por "referencia geométrica fija reproducible". No se reivindica localización anatómica adaptativa. |
| **F7** | "Diferenciación estructural entre Cresta y Basal." | Paired t-test y permutación $p < 0.001$ en $D_0, D_M, \Delta\alpha, \beta_0$. | **`SUPPORTED_WITH_LIMITATION`** | Aclarar que demuestra no-intercambiabilidad espacial de parches fijos, no patología. |
| **F8** | "Ausencia de shortcuts por resolución o histograma." | Sensibilidad y permutaciones no mostraron correlación espuria con resolución. | **`SUPPORTED_WITH_LIMITATION`** | Indicar que se descartaron confusores primarios de adquisición, pero persisten factores de proyección. |
| **F9** | "SET_G {D0, DM, Δα, β0} es el conjunto óptimo robusto." | Lacunaridad eliminada por colinealidad ($\rho = -0.9979, VIF > 380$); $\beta_1$ por inestabilidad. | **`NEEDS_REWORDING`** | **CORREGIDO**: `SET_G_LOCKED` es el subconjunto candidato congelado no redundante, no un óptimo clínico. |
| **F10** | "Pipeline congelado definitivamente." | Hash y especificación fija en `configs/final_pipeline_lock_v1.json`. | **`SUPPORTED`** | Mantener. Aclarar las limitaciones metodológicas declaradas. |
| **F11** | "Reproducción fuera de muestra y ausencia de overfitting." | Los 4 descriptores reprodujeron signo y magnitud comparable en Holdout ($N=162$). | **`SUPPORTED_WITH_LIMITATION`** | **CORREGIDO**: Reemplazado "100% reproducible" por "reprodujo consistentemente la dirección y magnitud aproximadamente similar". El rango 0.915–1.168 se reporta únicamente como ratio descriptivo de magnitud, no como métrica formal de reproducibilidad. |
| **F12** | "Validación anatómica por expertos de las ROIs." | 88% Cresta y 95% Basal usables; Kappa inter-observador $-0.06$ a $+0.10$. | **`OVERSTATED`** | **CORREGIDO**: F12 constituye una evaluación preliminar de interpretabilidad anatómica. No establece validación anatómica ni ground truth de localización. |

---

## 4. AUDITORÍA ESPECÍFICA DE LA FASE 12

### Lo que F12 REALMENTE Demuestra:
1. **Interpretabilidad Operacional Frecuente**: El 88% de las lecturas expertas de ROI Cresta y el 95% de las lecturas de ROI Basal fueron juzgadas como "usables" (contienen tejido óseo trabecular interpretable). Esto corresponde a 100 lecturas primarias de 2 expertos independientes sobre 50 imágenes.
2. **Identificación Transparente de Modas de Falla**: Registra los tipos de interferencia más frecuentes (ver Sección 4.1). Estos son conteos de lecturas de expertos, no tasas de prevalencia por imagen individual, y los tipos de interferencia no son mutuamente excluyentes.
3. **Necesidad de Futuras ROIs Adaptativas**: La baja concordancia fina entre expertos ($\kappa \approx 0.00$) demuestra que el juicio humano sobre límites marginales es subjetivo y apoya la transición hacia segmentación semántica basada en landmarks en investigaciones futuras.

### Sección 4.1 — Conteos de Interferencia Verificados (N = 100 lecturas primarias)

Los siguientes conteos fueron verificados directamente desde `data/processed/phase12_expert_pilot.csv`. Representan el número de lecturas de expertos (no imágenes únicas) en las cuales cada tipo de interferencia fue registrado. Las categorías no son mutuamente excluyentes.

**Interferencias en ROI Cresta (A):**
- `root` (solapamiento con raíz dental): **19 / 100 lecturas** (19.0%)
- `artifact` (artefacto radiográfico): **4 / 100 lecturas** (4.0%)
- `lamina_dura` (lámina dura): **4 / 100 lecturas** (4.0%)
- `periodontal_space` (espacio periodontal): **2 / 100 lecturas** (2.0%)

**Interferencias en ROI Basal (B):**
- `cortical_boundary` (borde cortical): **7 / 100 lecturas** (7.0%)
- `air_space` (espacio aéreo): **2 / 100 lecturas** (2.0%)

> **Nota metodológica**: Los valores anteriores corresponden a lecturas de expertos sobre el conjunto de 50 imágenes del piloto. Una misma imagen puede recibir 0, 1 o 2 lecturas con interferencia dependiendo del juicio de cada experto. No se presentan como porcentajes de imágenes afectadas ni como prevalencia clínica.

### Lo que F12 NO Demuestra (y NUNCA debe afirmarse):
1. **NO demuestra "Validación Anatómica Exacta"**: No afirma que las ROIs fijas sean equivalentes a landmarks anatómicos adaptativos.
2. **NO demuestra Ground Truth Clínico**: No evalúa presencia ni severidad de patología periodontal u ósea.
3. **NO demuestra Superioridad Geométrica**: No afirma que la caja de $64 \times 64$ px sea el tamaño óptimo biológico.

---

## 5. EVIDENCIA DE LA GEOMETRÍA FIJA COMO REFERENCIA COMPUTACIONAL REPRODUCIBLE

### "Evidence Supporting the Fixed ROI Geometry as a Computational Reference"

La geometría ROI fija (Cresta en $0.50w, 0.45h$; Basal en $0.50w, 0.80h$; parche $64 \times 64$ px) acumuló la siguiente evidencia a través de F6–F11:

> *"The fixed geometric ROI layout provided an operational, deterministic, and reproducible spatial framework for evaluating paired structural differences across radiographs. The geometry is completely independent of texture intensity and mathematical descriptor values, eliminating circularity during extraction. Across F6–F11, this reference produced consistent paired structural contrasts that survived spatial permutation testing and reproduced in direction and approximately similar magnitude in an independent held-out patient cohort. F12 documents a preliminary anatomical interpretability assessment that identifies the limitations of fixed geometric placement (particularly root overlap in the crest region) without invalidating the computational reproducibility demonstrated in F11."*

> "The fixed ROI geometry provided a reproducible computational reference for paired structural comparison across radiographs. This reproducibility should not be interpreted as equivalent to anatomically adaptive localization."

> [en español] "La geometría fija proporcionó una referencia computacional reproducible para la comparación estructural pareada entre regiones de las radiografías. Esta reproducibilidad no debe interpretarse como equivalente a una localización anatómica adaptativa basada en landmarks."

Lenguaje aprobado para el paper: **"fixed computational reference"**, **"reproducible geometric reference"**, **"operational ROI geometry"**, **"fixed spatial reference"**.

Lenguaje **no aprobado**: "validated ROI", "anatomically validated", "expert-validated ROI placement".

---

## 6. RECONCILIACIÓN ENTRE F11 Y F12

### ¿La baja concordancia de expertos en F12 invalida la reproducibilidad observada en F11?

**Respuesta Científica: NO. F11 y F12 responden a preguntas distintas.**

1. **F11** responde a: *¿Se reproduce el contraste numérico entre la región superior e inferior de la imagen en pacientes independientes no vistos?* El Holdout independiente reprodujo de forma consistente la dirección y una magnitud aproximadamente similar de los contrastes estructurales observados en Development. El ratio descriptivo de magnitud entre Holdout y Development osciló entre 0.915 y 1.168 (dato descriptivo de comparación de magnitudes, no una métrica formal de reproducibilidad).
2. **F12** responde a: *¿En qué proporción de casos dos expertos humanos coinciden exactamente en si un solapamiento marginal con una raíz invalida la ROI?* Esta es una pregunta anatómico-perceptual independiente.
3. **Independencia Algorítmica**: El pipeline extrae características de forma determinista sobre la rejilla de píxeles sin verse afectado por la variabilidad del juicio inter-observador.
4. **Conclusión**: F12 limita la interpretación de la correspondencia anatómica exacta de cada parche, pero no invalida la reproducibilidad out-of-sample del contraste estructural demostrada en F11.

Distinción terminológica obligatoria:
- **F4/F4.1** → validación de la implementación matemática de los descriptores.
- **F5** → estabilidad computacional ante perturbaciones sintéticas.
- **F11** → reproducibilidad empírica out-of-sample del contraste bajo el pipeline congelado. No es sinónimo de "robustez matemática".

---

## 7. EVALUACIÓN DE NOVEDAD (NOVELTY AUDIT)

### Lo que NO es novedoso por sí solo:
* La dimensión fractal por Box-Counting ($D_0$).
* La dimensión de manta de Minkowski ($D_M$).
* El espectro multifractal ($\Delta\alpha$) o la homología persistente (TDA $\beta_0$).
* El análisis de textura en radiografías dentales.

### La Contribución Metodológica de Lattice Bio (pendiente de cotejo bibliográfico formal en F13):
La posible contribución científica reside en la **cadena integrada de control metrológico y reproducibilidad out-of-sample**, que incluye:
1. Un marco de control de identidad de pacientes y deduplicación perceptual en benchmarks 2D.
2. Un protocolo de auditoría de algoritmos fractales/topológicos con corrección de sesgos de escala y colinealidad (VIF > 380).
3. Un diseño de contraste estructural intra-paciente pareado relativo ($R_{\text{trab}}$) controlado por permutación espacial.
4. El congelamiento definitivo del pipeline previo al acceso de un Holdout reservado con firewall criptográfico.
5. La caracterización explícita de las limitaciones de interpretabilidad anatómica mediante un piloto experto cegado.

> **Nota**: La novedad absoluta de esta combinación requiere revisión bibliográfica formal, tarea que corresponde a F13.

---

## 8. LÍMITES DE LAS AFIRMACIONES DEL PAPER (PAPER CLAIM BOUNDARIES)

Se proponen tres versiones del claim central del paper. **Se adopta oficialmente la Versión B (Balanceada)**:

* **Versión A (Conservadora)**:
  > *"We present a reproducible computational framework for extracting paired structural descriptors in 2D intraoral radiographs, showing consistent regional differences between upper and lower image patches that reproduced in direction and approximately similar magnitude in an independent held-out dataset."*
* **Versión B (Balanceada — RECOMENDADA PARA EL PAPER)**:
  > *"Lattice Bio establishes a rigorous computational pipeline for paired structural characterization of trabecular bone patterns in intraoral periapical radiographs. Using a locked set of validated fractal and topological descriptors under a fixed spatial reference, we demonstrate out-of-sample reproducibility of paired structural contrasts across independent patients while systematically documenting the anatomical interpretability limitations of non-adaptive geometric ROIs."*
* **Versión C (Fuerte pero Defendible)**:
  > *"We report a reproducible mathematical pipeline that quantifies paired trabecular structural contrast between alveolar crest and basal mandibular regions in 2D periapical radiographs, demonstrating consistent out-of-sample reproduction of directional structural differences and expert-assessed spatial usability under explicit anatomical limitations."*

### Términos PROHIBIDOS en la Redacción:
* ❌ Diagnóstico / Diagnostic tool / Diagnostic accuracy
* ❌ Periodontitis / Osteoporosis / Bone loss disease stage
* ❌ Biomarcador clínico / Clinical biomarker
* ❌ Arquitectura 3D / Densidad ósea absoluta
* ❌ Validación anatómica / Anatomically validated ROI / expert-validated ROI
* ❌ 100% reproducible / fully reproducible (como afirmación absoluta sin calificativo)
* ❌ Ausencia de overfitting / no overfitting (sin calificativo de scope)
* ❌ Mathematical robustness (como sinónimo de reproducibilidad empírica de F11)
* ❌ Ground truth (clínico o anatómico)

---

## 9. MATRIZ DE REQUISITOS Y VACÍOS PENDIENTES PREVIOS A F13

| Categoría | Elemento | Estado | Acción para F13 |
| :--- | :--- | :---: | :--- |
| **Requerido para Paper 1** | Definiciones matemáticas formales ($D_0, D_M, \Delta\alpha, \beta_0$) | **Listo** | Incluir en la sección de Métodos. |
| **Requerido para Paper 1** | Diagrama de flujo del dataset (F1, F1.5, Dev, Holdout) | **Listo** | Generar figura principal PRISMA-style. |
| **Requerido para Paper 1** | Tabla de reproducibilidad F11 (Dev vs Holdout) | **Listo** | Incluir Tabla 1 en Resultados. |
| **Requerido para Paper 1** | Sección de limitaciones anatómicas F12 y modas de falla con denominador correcto | **Listo** | Incluir en Discusión con denominador explícito (100 lecturas). |
| **Requerido para Paper 1** | Revisión bibliográfica formal para claim de novedad | **Pendiente** | Tarea prioritaria en F13. |
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
1. El proyecto ha completado todas las fases metodológicas (F0–F12.1.1) con auditoría de 0 violaciones de integridad de datos.
2. Los límites científicos y la nomenclatura están formalmente corregidos (F12.1.1).
3. La evidencia de reproducibilidad out-of-sample (F11) y las limitaciones de interpretabilidad anatómica (F12) están reconciliadas y documentadas.
4. La **revisión bibliográfica formal** para el claim de novedad es la única tarea sustantiva aún pendiente, y corresponde completarla al inicio de F13.

---

## 11. REGISTRO EN EL EXPERIMENT LEDGER

Las entradas correspondientes a esta fase fueron agregadas exitosamente a `data/processed/experiment_ledger.csv`:

- `EXP-F12.1-001`: Auditoría científica integral F0–F12.
- `EXP-F12.1.1-001`: Corrección final de lenguaje científico previo al paper.

---

## 12. VERIFICACIÓN DE REGLAS DE INTEGRIDAD (INTEGRITY CHECK)

* **Hash SHA256 del Holdout**: `85e3a856e5a1334d53084f242fff50a92c1c662fe1d4c8797053261578d2b335` (**VERIFICADO INTACTO**).
* **Modificaciones a F10 / F11**: **0**.
* **Re-evaluaciones de F11 / F12**: **0**.
* **Modificaciones de coordenadas ROI**: **0**.
* **Modificaciones de resultados numéricos**: **0**.
* **Eliminación de observaciones incómodas**: **0**.
