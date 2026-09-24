# ESPECIFICACIÓN DE REFERENCIA ANATÓMICA Y MEDICIÓN ESTRUCTURAL (FASE 3 - EDICIÓN CORREGIDA V2.0)
## PROYECTO: LATTICE BIO
**Fecha de Emisión:** 2026-09-24  
**Estado:** Inmutable / Especificación Corregida de Fase 3  
**Dataset de Referencia:** `data/processed/final_dataset_manifest.csv` (850 imágenes / 805 pacientes)  
- Development Set: 643 pacientes únicos (657 imágenes)  
- Holdout Set: 162 pacientes únicos (193 imágenes) [Congelado SHA256: `85e3a856e5a1334d53084f242fff50a92c1c662fe1d4c8797053261578d2b335`]

---

## 1. DESGLOSE CONCEPTUAL EN TRES NIVELES ESTRUCTURALES

Para evitar circularidades metodológicas y afirmaciones clínicas prematuras, la conceptualización del estudio se divide estrictamente en tres niveles jerárquicos:

```text
                                  LATTICE BIO
                                       │
      ┌────────────────────────────────┼────────────────────────────────┐
      ▼                                ▼                                ▼
NIVEL 1: ANATOMICAL REFERENCE    NIVEL 2: STRUCTURAL MEASUREMENT   NIVEL 3: CLINICAL GROUND TRUTH
(Cresta Alveolar vs Hueso Basal) (Descriptores D₀, D_M, Λ, Δα)    (RBL %, CAL, AAP Staging)
🟢 Referencia geométrica fija    🟢 Variables de medición         🔴 NO DISPONIBLE en dataset
```

### Nivel 1 — Anatomical Reference (Referencia Anatómica Independiente)
* **Definición:** Comparación entre la **Cresta Alveolar Interdental** y la **Región Basal Trabecular** del mismo paciente.
* **Carácter:** Las regiones se definen mediante criterios anatómicos y geométricos fijos respecto a la dentición, **de forma totalmente independiente de la textura, intensidad o apariencia visual de la imagen**.
* **Precisión:** Constituye una *referencia anatómica independiente*, NO un ground truth clínico de enfermedad.

### Nivel 2 — Structural Measurement (Variables de Medición Estructural)
* **Definición:** Descriptores matemáticos ($D_0$, Minkowski/Peleg $D_M$, Lacunaridad $\Lambda$, Espectro Multifractal $\Delta\alpha$, Topología $\beta_0, \beta_1$).
* **Carácter:** Son *variables de medición cuantitativa de textura y geometría*. NO constituyen ground truth ni biomarcadores diagnósticos.

### Nivel 3 — Clinical Ground Truth (Ground Truth Clínico Diagnóstico)
* **Definición:** Pérdida Ósea Radiográfica cuantificada ($RBL\%$), Nivel de Inserción Clínica ($CAL$), Estadificación Periodontal ($AAP\text{ Staging I-IV}$) o diagnóstico periodontal clínico independiente.
* **Estado:** **NO DISPONIBLE** en los datasets públicos actuales.
* **Regla Inviolable:** **NO AFIRMAR DIAGNÓSTICO DE PERIODONTITIS NI DETECCIÓN DE ENFERMEDAD EN EL PAPER 1.**

---

## 2. REDEFINICIÓN DEL ÍNDICE STRUCTURAL $R_{\text{trab}}$

El índice relativo trabecular intra-paciente se formula como:

$$R_{\text{trab}}(D) = \frac{D(\text{ROI Cresta Alveolar Interdental})}{D(\text{ROI Hueso Basal Trabecular del Mismo Paciente})}$$

* **Denominación Formal:** **Relative Trabecular Structural Index** (*Índice Estructural Relativo Trabecular Intra-Paciente / Intra-Imagen*).
* **Restricción Terminológica:** Prohibido catalogarlo como "ground truth", "biomarcador", "diagnóstico" o "medición directa de densidad mineral".

---

## 3. FORMULACIÓN HIPO-TÉTICA DE NORMALIZACIÓN (REVISADA)

Se elimina cualquier afirmación que sugiera la cancelación automática de confusores. Se adopta la siguiente formulación prudente:

> **"$R_{\text{trab}}$ se propone como una hipótesis de estrategia de normalización intra-paciente / intra-imagen destinada a reducir parte de la variabilidad global compartida entre regiones de una misma adquisición. Su capacidad real para mitigar efectos de adquisición, sensor, contraste y otras fuentes de variabilidad técnica deberá evaluarse empíricamente y no se asumirá como una garantía automática."**

---

## 4. ALCANCE Y LIMITACIONES DEL PAPER 1

### Lo que SÍ puede estudiar el Paper 1:
1. Si los descriptores matemáticos cuantifican de forma reproducible diferencias entre regiones anatómicas definidas independientemente (Cresta Alveolar Interdental vs Hueso Basal).
2. Si dichas representaciones estructurales aportan información complementaria a representaciones profundas auto-supervisadas (DINOv2).

