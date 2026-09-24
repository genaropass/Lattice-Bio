# Plan de Implementación — MorphoEngine
### Motor de Biomarcadores Computacionales por Análisis Fractal

**Objetivo real:** Producir un paper científico que valide la metodología, y construir
una base técnica reutilizable para aplicar análisis fractal a múltiples enfermedades
neurológicas y sistémicas.

---

## Visión del Proyecto (Reencuadre)

No es una app. Es una **metodología científica computacional** con dos horizontes:

| Horizonte | Qué es | Timeline |
|-----------|--------|----------|
| **Corto plazo** | Paper: fractales para pérdida ósea periodontal | 3-4 meses |
| **Mediano plazo** | Expandir la metodología a enfermedades neurológicas (TDAH, ELA, EM) | 6-18 meses |
| **Largo plazo** | Plataforma de detección temprana de patrones patológicos | 2+ años |

> [!IMPORTANT]
> El branch dental **no es el destino**, es el **vehículo**. Es el primer experimento
> porque tenés datos, acceso a validación clínica real, y es ejecutable en semanas.
> Pero la visión verdadera es la neurológica.

---

## Por qué Neurológico es el Objetivo Correcto

Las enfermedades que mencionás (TDAH, ELA, Esclerosis Múltiple) comparten algo:

- **Todas degradan estructuras que son fractales por naturaleza** — redes axonales,
  mielina, conectividad funcional cerebral.
- Todas son diagnosticadas tarde o con mucha subjetividad clínica.
- Todas carecen de **biomarcadores cuantitativos objetivos** accesibles.

Los fractales son matemáticamente adecuados para medir degradación de estructuras
complejas antes de que sea visible a ojo clínico.

| Enfermedad | Qué degrada | Señal fractal posible |
|-----------|-------------|----------------------|
| **TDAH** | Conectividad funcional / dinámica EEG | HFD, Katz FD, Permutation Entropy |
| **ELA** | Red de neuronas motoras / EMG | Dimensión de correlación, LZC |
| **Esclerosis Múltiple** | Mielina (sustancia blanca) en MRI | D₀ en lesiones de MRI, lacunaridad |
| **Periodontal (base)** | Trabeculado óseo alveolar | D₀, Λ, f(α) en radiografías |

---

## Estructura del Paper (Objetivo Tangible)

**Título tentativo:**
> *"Hybrid Computational Biomarkers for Periodontal Bone Loss Staging:
> Combining Deep Vision Embeddings with Fractal Geometry and Topological Data Analysis"*

**Estructura clásica (IMRAD):**

1. **Introduction** — Gap en la literatura (PubMed 41828058), hipótesis
2. **Methods** — Pipeline: segmentación → fractales → CNN embeddings → fusión → ML
3. **Results** — Tabla comparativa: CNN sola vs. CNN + Fractales. AUC, F1, p-value
4. **Discussion** — ¿Qué métricas fractales aportan más? ¿Cuándo mejoran sobre CNN sola?
5. **Conclusion** — Relevancia clínica, limitaciones, trabajo futuro (→ neuro)

**Target de publicación:** arXiv (preprint) primero → luego journal como
*Computer Methods and Programs in Biomedicine* o *Scientific Reports*.

---

## Fases de Implementación

### 🔬 Fase 1 — Dataset & Preprocesamiento (Semanas 1-2)

**Objetivo:** Tener datos listos y pipeline de preprocesamiento funcionando.

#### Tareas:
- Descargar y explorar **Tufts Dental Dataset** (panorámicas con anotaciones)
- Descargar **DENTEX** (segmentación dental, 4000+ imágenes)
- Implementar `src/preprocessing/contrast_normalization.py`:
  - CLAHE (Contrast Limited Adaptive Histogram Equalization)
  - Normalización de intensidad entre fuentes/equipos distintos
- Implementar `src/segmentation/bone_segmenter.py`:
  - Usar SAM (Segment Anything Model de Meta) o una U-Net preentrenada
  - Extraer ROI de la región interproximal (donde ocurre pérdida ósea)
- **Entrevista con la odontóloga:** ¿Qué marcas visualmente en una radiografía? ¿Qué te gustaría medir objetivamente?

> [!NOTE]
> La entrevista clínica con tu hermana no es secundaria — es el corazón de la
> validación. El paper va a citar ese proceso de validación experta.

---

### 🧮 Fase 2 — Motor Fractal Core (Semana 2-3)

**Objetivo:** Implementar todas las métricas fractales sobre ROIs de hueso.

