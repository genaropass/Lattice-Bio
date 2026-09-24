# 🔬 Informe de Auditoría Científica, Matemática, Técnica y de Producto
## Project: Lattice Bio — Sistema de Análisis Trabecular Óseo

**Fecha de Auditoría:** Septiembre 2026  
**Auditoría Técnica:** Advanced Agentic AI Coding & Biomedical Computer Vision Research  
**Objetivo:** Evaluación crítica, desambiguación matemática, revisión de evidencia clínica y definición de la hoja de ruta experimental y de producto para **Lattice Bio**.

---

# 1. CONTEXTO & REVISIÓN CRÍTICA DEL CONCEPTO

Lattice Bio propone un sistema de Computer Vision y Machine Learning orientado a caracterizar la estructura trabecular del hueso alveolar en radiografías dentales (panorámicas y periapicales).

### Diagnóstico de Madurez del Concepto:
El concepto es **plausible y cuenta con precedentes científicos fragmentados** en la literatura de procesamiento de imágenes médicas (1995-2026). Sin embargo, el planteo actual sufre de **superposición de afirmaciones entusiastas** que mezclan hipótesis físicas no demostradas (ej. "medir densidad mineral" en 2D) con técnicas matemáticas bien conocidas (Box-Counting, Lacunaridad).

La fortaleza de Lattice Bio no radicará en "descubrir" un nuevo operador matemático individual, sino en la **estandarización reproducible del pipeline, la extracción automática de ROI interdental y la prueba empírica de si la fusión de descriptores de estructura aporta información no redundante respecto a un modelo de visión profunda**.

---

# 2. AUDITORÍA DE AFIRMACIONES (ITEM POR ITEM)

A continuación se clasifica cada componente del planteo actual bajo las categorías:
- **[A] Respaldada por literatura:** Demostrada experimentalmente en estudios con significancia estadística.
- **[B] Plausible pero por demostrar:** Físicamente coherente pero dependiente de validación empírica en nuestra muestra.
- **[C] Simplificación:** Útil pedagógicamente pero conceptualmente imprecisa si se toma de forma literal.
- **[D] Científicamente incorrecta o demasiado fuerte:** Debe eliminarse o redactarse con rigor.
- **[E] Hipótesis nueva:** Propuesta propia a investigar mediante experimentos formales.

| Afirmación / Módulo | Categoría | Diagnóstico & Fundamento Científico | Redacción Corregida / Rigurosa |
|---|---|---|---|
| *"Modelar la radiografía en 3D tomando la intensidad de gris como densidad mineral"* | **[D] Incorrecta / [C] Simplificación** | Una radiografía 2D mide atenuación fotónica integrada (Ley de Beer-Lambert), no densidad mineral volumétrica (g/cm³). La intensidad refleja superposición de tejidos y exposición. | *"Cuantifica la variación de la superficie de intensidad radiográfica proyectada (2.5D) mediante Manta de Minkowski."* |
| *"La reabsorción ósea disminuye universalmente la Dimensión Fractal ($D_0$)"* | **[C] Simplificación / [B] Plausible** | La relación $D_0$ vs periodontitis depende del preprocesamiento, binarización y la fase de la enfermedad. En desmineralización temprana puede haber un aumento transitorio de $D_0$ por porosidad antes del colapso. | *"En estadíos moderados/avanzados, la pérdida de trabéculas disminuye la complejidad del patrón binarizado ($p < 0.05$ en periapicales)."* |
| *"Un aumento de lacunaridad ($\Lambda$) indica cavidades de reabsorción"* | **[A] Respaldada / [B] Plausible** | Respaldada por estudios de textura (Allain & Cloitre; Updike 2025). La lacunaridad mide el tamaño y la variabilidad de los huecos intertrabeculares. | *"La lacunaridad cuantifica la heterogeneidad espacial del espacio intertrabecular y su incremento se asocia con reabsorción porosa."* |
| *"El ratio topológico ($\beta_0 / \beta_1$) refleja la fragmentación del tejido"* | **[B] Plausible / [E] Hipótesis Nueva** | $TDA$ ($\beta_0$ componentes conexas, $\beta_1$ lazos) se ha aplicado en micro-CT de trabeculado (Edelsbrunner 2010), pero su uso en radiografías 2D es una hipótesis a validar por ruido de proyección. | *"La relación entre componentes desconectadas y ciclos cerrados cuantifica geométricamente la continuidad del entramado binarizado."* |
| *"Detecta cambios microestructurales antes de que sean visibles a simple vista"* | **[B] Plausible / [D] Demasiado Fuerte** | Plausible en teoría (la textura cambia antes del colapso macroscópico de la cresta), pero no se puede afirmar comercialmente sin un ensayo longitudinal prospectivo. | *"Hipótesis de investigación: Las métricas de textura y topología presentan cambios cuantificables previos a la pérdida de altura de la cresta alveolar en radiografías periapicales."* |
| *"Los colores del Heatmap (Verde = Sano, Rojo = Enfermo)"* | **[D] Incorrecta hoy** | Afirmar diagnóstico por color sin un modelo clasificador calibrado y validado es un riesgo regulatorio y metodológico. | *"El mapa de calor representa la desviación escalar local respecto a la mediana del patrón trabecular de referencia."* |

