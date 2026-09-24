# Contexto y Handoff — Proyecto Fractal AI
**Documento generado:** Septiembre 2026  
**Origen:** Conversación de investigación y desarrollo durante el proyecto DigPatho / demo-her2  
**Propósito:** Servir de base y contexto completo para iniciar el nuevo proyecto independiente de análisis fractal aplicado a dominios clínicos.

---

## 1. Punto de Partida — Qué se construyó en demo-her2

Durante el trabajo en el proyecto `demo-her2` de la firma Digpatho se desarrolló una **Prueba de Concepto (PoC)** de diagnóstico de HER2 en biopsias de cáncer de mama, que combinó:

- **Análisis fractal real de imágenes de biopsia** (Dimensión Fractal D₀ + Lacunaridad)
- **Lógica difusa** (`scikit-fuzzy`) para traducir métricas numéricas a variables lingüísticas clínicas
- **Orquestación multi-agente** con LangGraph (`ConsistencyAgent`, `CEOAgent`, `ReportAgent`)
- **GraphRAG Anti-alucinación** con Neo4j + ontología ASCO/CAP 2023
- **Generación de reportes clínicos PDF** con `reportlab`
- **Dashboard interactivo** con Streamlit
- **Integración con Vertex AI** (Gemini) para síntesis narrativa

### Stack técnico del proyecto original
```
Python 3.10+  |  Docker (Neo4j 5.26)  |  LangGraph  |  scikit-image
scikit-fuzzy  |  reportlab  |  Streamlit  |  Google Cloud (Vertex AI)
```

### Archivos clave producidos en esta conversación
| Archivo | Ubicación | Descripción |
|---|---|---|
| `her2_fractal_analysis.ipynb` | `demo-her2/` | Colab completo con pipeline fractal |
| `fractal_math_reference.md` | `demo-her2/docs/` | Referencia de fórmulas matemáticas |
| `contexto_proyecto_fractal.md` | `demo-her2/docs/` | Este documento |

---

## 2. El Problema Identificado con el Sistema Actual

> **El cuello de botella:** El sistema tenía un "cerebro brillante" (multi-agente + GraphRAG) pero "ojos miopes" (procesamiento de imagen demasiado básico).

**Problema técnico concreto:**  
El pipeline original convertía la imagen a escala de grises y aplicaba umbral de Otsu global antes del análisis fractal. Esto **destruía la información clave del HER2 +1 (HER2-Low)**: la tinción DAB (marrón, membranas) es débil e incompleta en estos casos, y el umbral de Otsu la borraba, dejando solo la señal de la hematoxilina (núcleos azules). En consecuencia, la dimensión fractal medía la arquitectura nuclear, no la membrana HER2.

**Solución propuesta e implementada en el Colab:**
1. **Deconvolución de Color (Ruifrok & Johnston 2001):** Separar matemáticamente el canal DAB (señal HER2) del canal de Hematoxilina (núcleos) antes de cualquier análisis.
2. **Binarización Adaptativa Local** (en lugar de Otsu global) para capturar tinción débil e incompleta.
3. Aplicar las métricas fractales **exclusivamente sobre el canal DAB** resultante.

---

## 3. Pipeline Matemático Desarrollado

### El motor fractal construido para el Colab tiene 5 capas:

```
📦 Input: imagen IHC (.tif / .png)
    │
    ▼
🎨 Paso 1 — Deconvolución de Color (Ruifrok 2001)
    → Canal DAB (marrón/HER2) separado del canal Hematoxilina
    │
    ▼
🔲 Paso 2 — Binarización Adaptativa (umbral local)
    │
    ▼
📏 Paso 3 — Extracción de Métricas
    ├──▶ D₀ (Box-Counting)
    ├──▶ Λ(r) (Espectro de Lacunaridad)
    ├──▶ f(α) / Dq (Espectro Multifractal — Método de Momentos)
    ├──▶ Índice de Oscilación Lapidus (residuos del log-log)
    └──▶ β₀, β₁ (TDA — Persistent Homology con ripser)
    │
    ▼
📊 Paso 4 — CSV + Panel Visual para informe médico
```

---

## 4. Referencia Matemática Rápida