#### [NEW] `src/fractal/box_counting.py`
- `compute_D0(roi)` → Dimensión fractal D₀ por regresión log-log
- `oscillation_index(residuals)` → Índice de Lapidus (oscilaciones en el log-log)

#### [NEW] `src/fractal/lacunarity.py`
- `compute_lacunarity(roi, box_sizes)` → Λ(r) (Allain & Cloitre 1991)

#### [NEW] `src/fractal/multifractal.py`
- `compute_multifractal_spectrum(roi)` → f(α), D_q, Δα (Chhabra & Jensen 1989)
- Δα = α_max − α_min → cuantifica heterogeneidad estructural

#### [NEW] `src/fractal/tda_features.py`
- `compute_betti_numbers(roi)` → β₀ (componentes), β₁ (ciclos) con `ripser`
- `betti_ratio()` → indicador de fragmentación trabecular

#### [NEW] `src/fractal/feature_extractor.py`
- Orquestador: recibe un ROI y devuelve un vector de features `[D0, λ, Δα, β0, β1, osc_idx]`

---

### 🤖 Fase 3 — Benchmark Comparativo (Semana 3-4)

**Objetivo:** Responder la pregunta científica central del paper.

#### Tres experimentos:
```
Exp. 1: Solo Features Fractales      → XGBoost
Exp. 2: Solo CNN Embeddings (DINOv2) → XGBoost  
Exp. 3: Fractales + CNN Embeddings   → XGBoost  ← hipótesis: este gana
```

**Métricas reportadas en el paper:**
- AUC-ROC con intervalo de confianza (bootstrap)
- F1-Score por clase (sano / leve / moderado / severo)
- Test estadístico: DeLong test entre curvas ROC
- Feature importance: ¿qué métricas fractales aportan más?

#### [NEW] `notebooks/03_benchmark.ipynb`
- Tabla comparativa lista para copiar al paper
- Curvas ROC superpuestas
- Violin plots de distribución de features por clase

---

### 📊 Fase 4 — Validación Clínica & Visualización (Semana 4-5)

**Objetivo:** Que la odontóloga valide que los outputs tienen sentido clínico.

#### [NEW] `src/reporting/dashboard.py` (Streamlit)
- Upload de radiografía
- Visualización: imagen original → ROI segmentado → heatmap de densidad fractal
- Panel de métricas: D₀, Λ, Δα, β₀/β₁
- Índice de Salud Trabecular (score 0-100 normalizado)

#### Sesión de validación:
- Mostrarle a tu hermana 15-20 casos del dataset sin decirle los scores
- Pedirle que los ordene de más a menos enfermo
- Correlacionar su ranking con los scores del sistema → si coinciden, la validación clínica está

---

### 📝 Fase 5 — Redacción del Paper (Semanas 5-8)

**Objetivo:** Preprint en arXiv.

**Plantilla a usar:** IEEE two-column o Elsevier single-column según el journal target.

- Redactar sección Methods (la más técnica, requiere más tiempo)
- Redactar Results con las tablas del benchmark
- Redactar Introduction citando el gap de PubMed 41828058
- Revisar con la odontóloga la sección de relevancia clínica
- Subir a arXiv antes de mandar a journal → visibilidad inmediata

---

### 🧠 Fase 6 — Branch Neurológico (Meses 3-6)

**Objetivo:** Aplicar la misma metodología a señales neurológicas.

**Estrategia:** El motor fractal ya está construido. Lo que cambia es el input y el
preprocesamiento.

#### Orden sugerido de ataque por enfermedad:

| Prioridad | Enfermedad | Por qué primero | Datos |
|-----------|-----------|-----------------|-------|
| 1 | **Esclerosis Múltiple** | Los datos son imágenes MRI (mismo dominio que el dental). Las lesiones en sustancia blanca son estructuras fractales analizables con el mismo motor. | OASIS-3, MS-SEG, lesionBrain |
| 2 | **TDAH** | EEG bien estudiado, datasets públicos, clara ventana de monetización (monitoreo de tratamiento) | TUEG, EEGBCI |
| 3 | **ELA** | Más complejo (EMG + MRI), menor cantidad de datos públicos, pero el impacto es enorme | ALS-DB |

> [!NOTE]
> **Esclerosis Múltiple primero** — no EEG. Las lesiones desmielinizantes en MRI
> son exactamente el mismo tipo de análisis morfológico que el trabeculado óseo.
> Podés reutilizar el 80% del código. Es el paso natural después del paper dental.

---

## Stack Tecnológico