---

# 3. DESAMBIGUACIÓN MATEMÁTICA DE LA "MANTA DE MINKOWSKI"

Existe confusión conceptual en el uso del término *"Manta de Minkowski"*. A continuación se desambiguan formalmente las alternativas:

```text
               DEFINICIONES MATEMÁTICAS POSIBLES

1. Minkowski Sausage (2D Boundary) ──► Dilatación de un contorno binario con un disco de radio ε
2. Bouligand-Minkowski Dimension ──► Pendiente log-log del volumen dilatado vs ε (para fractales)
3. Minkowski Blanket Method (Grayscale) ──► Superficies superior u(x,y,ε) e inferior b(x,y,ε) (Peitgen 1988)
4. Minkowski Functionals (Integral Geometry) ──► Área, Perímetro, Característica de Euler (Hadwiger 1957)
```

### A. Explicación Matemática de las Posibilidades

1. **Minkowski Blanket Method (Peitgen & Saupe 1988; Peene 1989):**
   Trata la imagen $I(x,y)$ como una superficie $z = I(x,y)$. Construye dos superficies límites para la escala $\varepsilon = 1, 2, \dots, \varepsilon_{\max}$:
   $$u(x,y,\varepsilon) = \max \left\{ u(x,y,\varepsilon-1) + 1, \max_{(m,n) \in N_4(x,y)} u(m,n,\varepsilon-1) \right\}$$
   $$b(x,y,\varepsilon) = \min \left\{ b(x,y,\varepsilon-1) - 1, \min_{(m,n) \in N_4(x,y)} b(m,n,\varepsilon-1) \right\}$$
   Con condiciones iniciales $u(x,y,0) = b(x,y,0) = I(x,y)$.
   El volumen del manto envuelto es $V(\varepsilon) = \sum_{x,y} \left( u(x,y,\varepsilon) - b(x,y,\varepsilon) \right)$.
   El área de la superficie a escala $\varepsilon$ es $A(\varepsilon) = \frac{V(\varepsilon) - V(\varepsilon-1)}{2}$.
   La **Dimensión de Minkowski-Bouligand** se obtiene como $D_{MB} = 2 - \lim_{\varepsilon \to 0} \frac{\log A(\varepsilon)}{\log \varepsilon}$.

2. **Minkowski Functionals (Geometría Integral - Teorema de Hadwiger):**
   Para un conjunto binarizado $K \subset \mathbb{R}^2$, existen exactamente 3 funcionales queretomáticos independientes bajo transformaciones isométricas:
   - $W_0(K) = \text{Área}(K)$
   - $W_1(K) = \frac{1}{2} \text{Perímetro}(K)$
   - $W_2(K) = \pi \cdot \chi(K)$ (donde $\chi$ es la Característica de Euler)

### B. Dictamen Técnico para Lattice Bio:
- **¿Qué afirmación es válida?:** La expresión *"medición de densidad mineral en 3D"* es **falsable y científicamente incorrecta**. Lo que se mide realmente es la **rugosidad y variación multiescala del relieve de intensidad radiográfica atenuada**.
- **Independencia funcional:** La Manta de Minkowski sobre escala de grises ($D_{MB}$) **NO es independiente** de la Dimensión Fractal Box-Counting ($D_0$) sobre binario; ambas miden la dimensión de Hausdorff-Besicovitch subyacente. La diferencia clave es que $D_{MB}$ evita la binarización fija y preserva los gradientes continuos de atenuación.

---

# 4. AUDITORÍA DE LA DIMENSIÓN FRACTAL ($D_0$)

### A. Sensibilidad a Parámetros de Procesamiento

La literatura en radiología oral y maxilofacial (*White & Rudolph 1999*, *Geraets 2006*, *Sindeaux 2014*, *PubMed 41828058*) demuestra que la Dimensión Fractal ($FD$) calculada por Box-Counting es **extremadamente sensible** a factores no biológicos:

```text
Sensibilidad de FD = f(Resolución, Binarización, CLAHE, Tamaño de ROI, Orientación)
```

1. **Binarización:** Si se usa Otsu global, imágenes con subexposición o gradientes de iluminación alteran drásticamente $FD$. La binarización de Sauvola local con ventana adaptativa ($w=25, k=0.2$) o la filtración de mallas (White & Rudolph) son mandatorias.
2. **Resolución:** Variaciones en DPI/tamaño de píxel entre sensores (ej. Dexis vs Carestream) modifican el rango inercial de la regresión log-log ($\log 1/\varepsilon$). Se debe estandarizar el tamaño físico del píxel ($\mu m/\text{pixel}$).
3. **Tamaño de ROI:** ROIs menores a $32 \times 32$ píxeles no poseen suficiente rango dinámico espacial para calcular una regresión log-log válida ($R^2 < 0.90$).

### B. Evidencia Clínica en Periodontitis

