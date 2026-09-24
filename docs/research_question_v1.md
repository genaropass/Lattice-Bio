# ESPECIFICACIÓN DE PREGUNTA CIENTÍFICA, HIPÓTESIS Y ALCANCE (FASE 2)
## PROYECTO: LATTICE BIO
**Fecha de Emisión:** 2026-09-23  
**Estado:** Inmutable / Especificación de Fase 2  
**Dataset de Referencia:** `data/processed/final_dataset_manifest.csv`  
- Development Set: 643 pacientes únicos (657 imágenes)  
- Holdout Set: 162 pacientes únicos (193 imágenes) [Congelado, SHA256: `85e3a856...`]

---

## 1. PREGUNTA CIENTÍFICA PRINCIPAL (*Research Question*)

> **¿Los descriptores matemáticos de la estructura trabecular observada en radiografías dentales proporcionan información estructural reproducible y complementaria a las representaciones visuales profundas auto-supervisadas (DINOv2), después de controlar el data leakage, la duplicación y el sesgo de fuente/dominio?**

*Nota Metodológica:* La pregunta NO intenta abordar en esta etapa la inferencia diagnóstica de enfermedad periodontal ("¿Podemos diagnosticar periodontitis?"), sino que se enfoca estrictamente en la **caracterización de estructura trabecular, la reproducibilidad computacional y la evaluación de complementariedad con modelos profundos auto-supervisados**.

---

## 2. FORMULACIÓN DE HIPÓTESIS

### Hipótesis Principal ($H_1$):
Las características matemáticas de la geometría trabecular (descriptores fractales, multifractales y topológicos) capturan patrones estructurales en radiografías dentales 2D que no son completamente codificados por representaciones visuales auto-supervisadas (DINOv2), de modo que un espacio latente híbrido presenta una complementariedad estructural medible en muestras independientes.

### Hipótesis Nula ($H_0$):
Los descriptores matemáticos de geometría trabecular no aportan información estructural adicional o no redundante respecto de la representación visual profunda (DINOv2) bajo el protocolo experimental estandarizado y libre de sesgo definido.

---

## 3. OBJETO DE ESTUDIO Y UNIDAD DE ANÁLISIS

### Objeto de Estudio:
La estructura y textura trabecular observada en proyecciones radiográficas dentales 2D.

### Unidad de Análisis Principal:
* **Unidad Primaria de Agrupamiento y Evaluación:** **PACIENTE (`patient_id`)**.
  * *Consecuencia Estadística:* Toda la aleatorización (`GroupKFold`), el aislamiento del Holdout y el re-muestreo por bootstrap se realizan **estrictamente a nivel de paciente** para evitar la pseudo-replicación (múltiples imágenes del mismo sujeto tratadas como independientes).
* **Unidad Secundaria de Medición:** Parche de Región de Interés (ROI) trabecular interdental ($64 \times 64$ px).

---

## 4. CLAIMS PROHIBIDOS Y ALCANCE LIMITADO

Para mantener la rigurosidad científica y evitar afirmaciones no sustentadas por los datos actuales, queda **estrictamente prohibido** sostener los siguientes enunciados en esta etapa del proyecto:

1. ❌ *Claim 1:* "La dimensión fractal 2D mide directamente la densidad mineral ósea (BMD)."
2. ❌ *Claim 2:* "Una proyección radiográfica 2D representa directamente la microarquitectura trabecular 3D."
3. ❌ *Claim 3:* "El ancho del espectro multifractal ($\Delta\alpha$) es un biomarcador clínico de periodontitis."
4. ❌ *Claim 4:* "Los descriptores matemáticos detectan o diagnostican la presencia de enfermedad periodontal."
5. ❌ *Claim 5:* "DINOv2 codifica la totalidad de la información estructural contenida en una imagen médica."
6. ❌ *Claim 6:* "La asociación estadística entre descriptores y parches implica una relación causal biológica."
7. ❌ *Claim 7:* "Un valor elevado de ROC-AUC implica automáticamente utilidad diagnóstica o beneficio clínico."

---

## 5. SEPARACIÓN DE LÍNEAS DE INVESTIGACIÓN (TRACKS)

```text
                                  LATTICE BIO
                                       │
                ┌──────────────────────┴──────────────────────┐
                ▼                                             ▼
       TRACK A (PAPER 1)                             TRACK B (FUTURO)
"Fenotipo Estructural & Metodología"          "Endpoint Clínico Diagnóstico"
- Estabilidad computacional                   - Asoc. con Pérdida Ósea (RBL %)
- Complementariedad Math + DINOv2             - Nivel de Inserción Clínica (CAL)
- Control estricto de sesgos                  - Estadificación Periodontal (AAP)
```