### 4.1 Dimensión Fractal D₀ (Box-Counting)
$$D_0 = \lim_{\varepsilon \to 0} \frac{\log N(\varepsilon)}{\log(1/\varepsilon)}$$

Regresión lineal en escala log-log. La **pendiente es D₀**.

### 4.2 Lacunaridad Λ(r) (Allain & Cloitre 1991)
$$\Lambda(r) = \frac{\langle s^2 \rangle}{\langle s \rangle^2}$$

Mide la textura de los huecos. Alta en estructuras fragmentadas e incompletas.

### 4.3 Espectro Multifractal f(α) (Chhabra & Jensen 1989)
$$D_q = \frac{1}{q-1} \lim_{\varepsilon \to 0} \frac{\log \sum_i p_i^q}{\log \varepsilon}$$

- D₀ = Dimensión de Capacidad  
- D₁ = Dimensión de Información  
- D₂ = Dimensión de Correlación  
- Δα = α_max − α_min = **ancho espectral** (cuantifica heterogeneidad)

### 4.4 Dimensiones Complejas de Lapidus
Las oscilaciones en los residuos de la regresión log-log del Box-Counting son una aproximación práctica a las dimensiones complejas de Lapidus. Se capturan con:
```python
osc_index = np.std(residuals_of_loglog_fit)
```

### 4.5 Números de Betti (TDA — Persistent Homology)
- **β₀** = componentes conectadas (fragmentos)  
- **β₁** = ciclos cerrados (anillos)  
- **Ratio β₀/(β₁+1)** → alto indica estructuras fragmentadas (compatible con HER2 1+)

---

## 5. Datasets Públicos Identificados

| Dataset | Fuente | Scores disponibles | Formato |
|---|---|---|---|
| **HER2-IHC-40x** | Zenodo | 0, 1+, 2+, 3+ | PNG (patches) |
| BCI Dataset | GitHub (bupt-ai-cz) | 0, 1+, 2+, 3+ | PNG (pares H&E + IHC) |
| ADEL Dataset | Zenodo | 0, 1+, 2+, 3+ | TIFF |
| MIST Dataset | GitHub | Múltiple | Patches |

**Para odontología:**
- Tufts Dental Dataset (panorámicas)
- DENTEX Dataset
- Datasets PANOREX de segmentación dental en PapersWithCode

**Para neurociencia (EEG/fMRI):**
- ADHD-200 (fMRI, no EEG)
- EEGBCI Dataset (Physionet)
- Temple University EEG Corpus (TUEG)

---

## 6. Análisis de Verticales para Nuevo Proyecto

Durante la conversación se analizaron en profundidad 7 verticales posibles para un proyecto/startup independiente usando el mismo stack de Computer Vision + Fractales + TDA + ML:

### Ranking final (para este perfil y momento)

| Vertical | Datos hoy | Fractales aportan | Ejecutabilidad | Potencial |
|---|---|---|---|---|
| 🦷 **Periodoncia** | ✅ Alto | ⭐⭐⭐⭐⭐ | ✅ Alta | ⭐⭐⭐⭐⭐ |
| 🧠 **Neuro/EEG** | ⚠️ Medio | ⭐⭐⭐⭐⭐ | ⚠️ Media | ⭐⭐⭐⭐⭐ |
| 👁️ **Retina Vascular** | ✅ Alto | ⭐⭐⭐⭐ | ✅ Alta | ⭐⭐⭐⭐ |
| 🌱 **Raíces AgriTech** | ✅ Alto | ⭐⭐⭐⭐ | ✅ Alta | ⭐⭐⭐⭐ |
| 🔬 **Morfología Celular** | ⚠️ Medio | ⭐⭐⭐⭐ | ⚠️ Media | ⭐⭐⭐⭐⭐ |
| 🔩 **Materiales/NDT** | ❌ Bajo | ⭐⭐⭐⭐⭐ | ❌ Baja | ⭐⭐⭐⭐⭐ |
| 🧴 **Dermatología** | ✅ Alto | ⭐⭐⭐ | ✅ Alta | ⭐⭐⭐ |

---

## 7. Las Dos Ideas Finalistas

### 🦷 Opción A — Periodoncia / Pérdida Ósea Trabecular