- **En radiografías periapicales de alta resolución:** Existe evidencia sólida (*Ruttimann 1992*, *Shrout 1997*, *Kaur 2021*) de que la destrucción trabecular avanzada reduce $FD$ de $\sim 1.78$ a $\sim 1.62$ ($p < 0.01$).
- **En radiografías panorámicas (OPG):** La evidencia es **moderada e inconsistente** debido a la distorsión por superposición de la columna cervical, sombras del paladar duro y magnificación no uniforme. **No se debe asumir una regla única universal $FD_{\text{sano}} > FD_{\text{enfermo}}$ en OPGs sin control de la región anatómica.**

---

# 5. LACUNARIDAD ($\Lambda$)

### A. Rigor Matemático
La lacunaridad $\Lambda(r)$ (Allain & Cloitre 1991) cuantifica la desviación de la homogeneidad traslacional a escala $r$:
$$\Lambda(r) = \frac{\langle s^2 \rangle}{\langle s \rangle^2}$$
donde $s$ es la masa dentro de una ventana deslizante de tamaño $r \times r$.

### B. Relación con la Dimensión Fractal y Validez de Afirmaciones
- **¿Es independiente de $FD$?:** **SÍ.** La Dimensión Fractal mide la densidad espacial del conjunto (cuánto espacio llena); la Lacunaridad mide **cómo se distribuyen los vacíos**. Dos imágenes con la misma $FD = 1.70$ pueden tener lacunaridades opuestas: una con poros diminutos distribuidos homogéneamente ($\Lambda \approx 1.05$) y otra con un gran defecto osteolítico aislado ($\Lambda > 1.50$).
- **Corrección de la afirmación:** Afirmar *"mayor lacunaridad = mayor reabsorción"* es una **simplificación**. Lo correcto es: *"Un aumento en la lacunaridad multiescala refleja un incremento en la discontinuidad e irregularidad del espacio intertrabecular."*

---

# 6. MORFOLOGÍA Y GEOMETRÍA INTEGRAL

Para evitar la multiplicación de métricas redundantes, auditamos los descriptores morfológicos:

| Descriptor | Fórmula / Principio | Fenómeno Estructural que Mide | ¿Es Redundante? | Recomendación para Lattice Bio |
|---|---|---|---|---|
| **Área Trabecular ($A$)** | $\sum I_{\text{bin}}(x,y)$ | Fracción de volumen trabecular proyectado ($BV/TV_{2D}$) | No | **CONSERVAR** (Línea base fundamental) |
| **Perímetro Trabecular ($P$)** | Conteo de píxeles de borde | Interfaz hueso-médula / Superficie específica | Algo con Área | **EVALUAR** como ratio $P/A$ |
| **Característica de Euler ($\chi$)** | $\chi = \beta_0 - \beta_1$ | Conectividad topológica neta | No | **CONSERVAR** (Fundamento riguroso) |
| **Granulometría Morfológica** | Apertura recursiva $\gamma_r(I)$ | Distribución de tamaños de las espículas óseas | Sí con Lacunaridad | **ELIMINAR** en V1 |

---

# 7. AUDITORÍA TOPOLÓGICA (TDA & NÚMEROS DE BETTI)

### A. Definición Formal en Grid 2D
- **$\beta_0$ (Betti-0):** Cantidad de componentes conectadas (fragmentos u órbitas independientes de espículas).
- **$\beta_1$ (Betti-1):** Cantidad de ciclos cerrados / lazos (trabéculas interconectadas que encierran un espacio medular).
- **Euler Characteristic ($\chi$):** $\chi = \beta_0 - \beta_1$.

### B. Homología Persistente (TDA)
La homología persistente mediante filtraciones de Vietoris-Rips o Sublevel Sets sigue la evolución de $\beta_0$ y $\beta_1$ a través de un parámetro continuo (intensidad de gris o distancia).

### C. Valor Biológico vs Redundancia:
- **¿Aporta valor biológico real?:** **SÍ.** Mide la **resiliencia biomecánica** de la red. Una red trabecular puede perder masa pero mantener sus lazos ($\beta_1$ alto = estructura resistente). Cuando la periodontitis rompe los lazos, $\beta_1$ colapsa y $\beta_0$ se dispara (fragmentación).
- **Dictamen TDA V1:** Usar **$\beta_0, \beta_1$ y $\chi$ morfológicos directos en la grilla** es suficiente, robusto y 100x más rápido que calcular diagramas de persistencia completos de Ripser. **Reservar Homología Persistente avanzada para investigación de v2.**

---

# 8. MAPA CONCEPTUAL INTEGRADO DE DESCRIPTORES

