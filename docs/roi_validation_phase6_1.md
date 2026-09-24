# FASE 6.1 — VALIDACIÓN ANATÓMICA Y CIENTÍFICA DEL ROI

## 1. Scope

### Lo que se auditó
- **Validez anatómica** de las coordenadas geométricas fijas de la ROI A (Cresta) y la ROI B (Basal).
- **Auditoría visual anotada** en una muestra representativa estratificada del dataset Development (30 imágenes).
- **Calibración física vs muestreo digital** del parámetro de escala nominal (`35 μm/px`).
- **Compatibilidad metodológica y matemática** entre el preprocesamiento de la Fase 6 (`Pipeline-A` y `Pipeline-B`) y las definiciones de los 6 descriptores auditados en la Fase 4.1 ($D_0, D_M, \Lambda, \Delta\alpha, \beta_0, \beta_1$).
- **Independencia de textura** y ausencia de circularidad en la función de localización de ROIs.

### Lo que NO se auditó
- **NO se entrenaron modelos predictivos.**
- **NO se calculó AUC ni métricas de clasificación.**
- **NO se utilizaron etiquetas clínicas de enfermedad.**
- **NO se accedió al conjunto Holdout** (congelado e intacto, SHA256 `85e3a856...`).

---

## 2. Dataset Utilizado

- **Dataset de Evaluación**: Exclusivamente las 657 imágenes pertenecientes al split `Development` del dataset `Periodontal` intraoral (Khatibi et al.).
- **Holdout Set**: 193 imágenes totalmente intocadas e inalteradas.
- **Total Registros del Manifest**: 2,599 registros en `data/processed/final_dataset_manifest.csv` (1,611 panorámicas excluidas por falta de Patient ID en Fase 1, 987 periapicales de las cuales 850 forman el benchmark principal).

---

## 3. ROI Definition (Definición Geométrica Vigente)

- **ROI A — Cresta Alveolar / Interdental (`crest`)**:
  - Coordenada centroide relativa: $(x, y) = (0.50 \cdot w, 0.45 \cdot h)$
  - Dimensiones por defecto: $64 \times 64$ píxeles
  - Zona anatómica: Tercio medio-superior interproximal del hueso trabecular alveolar.
- **ROI B — Hueso Trabecular Basal (`basal`)**:
  - Coordenada centroide relativa: $(x, y) = (0.50 \cdot w, 0.80 \cdot h)$
  - Dimensiones por defecto: $64 \times 64$ píxeles
  - Zona anatómica: Tercio inferior del cuerpo mandibular / hueso trabecular basal.

---

## 4. Anatomical Audit (Auditoría Visual Estratificada)

Se realizó una evaluación visual directa guardando las imágenes anotadas con cuadros delimitadores y coordenadas en `data/processed/phase6_1_roi_visual_audit/` sobre una muestra de 30 imágenes del split Development:

### Criterio de Auditoría
- **`VALID`**: La ROI cae íntegramente sobre hueso trabecular en la zona relativa pretendida, sin salirse del área anatómica útil ni caer sobre el fondo.
- **`PARTIAL`**: La ROI se encuentra sobre hueso trabecular pero toca parcialmente la lámina dura/raíz o el borde del hueso por variación en el encuadre.
- **`INVALID`**: La ROI cae sobre la corona dental, restauración, aire exterior o fuera de la matriz.

### Resultados
| Tipo de ROI | Evaluadas | `VALID` | `PARTIAL` | `INVALID` | % Validez Anatómica |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **ROI A (Cresta)** | 30 | 30 | 0 | 0 | **100.0%** |
| **ROI B (Basal)** | 30 | 30 | 0 | 0 | **100.0%** |
| **Global (Par)** | 30 | 30 | 0 | 0 | **100.0%** |

---

## 5. Scale Audit (Auditoría de "35 μm/px")

Se evaluó la naturaleza exacta de la conversión de escala en `src/preprocessing/contrast_normalization.py` (`standardize_spatial_resolution`):

- **Diagnóstico**: **Caso B / Caso C (Muestreo Digital Objetivo e Hipótesis)**. No existe una calibración física real proveniente de parches DICOM o phantoms radiográficos con escala milimétrica en el dataset fuente.
- **Resolución Metodológica**: La expresión `"35 μm/px reales"` es científicamente indefendible en este dataset. Se corrige oficialmente la nomenclatura en la documentación para declarar la variable como:
  > **"Standardized Digital Resampling Grid Target (35 μm/px nominal under assumed 150 DPI detector resolution)"**
- **Impacto**: Las comparaciones de descriptores son válidas dentro del dominio digital estandarizado, pero no representan mediciones métricas físicas absolutas.

---

## 6. Descriptor Compatibility (Compatibilidad Preprocessing vs F4.1)

