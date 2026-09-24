# Lattice Bio — Presentación del Sistema de Análisis Trabecular Óseo

Documento de información general preparado para evaluación clínica odontológica.

---

## ¿Qué es Lattice Bio?

Lattice Bio es un desarrollo de ingeniería y visión por computadora enfocado en el análisis de la microarquitectura trabecular del hueso alveolar mediante radiografías dentales (panorámicas y periapicales).

El propósito del sistema es proveer una herramienta de soporte que permita evaluar de forma objetiva y cuantitativa la densidad, porosidad e integridad del entramado óseo trabecular, ayudando en la caracterización precoz de cambios asociados a la pérdida ósea periodontal.

---

## ¿Qué hace el sistema y cómo funciona?

La evaluación radiográfica convencional se enfoca en observar la altura de la cresta ósea. Lattice Bio analiza la estructura interna del hueso antes de que los cambios de altura sean marcadamente visibles a simple vista.

El procesamiento analiza la radiografía a través de cuatro enfoques matemáticos complementarios:

### 1. Análisis de Densidad en Escala de Grises (Manta de Minkowski)
Modela la radiografía en tres dimensiones tomando la intensidad de gris como indicador de la densidad mineral. Permite evaluar la desmineralización incipiente sin necesidad de modificar o binarizar la imagen original.

### 2. Dimensión Fractal (Complejidad Estructural)
Mide la complejidad y autosimilitud espacial de la red trabecular. En hueso sano, el entramado presenta una alta complejidad matemática. Cuando ocurre reabsorción o inflamación, el patrón pierde complejidad y disminuye su valor.

### 3. Lacunaridad (Porosidad y Distribución de Huecos)
Cuantifica la distribución, tamaño y desorden de los espacios vacíos dentro del tejido. Un incremento en la lacunaridad indica la formación de cavidades o lagunas de reabsorción en la matriz trabecular.

### 4. Análisis Topológico (Índice de Fragmentación)
Evalúa la conectividad de la red identificando la proporción entre estructuras óseas aisladas y lazos cerrados de soporte. Un ratio elevado refleja la rotura del entramado trabecular y la presencia de espículas desconectadas.

---

## Mapa de Calor Visual (Heatmap)

Para facilitar la interpretación rápida en la práctica diaria, el sistema genera una capa visual de color sobre la radiografía original:

- Zonas Verdes: Tejido trabecular continuo y con densidad conservada.
- Zonas Amarillas: Áreas con signos tempranos de rarefacción o desmineralización moderada.
- Zonas Rojas: Regiones con pérdida de densidad trabecular o alta fragmentación.

---

## Generación de Informes

El sistema permite exportar un informe en formato PDF que resume las imágenes procesadas, el mapa de calor visual y los valores numéricos obtenidos, facilitando el seguimiento en el tiempo de la evolución del paciente.