| Método | Qué mide matemáticamente | Propiedad estructural que representa | Hipótesis biológica | ¿Redundante? | Validación empírica necesaria |
|---|---|---|---|---|---|
| **Manta de Minkowski (Grises)** | Superficie de relief $D_{MB} = 2 - \text{slope}(\log A \text{ vs } \log \varepsilon)$ | Rugosidad y gradientes continuos de atenuación | Modificación de la densidad cálcica cortical/trabecular | Complementa a $D_0$ binario | Correlación con densidad radiográfica óptica |
| **Box-Counting ($D_0$)** | Complejidad de ocupación espacial en matriz binarizada | Complejidad del trazado espicular 2D | Pérdida de ramificación trabecular por osteoclastosis | Parcialmente con $D_{MB}$ | Comparación sano vs periodontitis en ROI fija |
| **Lacunaridad ($\Lambda$)** | Varianza relativa de masa $\langle s^2 \rangle / \langle s \rangle^2$ | Heterogeneidad de la distribución de vacíos | Formación de lagunas de reabsorción ósea | **NO** (Ortogonal a $D_0$) | Discriminación en parches con misma $D_0$ |
| **Ratio Topológico ($\beta_0 / \beta_1$)** | Relación componentes / ciclos $\frac{\beta_0}{\beta_1 + 1}$ | Continuidad e interconexión de la red | Desconexión microestructural de la red trabecular | **NO** (Es topológico, no métrico) | Ensayo biomecánico / micro-CT ground truth |
| **Deep Embeddings (DINOv2)** | Representación en espacio latente $d \in \mathbb{R}^{768}$ | Patrones semánticos y contextuales complejos | Captura morfología global e intersección anatómica | **NO** (Es no paramétrico) | Ablation study (ML clásico vs DL vs Híbrido) |

---

# 9. LIMITACIÓN FUNDAMENTAL: 2D PROYECCIONAL VS 3D REAL

> [!CAUTION]
> **No se debe comercializar ni afirmar en papers que Lattice Bio evalúa la "microarquitectura 3D" en radiografías 2D.**

### A. Física de la Imagen y Proyección:
Una radiografía 2D es una **atenuación integrada en la línea de visión**:
$$I(x,y) = I_0 \cdot \exp \left( -\int \mu(x,y,z) \, dz \right)$$
Por ende, una espícula gruesa y una superposición de tres espículas delgadas producen la misma intensidad radiográfica.

### B. Comparativa Técnica de Modalidades:

| Modalidad | Resolución Espacial | Información Capturada | Afirmación Científica Permitida |
|---|---|---|---|
| **Radiografía Periapical 2D** | Alta ($\sim 20-50 \, \mu m$) | Proyección integrada 2.5D | *"Características estructurales 2D del trabeculado proyectado"* |
| **Radiografía Panorámica (OPG)** | Media ($\sim 100-200 \, \mu m$) | Proyección con distorsión focal | *"Patrones de textura y densidad aparente en arcos"* |
| **CBCT Dental 3D** | Alta 3D ($\sim 75-150 \, \mu m$) | Volumétrica real (Voxels) | *"Microarquitectura volumétrica 3D y espesor de trabécula"* |
| **Micro-CT (Ex vivo)** | Ultra-alta ($\sim 1-10 \, \mu m$) | Estructura trabecular física pura | *"Ground Truth trabecular absoluto ($BV/TV, Tb.Th, Tb.Sp$)"* |

---

# 10. GROUND TRUTH CLÍNICO & FORMULACIÓN DEL PROBLEMA

### A. Definición del Ground Truth Clínico
"Que la radiografía se vea fea" **NO es un ground truth científico**. El ground truth debe basarse en el **Consenso de la Clasificación Periodontal AAP/EFP 2018**:

1. **Pérdida Ósea Radiográfica (RBL):** Porcentaje de pérdida respecto a la longitud radicular (medido desde la CEJ al ápex).
2. **Nivel de Inserción Clínica (CAL):** Pérdida de soporte periodontal en milímetros.
3. **Estadificación AAP/EFP (Stages I, II, III, IV):**
   - Stage I: RBL $< 15\%$ (Pérdida ósea leve).
   - Stage II: RBL $15\% - 33\%$ (Pérdida ósea moderada).
   - Stage III/IV: RBL $> 33\%$ o extensión a furca.

### B. Formulación del Modelo de ML: ¿Clasificación, Regresión o Longitudinal?

```text
               OPCIONES DE FORMULACIÓN DEL PROBLEMA

1. Clasificación Binaria (Sano vs Periodontitis) ──► Débil (Demasiado fácil, poca utilidad)
2. Clasificación Multi-clase (AAP/EFP Stage I al IV) ──► Relevante para clínica
3. Regresión Continua (Porcentaje de RBL %) ──► Científicamente muy fuerte
4. Análisis Longitudinal (Cambio Δ en T1 - T0) ──► LA MÁS POTENTE Y DIFERENCIAL
```

**Dictamen:**
- Para la **Fase 1 (Paper)**: Formular como **Regresión del Porcentaje de RBL** y **Clasificación por Estadios AAP/EFP (Stages I al IV)**.
- Para el **Producto (Fase 2)**: Enfocarse en el **Análisis Longitudinal de Cambio ($\Delta T$)**, donde el paciente actúa como su propio control y los fractales capturan variaciones de textura antes del colapso lineal de la cresta.

---

# 11. ESTRATEGIA DE ROI (REGIÓN DE INTERÉS)