| Capa | Tecnología |
|------|-----------|
| Lenguaje | Python 3.10+ |
| Fractales | `scikit-image`, `numpy`, `scipy` |
| TDA | `ripser`, `persim` |
| Segmentación | `segment-anything` (SAM) o U-Net preentrenada |
| DL Embeddings | `timm` (DINOv2), `torch` |
| ML Fusion | `xgboost`, `scikit-learn` |
| Visualización | `matplotlib`, `seaborn`, `plotly` |
| Dashboard | `streamlit` |
| Reportes | `reportlab` |
| Paper | LaTeX (Overleaf) |

---

## Estructura del Repositorio

```
morpho-engine/
├── data/                    # gitignored — datasets descargados
├── notebooks/
│   ├── 01_dental_eda.ipynb
│   ├── 02_fractal_exploration.ipynb
│   └── 03_benchmark.ipynb
├── src/
│   ├── preprocessing/       # CLAHE, normalización
│   ├── segmentation/        # segmentación de ROI (dental / neuro)
│   ├── fractal/             # motor fractal (agnóstico al dominio)
│   │   ├── box_counting.py
│   │   ├── lacunarity.py
│   │   ├── multifractal.py
│   │   └── tda_features.py
│   ├── fusion/              # XGBoost / MLP sobre features combinados
│   └── reporting/           # Streamlit dashboard + PDF
├── paper/                   # LaTeX del paper
├── tests/
├── requirements.txt
└── README.md
```

---

## 📚 Qué Estudiar para Crecer Este Proyecto

### Prioridad Inmediata (primeras 4 semanas)

| Qué | Por qué | Recurso |
|-----|---------|---------|
| **Geometría fractal aplicada** | Base matemática del proyecto | *The Science of Fractal Images* — Peitgen & Saupe |
| **Topological Data Analysis** | Para entender el TDA que ya usás | *Edelsbrunner & Harer — Computational Topology* (libre en web) |
| **Cómo escribir un paper científico** | El objetivo inmediato es publicar | *How to Write and Publish a Scientific Paper* — Day & Gastel |
| **Estadística para ciencias médicas** | Para el benchmark y el paper | Fawcett 2006 (ROC curves), DeLong 1988 (comparar AUCs) |

### Prioridad Media (meses 2-4)

| Qué | Por qué | Recurso |
|-----|---------|---------|
| **Procesamiento de señales EEG** | Para el branch de TDAH y EEG | *Analyzing Neural Time Series Data* — Mike X Cohen (libre en PDF) |
| **Neuroimaging (MRI/fMRI)** | Para el branch de Esclerosis Múltiple | *Introduction to Neuroimaging Analysis* — FSL course (libre) |
| **Deep Learning for Medical Imaging** | Mejorar la capa CNN del pipeline | *Medical Image Analysis* — MIT OpenCourseWare |
| **XGBoost & Interpretabilidad (SHAP)** | Para explicar qué features importan en el paper | Documentación oficial + SHAP library |

### Prioridad Estratégica (para crecer el proyecto)

| Qué | Por qué | Recurso |
|-----|---------|---------|
| **Regulación de IA médica (ANMAT / FDA)** | Saber qué necesitás para eventualmente productizar | FDA AI/ML Action Plan (libre) |
| **Cómo postular a FONTAR** | Financiamiento real en Argentina para I+D | ANPCyT.gob.ar |
| **Scientific writing en inglés** | Todos los papers van en inglés | Writing in the Sciences — Coursera (Stanford, gratis) |

---

## Timeline Resumido

```
Semanas 1-2  →  Dataset dental + preprocesamiento + segmentación
Semanas 2-3  →  Motor fractal implementado y corriendo sobre datos reales
Semana 3-4   →  Benchmark comparativo + validación con odontóloga
Semanas 5-8  →  Redacción y publicación del paper en arXiv
Mes 3        →  Submitir a journal + iniciar branch EM (Esclerosis Múltiple)
Mes 4-6      →  Branch neurológico: EM → TDAH → ELA
Mes 6+       →  FONTAR / incubadora + prototipo de producto B2B
```

---

## Criterios de Go / No-Go del Paper

- AUC del modelo híbrido > 0.75
- Los fractales aportan ≥ 3% AUC sobre CNN sola (con p-value < 0.05)
- La odontóloga confirma relevancia clínica de los mapas visuales

Si no se cumplen → el paper **igual se escribe** pero como análisis negativo honesto
(los análisis negativos rigurosos también se publican y son valiosos metodológicamente).
