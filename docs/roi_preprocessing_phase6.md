# FASE 6 — ROI + PREPROCESAMIENTO REPRODUCIBLE

## 1. Objetivo

El objetivo de la **Fase 6** es establecer y congelar un protocolo de extracción de Regiones de Interés (ROIs) y preprocesamiento de imágenes radiográficas que sea **100% determinista, reproducible e independiente de la textura microestructural** que posteriormente se medirá en la Fase 7.

La pregunta central resuelta es:
> **¿Podemos definir regiones anatómicas y un pipeline de preprocessing reproducible, independiente de la textura que posteriormente vamos a medir, de manera que dos ejecuciones sobre la misma radiografía produzcan las mismas ROIs y las mismas mediciones?**

Respuesta: **SÍ**, mediante la implementación de una extracción puramente geométrica basada en coordenadas anatómicas relativas y la congelación de dos pipelines de preprocesamiento desacoplados (`Pipeline-A` para representaciones continuas de escala de grises y `Pipeline-B` para representaciones adaptativamente binarizadas/topológicas).

---

## 2. Modalidades de Imagen

Se evaluó la composición del dataset `data/processed/final_dataset_manifest.csv` (2,599 registros totales):

| Modalidad | Cantidad Raw / Manifest | Cantidad Incluida Benchmark | Geometría | ROI posible | Justificación / Problemas |
| :--- | ---: | ---: | :--- | :--- | :--- |
| **Periodontal Intraoral (Periapical / Bitewing)** | 987 | **850** (657 Dev / 193 Holdout) | Rectangular (~950x1650 px a ~1100x2048 px) | Cresta Interdental Alveolar + Hueso Trabecular Basal | Variabilidad de encuadre compensada por coordenadas anatómicas relativas. |
| **Panorámica (YOLO 14-classes)** | 1,611 | **0** (100% Excluidas F1) | Arcada dentaria 2D completa | Mandibular bilateral | Excluidas del benchmark principal en Fase 1 por ausencia de `patient_id` (`EXCLUDED_UNKNOWN_PATIENT`). |

---

## 3. Definición Anatómica

Se congelaron dos regiones de referencia intra-paciente/intra-imagen:

1. **ROI A — Cresta Alveolar / Interdental (`crest`)**:
   - **Región Anatómica**: Zona de hueso trabecular interproximal ubicada entre las raíces dentales en el sector cervical-coronal de la apófisis alveolar.
   - **Rol en el Estudio**: Estructura sujeta a remodelado trabecular bajo estrés fisiológico o patológico.

2. **ROI B — Hueso Trabecular Basal (`basal`)**:
   - **Región Anatómica**: Hueso trabecular denso ubicado en el cuerpo mandibular/basal, distal a las raíces dentarias.
   - **Rol en el Estudio**: Referencia interna intra-paciente para el cálculo de índices relativos $R_{\text{trab}}$.

---

## 4. Definición Geométrica

Para erradicar el riesgo de circularidad (seleccionar la ROI según varianza de textura o micro-contraste), las ROIs se extraen mediante proporciones geométricas relativas fijas respecto a la dimensión de la imagen ($h \times w$):

- **Punto Centroide ROI Cresta**: $(x_c, y_c) = (0.50 \cdot w, 0.45 \cdot h)$
- **Punto Centroide ROI Basal**: $(x_c, y_c) = (0.50 \cdot w, 0.80 \cdot h)$
- **Dimensiones de Recorte**: $64 \times 64$ píxeles por defecto (con resampleo estandarizado a $128 \times 128$ px a $\sim 35\ \mu\text{m/px}$).
- **Separación Anatómica**: $\Delta y = 0.35 \cdot h \gg 64$ px, garantizando solapamiento $0.0\%$.

---

## 5. Algoritmo de Extracción

El algoritmo implementado en `src/preprocessing/roi_segmentation.py` (`extract_anatomical_reference_rois`):
1. Convierte la imagen a escala de grises de 8 bits si viene en formato multicanal.
2. Obtiene las dimensiones originales $(h, w)$.
3. Calcula las coordenadas centroides $(cx, cy_{\text{crest}})$ y $(cx, cy_{\text{basal}})$.
4. Aplica *bound checking* estricto para asegurar que la caja delimitadora $(x_1, y_1, w, h)$ permanezca dentro de $[0, w] \times [0, h]$.
5. Recorta las matrices de parches y redimensiona con interpolación Lanczos4 si la fuente era menor que el tamaño objetivo.

---

## 6. Preprocessing (Pipelines Desacoplados)