La literatura demuestra que la selección de ROI es la **fuente #1 de variabilidad y sesgo** en el análisis fractal.

### Comparativa de Estrategias de ROI:

| Estrategia | Ventajas | Desventajas | Decisión para Lattice Bio |
|---|---|---|---|
| **1. Selección Manual** | Adaptada por el clínico | Subjetiva, baja reproducibilidad ($ICC < 0.75$) | **Descartar para producción** |
| **2. Bounding Box Fijo** | Simple de computar | Captura raíces, dentina o conductos mandibulares | **Descartar** |
| **3. ROI Anatomía Automática (YOLO/SAM)** | Altamente reproducible | Requiere dataset entrenado | **FASE 1 (Entrenamiento)** |
| **4. ROI Interdental Estandarizada ($1.5 \times 3.0 \, mm$)** | Captura exclusivamente hueso alveolar interproximal | Sensible a la orientación del diente | **ESTÁNDAR DEFINITIVO** |

### Estrategia Estandarizada Propuesta:
Extraer automáticamente un rectángulo orientado de **$1.5 \, mm \times 3.0 \, mm$** ubicado **$1.0 \, mm$ por debajo de la cresta alveolar interdental**, excluyendo raíz, espacio del ligamento periodontal y esmalte.

---

# 12. PIPELINE DE PREPROCESAMIENTO REPRODUCIBLE

El preprocesamiento **NO debe alterar la dimensión fractal natural**. Ciertas transformaciones (como suavizado gaussiano agresivo o thresholding global descalibrado) destruyen artificialmente $FD$.

```text
[Radiografía Raw] 
       │
       ▼
[Resampling Espacial Estandarizado (píxel = 35 µm)]
       │
       ▼
[Normalización Z-score de Intensidad Local]
       │
       ▼
[CLAHE Moderado (Clip limit = 2.0, Grid = 8x8)]
       │
       ▼
[Extracción de ROI Interdental Estandarizada]
       │
 ┌─────┴─────────────────────────┐
 ▼                               ▼
[Rama Grayscale]        [Rama Binarizada]
(Manta Minkowski)       (Sauvola Local: w=25, k=0.2)
                         │
                         ▼
                        [Esqueleto Morfológico]
```

> [!WARNING]
> **Prohibiciones en Preprocesamiento:**
> - NO usar ecualización de histograma global estándar (distorsiona gradientes).
> - NO aplicar filtros gaussianos con $\sigma > 1.5$ píxeles antes del cálculo fractal (destruye altas frecuencias).

---

# 13. EXPERIMENTO FUNDAMENTAL DE VALIDACIÓN

Para responder si Lattice Bio aporta valor o es redundante, debemos ejecutar el siguiente **Experimento Fundamental de Fusión**:

### Hipótesis Nula ($H_0$):
> "La adición de características matemáticas (Minkowski, $D_0$, $\Lambda$, TDA) a los embeddings de una red de visión profunda (DINOv2 / ResNet50) NO produce un incremento estadísticamente significativo en el AUC-ROC o R² de predicción de RBL."

### Diseño Experimental (5 Modelos Comparados):

```text
Modelo A: Solo Features Matemáticos (Minkowski + D0 + Lacunaridad + TDA) -> XGBoost
Modelo B: Solo Embeddings DL (DINOv2 ViT-S/14 latente 384d) -> XGBoost
Modelo C: Modelo de Visión Finetuned Pura (ResNet50 / ConvNeXt)
Modelo D: Fusión Híbrida (Embeddings DL + Features Matemáticos) -> XGBoost
Modelo E: Baseline Clínico (Edad + Sexo + Medición Lineal Manual)
```

### Prueba Estadística de Validación:
- **DeLong Test** para comparar curvas ROC entre Modelo B vs Modelo D.
- **$p < 0.05$** requerida para rechazar $H_0$ y demostrar el valor diferencial de la matemática.

---

# 14. ABLATION STUDY & INTERPRETABILIDAD

Para entender la contribución exacta de cada bloque matemático, se ejecutará el siguiente plan de ablación:

```text
Baseline (Área Trabecular 2D)
  ├── + Minkowski Blanket (D_MB)
  ├── + Box-Counting (D_0)
  ├── + Lacunaridad (Λ)
  └── + Topología Betti (β0/β1)
```

### Análisis de Importancia:
1. **SHAP (SHapley Additive exPlanations):** Medir el valor SHAP medio $|\phi_i|$ de cada descriptor en la predicción.
2. **Información Mutua (Mutual Information Score):** Determinar redundancia entre $D_{MB}$ y $D_0$.
3. **Multicolinealidad (VIF - Variance Inflation Factor):** Eliminar métricas con $\text{VIF} > 10$.

---

# 15. HIPÓTESIS STRATEGIC SMALL DATA

> **¿Puede Lattice Bio ser superior a Deep Learning en escenarios de pocos datos ($N < 200$)?**

