# 🔬 Reporte de Auditoría de Calidad (QA) y Estado Científico — MorphoEngine Dental

**Fecha:** Septiembre 2026  
**Foco exclusivo:** Odontología / Estadificación de Pérdida Ósea Periodontal  
**Objetivo:** Elevar el software y la metodología al estándar de publicación en journals de alto impacto (*Scientific Reports*, *Computer Methods and Programs in Biomedicine*, *IEEE JBHI*).

---

## 1. 📚 Estado del Arte y Literatura Científica Relevante

Una revisión de la literatura actual sobre **Análisis Fractal y Periodoncia** revela los siguientes hallazgos clave:

1. **Dimensión Fractal ($FD / D_0$):**
   - Estudios en radiografías periapicales y panorámicas (*Updike et al.*, *MDPI 2025/2026*) demuestran que los valores de $FD$ disminuyen de manera estadísticamente significativa en pacientes con periodontitis respecto a controles sanos ($p < 0.001$).
   - La caída de $FD$ refleja la pérdida de complejidad del entramado trabecular debido a la reabsorción inflamatoria.

2. **Lacunaridad ($\Lambda$) como complemento de $FD$:**
   - La literatura (*Journal of Clinical Periodontology*, *NIH PubMed*) confirma una **correlación inversa entre $FD$ y Lacunaridad**.
   - A medida que avanza la pérdida ósea, la dimensión fractal disminuye mientras que la lacunaridad aumenta bruscamente debido a la aparición de "lagunas" o grandes poros de reabsorción.

3. **Gaps de la Literatura Actual (Nuestra Oportunidad Científica):**
   - **Dependencia de la Binarización:** La mayoría de los estudios usan ImageJ con umbrales fijos o Otsu global, perdiendo matices de desmineralización temprana.
   - **Falta de Descriptores Topológicos:** Ningún paper relevante integra Homología Persistente (Números de Betti $\beta_0, \beta_1$) ni oscilaciones de Lapidus.
   - **Ausencia de Modelos Híbridos:** Existe un vacío en la combinación de Visión Profunda (embeddings DINOv2) + Fractales 3D (Manta de Minkowski) + TDA.

---

## 2. 🛡️ Auditoría de Calidad de Código (QA Report)

Se realizó una revisión exhaustiva de edge cases, estabilidad numérica y rendimiento sobre los módulos principales:

| Módulo | Pruebas de QA Realizadas | Estado | Resultado |
|---|---|---|---|
| **`contrast_normalization.py`** | Imágenes de tamaño < 10x10, imágenes vacías (std=0), imágenes en color RGBA. | **PASÓ** | Agregado de grilla adaptativa CLAHE y Sauvola seguro. |
| **`minkowski.py`** | Superficies planas (std=0), rangos de intensidad desacoplados del grid espacial. | **PASÓ** | Normalización espacial de intensidad aplicada; $D_{Minkowski} \in [2.0, 3.0]$. |
| **`local_heatmap.py`** | Imágenes más pequeñas que la ventana deslizante, strides impares, pad de bordes. | **PASÓ** | Resampling bicúbico estable e interpolación sin artefactos visuales. |
| **`feature_extractor.py`** | ROIs totalmente vacíos (0 píxeles activos) o completamente llenos. | **PASÓ** | Fallbacks limpios retornando 0.0/2.0 sin lanzar excepciones ni `NaN`. |
| **`pdf_report.py`** | Generación de informes con datos faltantes o cadenas vacías. | **PASÓ** | Construcción exitosa de PDFs clínicos formales con ReportLab. |

---

## 3. 🎯 Ventajas Metodológicas del Sistema Construido

```
         PIPELINE DE INNOVACIÓN MORPHOENGINE
         
  [Radiografía Dental] ──► [CLAHE + Sauvola]
                                │
   ┌────────────────────────────┼────────────────────────────┐
   ▼                            ▼                            ▼
[Manta de Minkowski 3D]    [Heatmap Local RGB]        [TDA - Betti]
(Analiza grises sin        (Visualización Verde/      (Mide conectividad
binarizar desmineraliz.)    Amarillo/Rojo)            y fragmentación)
   │                            │                            │
   └────────────────────────────┼────────────────────────────┘
                                ▼
                   [FUSIÓN DE CARACTERÍSTICAS]
                                │
                                ▼
           [ÍNDICE CUANTITATIVO DE SALUD TRABECULAR]
```

---

## 4. 📋 Checklist para la Redacción del Paper

- [x] **Base Matemática Implementada y Testeada:** Box-Counting, Minkowski, Lacunaridad, Multifractal, TDA.
- [x] **Motor de Visualización Clínico:** Heatmap local superpuesto.
- [x] **Protocolo de Benchmark Implementado:** K-Fold CV estratificado (`feature_fusion.py`).
- [ ] **Descargar Dataset Final (Tufts / DENTEX / Muestras Clínicas):** Para entrenar y generar la matriz de confusión y curvas ROC definitivas.
- [ ] **Entrevista de Validación Clínico-Odontológica:** Validar los heatmaps con la odontóloga.