### Lo que NO puede afirmar el Paper 1:
* ❌ Que detecta o diagnostica periodontitis.
* ❌ Que detecta pérdida ósea clínica o patología.
* ❌ Que mide densidad mineral ósea (BMD).
* ❌ Que representa directamente la microarquitectura trabecular 3D.
* ❌ Que una diferencia cresta/basal equivale a enfermedad.
* ❌ Que $R_{\text{trab}}$ es un biomarcador clínico validado.

---

## 5. REVISIÓN DEL RIESGO DE CIRCULARIDAD DE ENDPOINTS

| Candidato a Target / End-Point | ¿Construido a partir de la apariencia visual que se busca predecir? | Clasificación de Riesgo | Diagnóstico y Decisión |
| :--- | :--- | :---: | :--- |
| `source_dataset` name | No directamente, pero codifica tipo de cámara/sensor y resolución. | 🔴 **CIRCULAR / TARGET LEAKAGE** | ❌ **PROHIBIDO** |
| Densidad visual basada en apariencia | Sí: define la etiqueta mediante la misma apariencia/brillo que mide. | 🔴 **CIRCULAR / TARGET LEAKAGE** | ❌ **PROHIBIDO** |
| **Referencia Anatómica (Cresta vs Basal)** | **No:** Las regiones se definen por geometría anatómica fija (dentición). | 🟢 **INDEPENDIENTE ANATÓMICAMENTE** | ✅ **ADOPTADO** |

*Precisión de Independencia:* La independencia se refiere exclusivamente a la **definición anatómica de las regiones**, no a la existencia de un ground truth externo de alteración estructural o enfermedad clínica.

---

## 6. FASE 3 AUDIT MATRIX (REVISIÓN DE CORRECCIÓN)

| Criterio de Auditoría | Estado | Diagnóstico y Verificación Metodológica |
| :--- | :---: | :--- |
| **Cresta vs Basal como Referencia Anatómica** | ✅ | Definido estrictamente como *Anatomical Reference* (Nivel 1), no como ground truth. |
| **No presentado como Clinical Ground Truth** | ✅ | Confirmado. Clinical Ground Truth declarado explícitamente como NO DISPONIBLE (Nivel 3). |
| **$R_{\text{trab}}$ definido como Índice Relativo** | ✅ | Catalogado como *Relative Trabecular Structural Index*, prohibido llamarlo biomarcador. |
| **Normalización prudente (No garantizada)** | ✅ | Formulado como hipótesis de normalización a evaluar empíricamente. |
| **Clinical Ground Truth declarado ausente** | ✅ | Ausencia declarada de CAL, RBL% y AAP Staging en datasets actuales. |
| **Circularidad diferenciada** | ✅ | Independencia acotada a la posición anatómica fija, no a ground truth de alteración. |
| **No se afirma diagnóstico de Periodontitis** | ✅ | Prohibición explícita de claims diagnósticos en Paper 1. |
| **No se afirma medición 3D desde 2D** | ✅ | Prohibición explícita de inferir 3D desde proyecciones 2D. |
| **Cero Análisis Científico / Feature Computation** | ✅ | Ningún cálculo fractal, multifractal, TDA, DINOv2 ni AUC ejecutado. |
| **Dataset sin Modificaciones** | ✅ | `final_dataset_manifest.csv` intacto sin cambios en imágenes ni splits. |
| **Holdout sin Modificaciones** | 🔒 | SHA256 `85e3a856...` verificado e idéntico byte-a-byte. |
| **Fase 4 No Iniciada** | 🛑 | **STOP:** Detenido antes del inicio de la Fase 4. |

---

## 📌 VERDICTO FINAL DE FASE 3 — CORRECCIÓN

### FASE 3 — CORRECCIÓN
**Estado:** 🟢 **CERRADA DEFINITIVAMENTE**

### RESUMEN DE LA CORRECCIÓN DOCUMENTAL:
1. **Documento Actualizado:** `docs/ground_truth_v1.md` corregido e integrado con la terminología de tres niveles (*Anatomical Reference*, *Structural Measurement*, *Clinical Ground Truth*).
2. **Definición de $R_{\text{trab}}$:** Ajustado como *Relative Trabecular Structural Index*, reformulando la hipótesis de normalización como algo a evaluar empíricamente.
3. **Clinical Ground Truth:** Declarado **NO DISPONIBLE**. Cero claims diagnósticos de periodontitis.
4. **Holdout Congelado:** SHA256 verificado e idéntico byte-a-byte (`85e3a856e5a1334d53084f242fff50a92c1c662fe1d4c8797053261578d2b335`).

---

🛑 **STOP ABSOLUTO:** Corrección documental completada $\longrightarrow$ Auditoría finalizada $\longrightarrow$ Cierre definitivo de Fase 3 $\longrightarrow$ **STOP**. Quedo a la espera de autorización previa antes de abordar la Fase 4.