### La Hipótesis:
Las redes neuronales profundas (DL) requieren miles de imágenes para no sobreajustar (overfitting). Los descriptores matemáticos explícitos ($D_0, \Lambda, \beta_0/\beta_1$) actúan como **prior inductivo biológico**, permitiendo entrenar clasificadores robustos (XGBoost/SVM) con conjuntos de datos pequeños.

### Experimento de Curvas de Aprendizaje:
Evaluar AUC-ROC en subsamples del dataset con $N = \{25, 50, 100, 250, 500, 1000, 2000\}$:

```text
AUC-ROC
  1.0 ┤                                      ┌─ DL (DINOv2)
  0.9 ┤                      ┌───────────────┴─ Híbrido (Lattice Bio)
  0.8 ┤ ┌────────────────────┼───────────────── ML Matemático
  0.7 ┤ └─ DL Puro (Falla N<100)
  0.6 └─┬──────┬──────┬──────┬──────┬──────┬───
       25     50    100    250    500   1000  (N Muestras)
```

**Si Lattice Bio supera a DL en $N < 250$, esta es la mayor ventaja comercial y científica del sistema.**

---

# 16. AUDITORÍA DEL HEATMAP & RIESGO CLINICO

### A. Dictamen Técnico
El planteo inicial *"Verde = Sano, Rojo = Periodontitis"* es **científicamente indefendible y peligroso**. Un mapa de falso color derivado de una ventana deslizante no es un mapa diagnóstico; es un **mapa de desviación estructural local**.

### B. Generación Rigurosa del Heatmap:
1. **Opción Científica A (Sliding Window Anomaly):** Representar la desviación estándar Z-score del descriptor $D_{MB}$ local respecto al promedio de parches trabeculares de referencia sanos:
   $$Z(x,y) = \frac{D_{MB}(x,y) - \mu_{\text{sano}}}{\sigma_{\text{sano}}}$$
2. **Opción Científica B (Grad-CAM Híbrido):** Ponderar el mapa de activación Grad-CAM del modelo de visión por el mapa de lacunaridad local.

---

# 17. REFACTORIZACIÓN DEL INFORME CLÍNICO FORMAL

El informe exportable debe estructurarse separando rigurosamente **Datos Objetivos**, **Visualizaciones** e **Interpretación**:

```markdown
# Informe de Caracterización Trabecular — Lattice Bio Engine

## 1. Datos Objetivos de la Imagen (Mediciones Físicas)
- Resolución Espacial: 35 µm/píxel (Normalizada)
- Área de ROI Analizada: 4.5 mm² (Región Interdental)
- Dimensión de Manta de Minkowski (D_MB): 2.41 (Intervalo Ref. Sano: 2.75 - 2.95)
- Lacunaridad Media (Λ): 1.38 (Intervalo Ref. Sano: 1.05 - 1.18)
- Ratio de Fragmentación Topológica (β0/β1): 2.85 (Intervalo Ref. Sano: < 0.40)

## 2. Visualización Estructural
[ Radiografía ROI ]  [ Mapa de Desviación Estructural Z-Score ]

## 3. Interpretación Algorítmica (Soporte a la Decisión)
- Índice de Integridad Trabecular (Lattice Index): 48 / 100
- Patrón Morfológico: Compatible con rarefacción trabecular e incremento de porosidad interdental.
- Nota de Responsabilidad: Los datos cuantitativos representan un análisis de textura radiográfica y deben ser correlacionados por el clínico con la sonda periodontal y el nivel de inserción clínica (CAL).
```

---

# 18. PROTOCOLO DE VALIDACIÓN Y CONFOUNDERS

### A. Protocolo de División de Datos (Patient-Level Split)
- **Regla de Oro:** **NUNCA** colocar radiografías del mismo paciente en entrenamiento y prueba. La división (Train 70%, Val 15%, Test 15%) debe ser estrictamente por `Patient_ID`.

### B. Confounders (Variables de Confusión a Controlar)

```text
                            CONFOUNDERS MATEMÁTICOS
                            
     Biológicos/Anatómicos                   Técnicos/Equipos
  ─────────────────────────               ──────────────────────
  • Edad del paciente                     • Fabricante del sensor (Dexis, Vatech)
  • Sexo (osteopenia sistémica)           • Dosis / kVp / mAs de exposición
  • Mandíbula vs Maxilar superior         • Ángulo de proyección del cono
  • Estado de dentición / Implantes       • Formato (DICOM sin compresión vs JPG)
  • Tabaquismo / Diabetes                 • Magnificación geométrica
```

**Estrategia de Control:** Ejecutar un modelo de regresión multivariable (ANCOVA) para verificar si las diferencias en $D_{MB}$ y $\Lambda$ entre sanos y enfermos se mantienen significativas tras ajustar por edad, sexo y tipo de sensor.

---

# 19. REVISIÓN DE NOVEDAD & DIFERENCIACIÓN REAL

> **¿Qué hace diferente a Lattice Bio de la literatura existente desde 1995?**

