# Documento de Transferencia de Contexto & Blueprint de Proyecto

Este documento reúne todo el trabajo, código y modelos desarrollados en **DigPatho**, junto con la estrategia completa para el nuevo proyecto de **Análisis Fractal & IA Dental**. Sirve como archivo de handover para copiar al nuevo espacio de trabajo.

---

## 📌 PARTE 1: Resumen de Trabajo & IP Desarrollada en DigPatho

### 1. Modelo de Clasificación PAAF (8 Clases)
- **Modelo:** `best_paaf.pt` (`yolov8n-cls`)
- **Precisión:** **96.03% Top-1 Accuracy / 100% Top-5**
- **Clases (8):** `carcinoma`, `histiocitoma`, `linfoma`, `mastocitoma`, `melanoma`, `negativo_inflamatorio`, `plasmocitoma`, `tvt`.
- **Dataset de Entrenamiento:** 20.000 imágenes ($320 \times 320$ px) combinadas de CytoCanine (Kaggle) + recortes de Whole Slide Images del dataset CATCH.

### 2. Filtros Morfométricos y Cromáticos Creados
- **`stain_filtering.py`:** 
  - Binarización Otsu adaptativa sobre el canal basófilo (Verde/HSV) para aislar núcleos púrpuras.
  - `es_celula_nucleada(crop)`: Elimina el 100% de eritrocitos anucleados (glóbulos rojos) y detritos de fondo.
- **Relación Núcleo/Citoplasma ($N:C$ Ratio):**
  - `calcular_nc_ratio(crop)`: Si $N:C < 0.15$ (núcleo pequeño respecto al citoplasma, característico de leucocitos maduros/células sanas), reclasifica como `negativo_inflamatorio`.
- **Umbral de Confianza Estricto:** `MIN_CELL_CONF = 0.65` ($65\%$ de certeza mínima para cajas borrador).

### 3. Aprendizaje Activo (Active Learning Feedback Loop)
- **`feedback_service.py` + Endpoint `POST /api/v1/analyze-citologia/feedback`:** 
  - Guarda automáticamente los recortes corregidos por el patólogo en `dataset_feedback/{clase_corregida}/`.
- **`retrain_with_feedback.py`:** Script de 1-click para fusionar el feedback y reentrenar `best_paaf.pt` en GPU.

### 4. Plataforma de Telepatología Humano en el Bucle (TELE-1..10)
- **Esquema Prisma & Backend (`schema.prisma`, `telepathology_service.py`, `pedidos.py`):**
  - Ciclo de vida: `BORRADOR` → `ENVIADO` → `EN_REVISION` → `DIAGNOSTICADO` → `VISTO_POR_VET`.
  - Roles `VETERINARIO` y `PATOLOGO`.
  - Pre-anotación silenciosa de la IA al subir el pedido.
- **Frontend Vistas (`nuevo/page.tsx`, `inbox/page.tsx`, `pedido/[id]/page.tsx`, `mis-diagnosticos/page.tsx`):**
  - Flujo completo de carga por el veterinario, bandeja de entrada para la patóloga (Carina), visor de edición e informe final.

---

## 📌 PARTE 2: Blueprint del Nuevo Proyecto (IA Fractal Dental)

### 🎯 1. La Tesis del Proyecto
**"Desarrollo de Biomarcadores Computacionales de Estructura Ósea mediante Geometría Fractal, Visión por Computadora y Machine Learning para Pérdida Ósea Periodontal."**

- **Por qué no es "otra app de caries":** Las caries son opacidades binarias. La periodontitis es la **degradación de la red trabecular del hueso alveolar**, la cual es una estructura fractal autosimilar por definición física.
- **La hipótesis científica:** La dimensión fractal y lacunaridad de la red trabecular sufren cambios microestructurales **antes de que la pérdida de volumen óseo sea visible a simple vista** en una radiografía.

### 🏗️ 2. Arquitectura Propuesta (`MorphoEngine`)

```
RADIOGRAFÍA DENTAL (Panorámica / Periapical)
                    │
                    ▼
       [SEGMENTACIÓN DE HUESO Y DIENTES]
             (Tufts / DENTEX / U-Net)
                    │
        ┌───────────┴───────────┐
        ▼                       ▼
┌──────────────┐      ┌──────────────────┐
│ VISIÓN DL    │      │ MOTOR FRACTAL    │
│ (DINOv2/CNN) │      │ • Minkowski 2D   │
│ Embeddings   │      │ • Dim. Fractal   │
│              │      │ • Lacunaridad    │
└───────┬──────┘      └────────┬─────────┘
        │                      │
        └───────────┬──────────┘
                    ▼
           FEATURE FUSION (XGBoost / MLP)
                    │
                    ▼
  [BIOMARCADOR CUANTITATIVO DE SALUD TRABECULAR]
```

### 🏆 3. Las 3 Ventajas Competitivas
1. **Acceso a Datos:** Datasets públicos masivos de radiografías dentales disponibles hoy (Tufts, DENTEX, ISBI).
2. **Defendibilidad Científica:** Combinación de geometría fractal + visión por computadora (publicable en paper y financiable por VCs/Incubadoras).
3. **Canal de Validación Clínica Real:** Tu hermana (odontóloga), que provee feedback de usabilidad y prueba clínica desde el día 1.

---

## 🗓️ PARTE 3: Plan de Ejecución de 4 Semanas (Sprint Inicial)

- **Semana 1: Configuración de Dataset & Preprocesamiento**
  - Descargar dataset público de radiografías dentales (Tufts / DENTEX).
  - Configurar pipeline de normalización de contraste y extracción de ROI de hueso trabecular.
- **Semana 2: Feature Engine Fractal 2D**
  - Adaptar las funciones de **Manta de Minkowski**, **Dimensión Fractal (Box-Counting)** y **Lacunaridad** para actuar sobre la matriz trabecular de la radiografía.
- **Semana 3: Benchmark Comparativo**
  - Evaluar: `CNN pura` vs. `CNN + Características Fractales + XGBoost`.
  - Medir si los fractales mejoran el AUC / F1-Score en la caracterización del hueso.
- **Semana 4: Validación con Experto & Decisión Estratégica**
  - Presentar los mapas de densidad fractal a tu hermana odontóloga para validar la relevancia clínica.
  - Decidir avance hacia prototipo/paper/startup.