### Track A — Structural / Methodological (Alcance del Paper 1):
Responde a si los descriptores matemáticos caracterizan de manera reproducible patrones estructurales en proyecciones radiográficas y si aportan información no redundante a representaciones profundas auto-supervisadas.

### Track B — Clinical (Estudio Secundario Futuro):
Evaluación de la asociación cuantitativa de dichos descriptores con endpoints clínicos validados por paneles odontológicos (RBL %, CAL, Staging AAP). *Fuera del alcance de la primera publicación.*

---

## 6. ANÁLISIS DE OPCIONES DE GROUND TRUTH Y RIESGOS DE CIRCULARIDAD

| Opción de Ground Truth / Target | Ventajas | Limitaciones | Riesgo de Circularidad / Leakage | Decisión Metodológica |
| :--- | :--- | :--- | :--- | :--- |
| **Opción A: Fenotipo Estructural Anatómico Independiente** | Transparente, no requiere metadata subjetiva. | No representa directamente enfermedad clínica. | 🟢 **Bajo.** Compara regiones anatómicas independientes sin etiquetas arbitrarias. | **Adoptado para Track A / Paper 1.** |
| **Opción B: Medición Radiográfica Independiente (CEJ-AC / RBL %)** | Métrica objetiva continua de soporte óseo. | Requiere anotación experta de puntos anatómicos. | 🟢 **Bajo.** Métrica física cuantificable. | **Recomendado para Track B.** |
| **Opción C: Endpoint Clínico (CAL / Staging AAP)** | Alta relevancia diagnóstica. | Ausente en datasets públicos actuales. | 🟢 **Bajo.** Ground truth médico estándar. | **Requiere nuevo dataset clínico.** |
| **Opción D: Etiquetas Derivadas de la Misma Apariencia Visual** | Fácil de implementar sintéticamente. | Definición circular: predice la textura con la misma textura. | 🔴 **CRÍTICO.** *Target Leakage / Circularity*. | **PROHIBIDO E INVALIDADO.** |

---

## 7. DEFINICIÓN METODOLÓGICA DE "INFORMACIÓN COMPLEMENTARIA"

No se considerará que la fusión ($M3$) aporta información complementaria simplemente porque $\text{AUC}_{\text{Fusion}} > \text{AUC}_{\text{DINOv2}}$.

### Criterios Múltiples Exigidos para Demostrar Complementariedad:
1. **Mejora en Muestra Independiente ($\Delta\text{AUC}$):** $\Delta\text{AUC} > 0$ en el Holdout congelado con un intervalo de confianza al 95% (Paired Patient Bootstrap) que **excluya el valor cero**.
2. **Confiabilidad Computacional ($\text{ICC} > 0.75$ / Low CV):** Los descriptores matemáticos deben ser estables ante perturbaciones físicas de ruido y rotación (Fase 5).
3. **No-Redundancia Matemática (Partial Correlation):** Demostrar que los descriptores seleccionados poseen varianza no explicada por las componentes principales del espacio latente de DINOv2.
4. **Consistencia en Ablación:** El incremento de desempeño debe ser atribuible a familias matemáticas específicas en la Fase 10.

---

## 8. ALCANCE ESPECÍFICO DEL PAPER 1

### Título de Trabajo Ajustado:
> **"Mathematical Characterization of Trabecular Patterns in 2D Dental Radiographs: Evaluating Structural Complementarity with Self-Supervised Visual Representations"**

### Incluido en Paper 1:
* Control estricto de independencia por paciente (`GroupKFold` + Holdout 20% retenido).
* Prueba de estabilidad computacional ante perturbaciones para cada descriptor.
* Evaluación de complementariedad entre representaciones auto-supervisadas (DINOv2) y geometría trabecular.
* Sanity check via *Label Permutation Test* y diagnóstico de sesgo de fuente.

### Excluido de Paper 1:
* Diagnóstico de periodontitis o clasificación clínica de pacientes.
* Reconstrucción 3D de microarquitectura.
* Afirmaciones de utilidad o efectividad en la práctica clínica.

---

## 9.DECISIONES METODOLÓGICAS ABIERTAS

1. **Rango de Momentos $q$:** Se elegirá en la Fase 4 basándose en la linealidad de $\tau(q)$ ($R^2 > 0.95$) y estabilidad numérica, no en el AUC del clasificador.
2. **Métricas de Rendimiento:** Paired Patient-Level Bootstrap para $\Delta\text{AUC}$ como métrica inferencial primaria; DeLong como análisis secundario únicamente si la anidación del modelo lo justifica.