**La idea no es:** "IA que detecta caries" (ya existe, poco diferencial).

**La idea es:**  
> Cuantificar la microarquitectura trabecular del hueso alveolar **antes** de que la pérdida ósea sea visible radiológicamente, usando análisis fractal + TDA sobre radiografías panorámicas y periapicales.

**Por qué es diferencial:**  
- La textura trabecular cambia ANTES de que disminuya la altura ósea visualmente. Los fractales capturan esa señal sutil que una CNN sola no puede.
- Una revisión sistemática de 2026 (PubMed: 41828058) analizó 80 estudios de fractales + IA para pérdida ósea periodontal y concluyó que **falta estandarización y modelos híbridos rigurosos**. Ese hueco es la oportunidad.

**Pipeline propuesto:**
```
Radiografía
    │
    ▼
Segmentación dental (hueso alveolar)
    │
    ├──▶ CNN / DINOv2 embeddings
    └──▶ Fractal Analysis (D₀, Λ, f(α), β₀/β₁)
              │
              ▼
         Feature Fusion
              │
              ▼
         XGBoost / MLP
              │
              ▼
    Índice cuantitativo de salud ósea
```

**Ventaja de validación:** Acceso directo a profesional odontóloga para validación clínica real desde el día 1.

**Pregunta científica inicial:**
> ¿Las características fractales y morfológicas del trabeculado óseo dental aportan información estadísticamente significativa y adicional a un modelo de visión profunda para estadificar la pérdida ósea periodontal?

---

### 🧠 Opción B — Biomarcadores Fractales de Dinámica Cerebral (TDAH/Neuro)

**La idea no es:** "IA que detecta TDAH y lo cura."

**La idea es:**
> Desarrollar biomarcadores computacionales de dinámica cerebral basados en geometría fractal, teoría de la información y ML, investigando si capturan información complementaria a los métodos clásicos para caracterizar TDAH (subtipos, severidad, respuesta al tratamiento).

**Descriptores no lineales de EEG a implementar:**
- Dimensión Fractal de Higuchi (HFD)
- Dimensión Fractal de Katz
- Exponente de Hurst
- Entropía de Shannon / Permutation Entropy
- Entropía Multiescala (MSE)
- Lempel-Ziv Complexity
- Dimensión de Correlación
- Exponente de Lyapunov

**Por qué es diferencial:**  
Una revisión sistemática de 2025 (PubMed: 39978669) analizó 87 estudios de ML con EEG/MRI para TDAH y concluyó que **no existe todavía un sistema suficientemente fiable para uso clínico**, señalando problemas de heterogeneidad, sobreajuste y reproducibilidad. La oportunidad está en construir metodología más rigurosa y reproducible.

**El ángulo de producto más interesante:** No diagnóstico, sino **monitoreo cuantitativo de respuesta al tratamiento**. Un sistema que mide si el EEG cambia de forma objetiva y reproducible antes y después de una intervención.

**Advertencias importantes:**
- Los datasets de EEG son más difíciles de procesar que imágenes (requiere ICA, artifact rejection, etc.)
- ADHD-200 es fMRI, no EEG. Son dominios técnicos distintos.
- Necesita colaboración con neurólogo/psiquiatra para validación clínica.

---

## 8. Estrategia Recomendada para el Nuevo Proyecto

### La arquitectura del proyecto madre

No hacer una startup de un dominio específico desde el día 1.  
Construir primero un **Motor de Análisis Morfológico/Fractal reutilizable** que pueda aplicarse a múltiples dominios.

```
FRACTAL AI ENGINE
        │
┌───────┴───────┐
↓               ↓
DENTAL        NEURO
  │               │
Dataset       Dataset
  │               │
Feature       Feature
engine        engine
  │               │
ML            ML
baseline      baseline
  │               │
└───────┬───────┘
        ↓
   COMPARACIÓN
   ¿Dónde la señal
    fractal es más fuerte?
```

### Secuencia de ejecución recomendada