1. **Lo que NO es nuevo:** Usar Box-Counting o Lacunaridad en dientes (existen 80+ papers sobre esto).
2. **Lo que SÍ es novedoso y diferencial:**
   - La combinación unificada de **Manta de Minkowski en grises (2.5D) + Topología de Betti ($\beta_0/\beta_1$) + Deep Embeddings (DINOv2)**.
   - El algoritmo de **ROI Interdental Estandarizada Automática**.
   - El enfoque de **Análisis Longitudinal de Cambio ($\Delta T$)**, evaluando la velocidad de desmineralización en el mismo paciente.

---

# 20. ARQUITECTURA TÉCNICA DEFINITIVA DE LATTICE BIO

```text
                  RADIOGRAFÍA DENTAL (DICOM / PNG)
                                 │
                                 ▼
                     [ PREPROCESAMIENTO ]
              (CLAHE + Resampling 35µm + Z-score)
                                 │
                                 ▼
             [ SEGMENTACIÓN ANATÓMICA AUTOMÁTICA ]
              (Meta SAM / U-Net -> ROI Interdental)
                                 │
        ┌────────────────────────┼────────────────────────┐
        ▼                        ▼                        ▼
[Minkowski Blanket 3D]   [Lacunaridad & D0]      [TDA & Betti β0/β1]
 (Grises continuos)      (Matriz binarizada)     (Integridad de red)
        │                        │                        │
        └────────────────────────┼────────────────────────┘
                                 ▼
                  [ FUSIÓN DE CARACTERÍSTICAS ]
                 (Vector p-dimensional + DINOv2)
                                 │
                                 ▼
                     [ CLASIFICADOR XGBOOST ]
                                 │
                 ┌───────────────┴───────────────┐
                 ▼                               ▼
     [ RBL % / Stage AAP/EFP ]        [ Heatmap Z-Score Local ]
                 │                               │
                 └───────────────┬───────────────┘
                                 ▼
                   [ REPORTE PDF LATTICE BIO ]
```

---

# 21. ESTRATEGIA DE PRODUCTO & RIESGO REGULATORIO

### Matriz de Riesgo Regulatorio:

```text
MAYOR RIESGO REGULATORIO (FDA Class II / Software as Medical Device - SaMD)
  │  ❌ "IA Diagnóstica que detecta Periodontitis" (Años de ensayos clínicos y $M)
  │
  │  ⚠️ "Clinical Decision Support System (CDSS)" (Requiere 510(k) cleared predicate)
  │
  │  ✅ "Research & Analytics Platform / Imaging Biomarker Tool" (Menor barrera de entrada)
MENOR RIESGO REGULATORIO (RUO - Research Use Only / Software Analytics API)
```

**Recomendación de Go-To-Market:**
1. **Fase 1 (Inmediata):** Lanzar como **Research Use Only (RUO) Platform** para universidades, departamentos de periodoncia y ensayos de fármacos/regeneradores óseos.
2. **Fase 2 (Mediano Plazo):** Certificar como **Software de Análisis Cuantitativo Complementario (Imaging Analytics API)** integrable en software de gestión clínica (PMS/PACS).

---

# 22. PROPIEDAD INTELECTUAL (IP)

| Elemento del Sistema | Protegible por Patente | Protegible por Secreto / Copyright | Estrategia de Protección |
|---|---|---|---|
| **Fórmulas matemáticas (FD, Lacunaridad)** | ❌ NO (Dominio público) | ❌ NO | Ninguna (Es matemática abierta) |
| **Pipeline Híbrido (Minkowski + TDA + DINOv2)** | ⚠️ DUDOSO (Combinación) | ✅ SÍ (Código fuente) | Copyright de software |
| **Algoritmo de ROI Interdental Estandarizada** | ✅ POSIBLE PATENTE | ✅ SÍ | Solicitud de Patente de Método |
| **Dataset Curado de Biomarcadores Trabeculares** | ❌ NO | ✅ SÍ (Base de datos propia) | Secreto Comercial / Data Asset |
| **Marca "Lattice Bio"** | ✅ SÍ | ✅ SÍ | Registro de Marca Comercial |

---

# 23. AUDITORÍA DE AFIRMACIONES DE LA PRESENTACIÓN ORIGINAL

| Afirmación Original | Estado | Problema Científico | Nueva Redacción Rigurosa |
|---|---|---|---|
| *"Analiza la microarquitectura trabecular 3D"* | 🔴 REFORMULAR | Una radiografía 2D es una proyección atenuada integrada. | *"Analiza las características estructurales 2D de la microarquitectura trabecular proyectada."* |
| *"Modela la densidad mineral en 3D"* | 🔴 REFORMULAR | No mide $g/cm^3$ mineral volumétrico. | *"Cuantifica la variación de la superficie de intensidad radiográfica atenuada."* |
| *"Detecta desmineralización incipiente antes de ser visible"* | 🟡 HIPÓTESIS | Requiere ensayo prospectivo longitudinal. | *"Hipótesis de investigación: Caracteriza variaciones de textura previa a la pérdida visible de altura de la cresta."* |
| *"El hueso sano siempre presenta alta dimensión fractal"* | 🟡 REFORMULAR | Depende de la binarización y la fase del tejido. | *"En estadios moderados/avanzados, la pérdida de espículas reduce la complejidad espacial $D_0$."* |
| *"Zonas rojas representan pérdida de densidad"* | 🔴 REFORMULAR | Riesgo diagnóstico sin modelo clasificador. | *"Zonas rojas indican áreas con desviación relativa de textura respecto al patrón de referencia."* |

