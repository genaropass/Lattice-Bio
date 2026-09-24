# 🔬 Lattice Bio: Motor de Biomarcadores Computacionales por Análisis Fractal

**Lattice Bio** es una plataforma científica y modular para la extracción de biomarcadores cuantitativos de microarquitectura y complejidad estructural mediante **Geometría Fractal**, **Análisis Topológico de Datos (TDA)** y **Visión por Computadora Híbrida**.

Diseñado inicialmente para la estadificación temprana de la **pérdida ósea trabecular periodontal**, con extensibilidad metodológica hacia la cuantificación de lesiones en **Esclerosis Múltiple**, **TDAH (dinámica EEG)** y **ELA**.

---

## 🏛️ Arquitectura del Sistema

```
IMAGEN / RADIOGRAFÍA / SEÑAL
              │
              ▼
    [PREPROCESAMIENTO & ROI]
  (CLAHE, Normalización, Sauvola)
              │
      ┌───────┴───────┐
      ▼               ▼
┌──────────────┐    ┌─────────────────────────────────┐
│ VISIÓN DL    │    │ MOTOR FRACTAL & TOPOLÓGICO      │
│ (DINOv2/CNN) │    │ • Manta de Minkowski 3D (D_M)   │
│ Embeddings   │    │ • Dimensión Fractal (D₀)        │
│              │    │ • Espectro de Lacunaridad (Λ)   │
│              │    │ • Heatmaps Locales (RGB)        │
│              │    │ • Homología Persistente (β₀, β₁)│
└──────┬───────┘    └────────────────┬────────────────┘
       │                             │
       └──────────────┬──────────────┘
                      ▼
            FEATURE FUSION (XGBoost)
                      │
                      ▼
    [BIOMARCADOR CUANTITATIVO DE SALUD]
                      │
                      ▼
         REPORTE MÉDICO & DASHBOARD
```

---

## 📁 Estructura del Proyecto

```
├── src/
│   ├── preprocessing/      # Normalización, filtros CLAHE, extracción de ROI
│   ├── fractal/            # Motor matemático (Minkowski 3D, Box-Counting, Lacunaridad, Heatmaps, TDA)
│   ├── neuro/              # Módulo de procesamiento de señales (Higuchi FD, Hurst)
│   ├── fusion/             # Fusión de características y modelos de ML (XGBoost)
│   └── reporting/          # Generación de reportes PDF y Dashboard interactivo (Streamlit)
├── tests/                  # Tests unitarios matemáticos y de integración
├── notebooks/              # Exploración y benchmarks comparativos
├── data/                   # Datasets (Tufts, DENTEX, etc. - gitignored)
├── requirements.txt
└── README.md
```

---

## 🚀 Instalación y Uso Rápido

```bash
# Crear entorno virtual
python -m venv .venv
# Activar en Windows
.venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar tests matemáticos unitarios
python -m unittest discover tests

# Lanzar Dashboard Interactivo
streamlit run src/reporting/dashboard.py
```