1. **Semanas 1-4 — Branch Dental primero (solo)**
   - 3-5 entrevistas con profesional odontóloga: *"¿Qué medís a ojo que te gustaría poder medir objetivamente?"*
   - Descargar dataset público de panorámicas (Tufts / DENTEX)
   - Implementar segmentación de hueso alveolar
   - Calcular métricas fractales (D₀, Λ, Δα) sobre la región trabecular
   - Primer resultado cuantitativo: CSV + curva ROC vs ground truth clínico

2. **Semanas 5-8 — Evaluación y decisión**
   - Si la señal dental es fuerte → continuar en ese vertical
   - Si la señal es débil → abrir Branch Neuro con el conocimiento adquirido sobre cómo iterar rápido

3. **Semanas 9-12 — Paper corto / preprint**
   - Redactar pregunta científica + metodología + resultados
   - Un preprint ya te da credibilidad ante inversores e incubadoras

4. **A partir del mes 4 — MVP y financiamiento**
   - Prototipo web mínimo con el vertical que mostró señal
   - Postulación a FONTAR (ANPCyT) — financian exactamente este tipo de proyectos
   - Incubadoras universitarias (UTN, UBA, UNSAM) para mentoring y conexiones

---

## 9. Qué llevar y qué NO llevar de DigPatho

### ✅ Podés llevar (es conocimiento tuyo)
- El conocimiento matemático: fractales, TDA, deconvolución de color, box-counting, lacunaridad, persistent homology
- La arquitectura mental del pipeline: imagen → segmentación → features → ML → reporte
- La experiencia práctica con: `scikit-image`, `ripser`, `scikit-fuzzy`, `reportlab`, `streamlit`, LangGraph
- El Colab notebook desarrollado (`her2_fractal_analysis.ipynb`) — matemáticas de dominio público

### ❌ No llevás (es IP de DigPatho)
- Código fuente de los repositorios de la empresa
- Datasets clínicos internos
- La ontología ASCO/CAP construida en Neo4j
- Arquitectura específica del sistema multi-agente de producción
- Cualquier dato de pacientes o imágenes de biopsias propias

---

## 10. Preguntas Clave a Responder en el Nuevo Proyecto

Antes de escribir una línea de código del nuevo proyecto, estas son las preguntas que definen el camino:

1. **¿Tenés acceso a un profesional del dominio elegido** que pueda hacer por Neuro lo que la odontóloga puede hacer por Dental?
2. **¿Qué mide el profesional a ojo hoy** que le gustaría poder medir objetivamente y con un número?
3. **¿Los fractales realmente aportan información nueva** o solo replican lo que ya captura una CNN? (Esto se responde con el experimento de 4 semanas)
4. **¿Hay un dataset público hoy** suficientemente grande y bien etiquetado para el problema específico?
5. **¿Quién paga y cuánto?** ¿El primer cliente es una universidad, una clínica, una farmacéutica?

---

## 11. Recursos y Referencias Clave

| Referencia | Relevancia |
|---|---|
| PubMed: 41828058 | Revisión sistemática 2026 — Fractales + IA para pérdida ósea periodontal. Identifica la necesidad de modelos híbridos estandarizados. |
| PubMed: 39656957 | Revisión IA para pérdida ósea periodontal — problemas de calidad y heterogeneidad actuales. |
| PubMed: 39978669 | Revisión sistemática 2025 — 87 estudios ML con EEG/MRI para TDAH. Concluye que no hay sistema clínicamente fiable todavía. |
| PubMed: 39963122 | XGBoost + EEG para TDAH (2025, 168 participantes). |
| PMC: 8687398 | Análisis no lineal de EEG en TDAH: dimensión fractal de Higuchi, Katz, Hurst. |
| PMC: 11633071 | Datasets públicos de radiografías dentales: panorámicas, segmentación, caries. |
| Ruifrok & Johnston (2001) | Algoritmo de deconvolución de color H-DAB. Implementado en el Colab. |
| Chhabra & Jensen (1989) | Método de momentos para el espectro multifractal f(α). |
| Lapidus (2006-2013) | Cuerdas fractales y dimensiones complejas. |
| Edelsbrunner & Harer (2010) | Homología persistente (TDA). |

---

*Documento de contexto generado al cierre del ciclo de trabajo en DigPatho / demo-her2.*  
*El nuevo proyecto parte de aquí, con código y datos completamente propios.*