| Descriptor | Input en F6 | Preprocessing en F6 | Input Usado en F4.1 | ¿Compatible? | Clasificación y Análisis |
| :--- | :--- | :--- | :--- | :---: | :--- |
| **$D_0$ (Box-counting)** | Máscara Binaria | `Pipeline-B` (CLAHE $2.5$ + Sauvola $W=15, k=0.2$) | Imagen Binaria (Phantom / Sintética) | **SÍ** | `COMPATIBLE_WITH_DOCUMENTATION`. F4.1 validó $D_0$ sobre alfombra sintética binaria; $D_0$ requiere una matriz binaria determinística. |
| **$D_M$ (Minkowski)** | Escala de Grises | `Pipeline-A` (Lanczos4 + MinMax $[0,1]$) | Superficie de Intensidad 2.5D (Phantom 2D) | **SÍ** | `COMPATIBLE_WITH_DOCUMENTATION`. $D_M$ mide la superficie de la manta de intensidad 2.5D; CLAHE distorsionaría el volumen del perfil. |
| **$\Lambda$ (Lacunaridad)** | Escala de Grises | `Pipeline-A` (Escala de Grises) / `Pipeline-B` | Matriz 2D de Intensidades / Binaria | **SÍ** | `COMPATIBLE_WITH_DOCUMENTATION`. Lacunaridad por gliding box evaluada en distribución de masa. |
| **$\Delta\alpha$ (Multifractal)** | Escala de Grises / Binaria | `Pipeline-B` (Grilla Estandarizada) | Superficie 2D de Intensidad ($q \in [-5, 5]$) | **SÍ** | `COMPATIBLE_WITH_DOCUMENTATION`. El espectro multifractal de la masa trabecular utiliza la distribución de medidas locales. |
| **$\beta_0$ (Betti 0)** | Máscara Binaria | `Pipeline-B` (Sauvola $W=15, k=0.2$) | Matriz Binaria (Componentes Conexas) | **SÍ** | `COMPATIBLE_WITH_DOCUMENTATION`. Requiere binarización adaptativa determinística para evaluar 8-conectividad. |
| **$\beta_1$ (Betti 1)** | Máscara Binaria | `Pipeline-B` (Sauvola $W=15, k=0.2$) | Matriz Binaria (Ciclos Trabeculares) | **SÍ** | `COMPATIBLE_WITH_DOCUMENTATION`. Requiere binarización adaptativa determinística para contar cavidades trabeculares. |

---

## 7. Circularity Audit (Auditoría de Circularidad)

- **Evaluación**: Se inspeccionó el código fuente de `extract_anatomical_reference_rois` en `src/preprocessing/roi_segmentation.py`.
- **Resultado**: La función utiliza únicamente las dimensiones $(h, w)$ de la matriz y constantes geométricas fijas (`crest_y_ratio=0.45`, `basal_y_ratio=0.80`, `x_ratio=0.50`).
- **Dictamen**: **Circulariad 0.0%**. La selección del ROI está 100% independizada de métricas de intensidad, varianza, gradientes, $D_0, D_M, \Lambda, \Delta\alpha$, TDA o modelos de aprendizaje profundo (DINOv2).

---

## 8. Problems Found (Problemas Identificados)

1. **`IMPORTANT` — Representación de Coordenadas Relativas vs Hitos Anatómicos 3D**:
   La regla $(0.50 \cdot w, 0.45 \cdot h, 0.80 \cdot h)$ es una referencia geométrica relativa intra-imagen y no un hito anatómico 3D. Se resuelve documentándola como referencia relativa intra-imagen.
2. **`IMPORTANT` — Falta de Calibración Física para "35 μm/px"**:
   El valor es un objetivo de muestreo digital nominal ($150$ DPI asumidos), no una escala métrica real. Se resuelve corrigiendo la nomenclatura.
3. **`MINOR` — Incompatibilidad de la Regla Geométrica Fija con Radiografías Panorámicas**:
   El centro $(0.50 \cdot w, 0.45 \cdot h)$ en una radiografía panorámica completa cae sobre la espina o cavidad nasal. Se resuelve restringiendo el alcance del Paper 1 exclusivamente a radiografías periodontal-periapicales.

---

## 9. Decision Final (Dictamen Científico de Fase 6.1)

### Dictamen Oficial: **`F6.1 CLOSED_WITH_LIMITATIONS`**

#### Justificación
La definición geométrica actual de los ROIs es 100% reproducible, determinista e independiente de la textura, habiendo sido validada visualmente en el 100% de la muestra evaluada del benchmark Development. No obstante, se establecen tres **limitaciones explícitas obligatorias** para las fases subsecuentes (Fase 7 en adelante) y la redacción del Paper 1:

1. **Alcance Limitado a Radiografías Periapicales**: El estudio se restringe estrictamente a radiografías intraorales periapicales (850 imágenes de benchmark).
2. **Definición de Escala Digital**: El término `35 μm/px` se define como *"Standardized Digital Resampling Grid Target"* bajo el supuesto nominal de 150 DPI y no como escala física calibrada.
3. **Carácter de Referencia Anatómica Geométrica**: Las ROIs A y B se declaran como una grilla de referencia geométrica intra-paciente/intra-imagen, no como ground truth clínico ni diagnóstico.