---

# 24. REPORTE FINAL DE AUDITORÍA (APARTADOS A - L)

## A. Lo que ya está científicamente respaldado
- El uso de **Dimensión Fractal ($D_0$)** y **Lacunaridad ($\Lambda$)** en radiografías periapicales de alta resolución para diferenciar hueso sano vs tejido con pérdida ósea severa ($p < 0.01$).
- La correlación inversa entre $D_0$ y $\Lambda$ en procesos osteolíticos.
- La utilidad del preprocesamiento adaptativo (CLAHE + Sauvola) para estabilizar radiografías.

## B. Lo que es una hipótesis razonable
- Que la **Manta de Minkowski sobre escala de grises ($D_{MB}$)** preserva información de desmineralización temprana mejor que el Box-Counting binarizado.
- Que las métricas matemáticas explícitas permiten entrenar modelos precisos en **escenarios de pocos datos ($N < 250$)**.
- Que el **Ratio Topológico de Betti ($\beta_0/\beta_1$)** mide la discontinuidad y fragmentación del tejido.

## C. Lo que actualmente estábamos afirmando demasiado fuerte
- Afirmar que medimos "densidad mineral 3D" en radiografías 2D.
- Afirmar que las zonas rojas del Heatmap representan diagnósticos clínicos de periodontitis.
- Afirmar que el sistema "detecta daño antes de que sea visible" sin haber publicado un estudio longitudinal prospectivo.

## D. Lo que debemos cambiar matemáticamente
- Estandarizar la resolución espacial (píxel = $35 \, \mu m$) antes de cualquier cálculo.
- Acoplar la escala de intensidad de Minkowski al rango espacial espacial ($D_{MB} \in [2.0, 3.0]$).
- Reemplazar la binarización fija por la Manta de Minkowski sobre grises para la rama principal.

## E. Lo que debemos experimentar (Próximos Pasos)
- **Experimento Fundamental de Fusión:** Demostrar si `ML Matemático + DL` supera a `DL Solo` ($p < 0.05$ vía DeLong test).
- **Ablation Study:** Medir el SHAP value y la ganancia de AUC de cada descriptor ($D_{MB}, D_0, \Lambda, \beta_0/\beta_1$).
- **Curva de Aprendizaje Small Data:** Probar rendimiento a $N = \{25, 50, 100, 250, 500\}$.

## F. Qué dataset necesitamos
- **Dataset Clínico Anotado de Estadios AAP/EFP (Stages I al IV)** con etiquetas de pérdida ósea radiográfica (RBL %) y Nivel de Inserción Clínica (CAL), idealmente pareado con datos de sonda periodontal.

## G. Qué arquitectura implementar primero
- La **Arquitectura Híbrida Modular** (Segmentación de ROI Interdental Estandarizada $\rightarrow$ Extracción paralela Grayscale/Fractal/TDA $\rightarrow$ Clasificador XGBoost).

## H. Qué experimento puede validar/refutar Lattice Bio
- El **Experimento de Ablación y DeLong Test** sobre las 2.795 radiografías procesadas. Si el modelo híbrido NO supera al modelo DL puro con significancia estadística ($p \ge 0.05$), la hipótesis central de agregar matemática explícita queda refutada.

## I. Qué podría ser realmente novedoso
- El **análisis longitudinal de cambio microestructural ($\Delta T$)** sobre el mismo paciente.
- El descriptor híbrido unificado de **Manta de Minkowski 3D + Topología de Betti en ROI Interdental Estandarizada**.

## J. Qué podría convertirse en producto
- Una **Plataforma de Investigación y Analítica de Imágenes (Research & Imaging Analytics API)** para facultades de odontología, laboratorios y fabricantes de software de gestión clínica.

## K. Qué podría convertirse en propiedad intelectual
- El **método y algoritmo de extracción de ROI Interdental Estandarizada Orientada**.
- El código fuente y la base de datos propietaria curada de biomarcadores trabeculares.

## L. DICTAMEN FINAL: GO / NO-GO

### 🟢 DICTAMEN: GO (CON CONDICIONES METODOLÓGICAS)

**Fundamentación:**
Existe una **hipótesis científica real, medible y potencialmente diferencial** en Lattice Bio: la cuantificación de la textura trabecular proyectada mediante Manta de Minkowski y Topología complementa la evaluación de visión profunda, especialmente en escenarios de datos limitados.

**Condiciones obligatorias para avanzar:**
1. Eliminar todo el lenguaje de marketing y afirmaciones de "densidad 3D".
2. Ejecutar el **Experimento Fundamental de Ablación (DeLong Test)** sobre las 2.795 imágenes procesadas para demostrar la hipótesis con evidencia empírica irrefutable.