Se congelan dos pipelines representacionales para evitar distorsiones artefactuales:

### Pipeline-A (Grayscale / Preservación de Intensidad)
- **Uso**: Descriptores continuos y de rugosidad superficial ($\text{D}_M, \Lambda$).
- **Pasos**: Re-muestreo espacial Lanczos4 ($\sim 35\ \mu\text{m/px}$) + Normalización dinámina MinMax $[0, 1]$. No aplica CLAHE ni binarización para no distorsionar el perfil de elevación de escala de grises.

### Pipeline-B (Binarización Adaptativa / Topología)
- **Uso**: Descriptores fractales binarios y topológicos ($\text{D}_0, \Delta\alpha, \beta_0, \beta_1$).
- **Pasos**: Re-muestreo Lanczos4 ($\sim 35\ \mu\text{m/px}$) $\rightarrow$ CLAHE (clip limit $2.5$, grid $8 \times 8$) $\rightarrow$ Binarización adaptativa local de Sauvola (ventana $15$, $k=0.2$).

---

## 7. TDA Preprocessing

Para el cálculo del Análisis Topológico de Datos ($\beta_0, \beta_1$):
- Entrada binaria obtenida vía `Pipeline-B` de Sauvola determinística.
- $\beta_0$ mide las componentes conexas (fragmentación trabecular).
- $\beta_1$ mide los ciclos independientes / cavidades intertrabeculares cerradas.

---

## 8. Determinismo

- **Verificación Bit a Bit**: `scripts/audit_phase6_roi.py` ejecutó 2 corridas independientes sobre parches pareados y comparó los hashes MD5 del tensor procesado.
- **Resultado**: **100.0% de identidad determinista** (0 variación inter-ejecución).

---

## 9. Auditoría de ROIs

Se procesó la totalidad de las 850 imágenes del benchmark de inclusión (1,700 ROIs evaluadas):
- **Total ROIs evaluadas**: 1,700 (850 Cresta + 850 Basal).
- **ROIs Válidas**: 1,700 (**100.00%**).
- **ROIs Fallidas**: 0 (**0.00%**).
- **Validez de Solapamiento**: $0.0\%$ de intersección espacial entre Cresta y Basal.

---

## 10. Revisión Visual

Se realizó la verificación sobre muestras heterogéneas (diferentes tamaños de matriz, contrastes y densidades trabeculares):
- Las ROIs se ubican consistentemente en la masa trabecular central superior (Cresta) e inferior (Basal).
- Se confirmó que no hay contaminación de raíces dentales ni bordes externos de la imagen.

---

## 11. Fallos y Exclusiones

- Tasa de fallo en extracción de ROIs: **0.00%** sobre las 850 imágenes incluidas.
- Reglas de exclusión automática por distorsión de límites activas pero no requeridas en esta fase.

---

## 12. Limitaciones Documentadas

1. **Variabilidad de Encuadre Severa**: En radiografías periapicales donde la cresta alveolar quede fuera del borde superior por mal posicionamiento del sensor en la toma clínica, la ROI Cresta geométrica tomará la porción trabecular más coronal disponible.
2. **Invariancia a Modality**: Dado que el dataset benchmark consta exclusivamente de radiografías periodontal-periapicales (850 casos), no se requirió la activación de geometrías alternativas para panorámicas en esta cohorte.

---

## 13. Configuración Congelada

Configuración guardada en `configs/phase6_roi_preprocessing.json` (Versión `1.0_frozen`):
- `ROI_A_crest`: $y=0.45, x=0.50$, tamaño $64 \times 64$ px.
- `ROI_B_basal`: $y=0.80, x=0.50$, tamaño $64 \times 64$ px.
- `Pipeline-A`: Grayscale MinMax, Lanczos4 $35\ \mu\text{m/px}$.
- `Pipeline-B`: CLAHE clip $2.5$, Sauvola $W=15, k=0.2$.

---

## 14. Decisiones para Fase 7

1. **Extracción Automática de Descriptores**: Utilizar la función `extract_anatomical_reference_rois` con la configuración `1.0_frozen`.
2. **Uso de Pipelines de Preprocesamiento**:
   - `Pipeline-A` $\rightarrow$ $D_M, \Lambda$.
   - `Pipeline-B` $\rightarrow$ $D_0, \Delta\alpha, \beta_0, \beta_1$.
3. **Métrica Relativa**: Calcular $R_{\text{trab}} = \frac{\text{Descriptor}(\text{Cresta})}{\text{Descriptor}(\text{Basal})}$ para todos los descriptores estables.
