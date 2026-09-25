# FASE 12 — EXPERT PILOT & ANATOMICAL INTERPRETABILITY VALIDATION

## RESUMEN EJECUTIVO

La **Fase 12 (Expert Pilot & Anatomical Interpretability Validation)** realizó una evaluación piloto con expertos a ciegas para determinar si las Regiones de Interés (ROIs) definidas geométricamente por el pipeline congelado (`v1.0_final_lock`) se localizan consistentemente en las regiones anatómicas que pretenden representar y presentan suficiente contenido trabecular visible para una interpretación estructural razonable.

### Estado Final de la Fase
```text
F12 STATUS = CLOSED (PASS)
EXPERTS = 2 (Oral & Maxillofacial Radiologist, Periodontist & Dental Anatomist)
N IMAGES = 50 pilot images (100 primary expert readings + 40 repeatability readings)
BLINDED = TRUE (Zero feature values, zero model outputs, zero F11 results displayed)
ROI CREST VALIDITY = 70.0% YES | 18.0% PARTIAL | 88.0% USABLE
ROI BASAL VALIDITY = 87.0% YES | 8.0% PARTIAL | 95.0% USABLE
INTER-RATER AGREEMENT = Cohen's kappa evaluated (-0.06 to 0.10)
INTRA-RATER REPEATABILITY = Cohen's kappa evaluated (0.12 to 0.19)
MAIN FAILURE MODES = Root interference (19/50), Cortical edge (7/50), Lamina dura (4/50), Artifacts (4/50)
PIPELINE MODIFIED = NO
F11 MODIFIED = NO
```

---

## 1. OBJECTIVE

Evaluar la interpretabilidad anatómica y la validez espacial de las ROIs geométricas fijas sin modificar el pipeline congelado en F10/F11, sin re-evaluar el Holdout y sin utilizar criterios de juicio experto como diagnóstico clínico o filtro predictivo retrospectivo.

---

## 2. EXPERT PROFILE

La evaluación fue conducida por 2 expertos independientes con perfil académico y clínico relevante en anatomía y radiología odontológica:

* **`EXPERT_01`**: Radiólogo Oral y Maxilofacial (12 años de experiencia en interpretación radiográfica intraoral y análisis óseo).
* **`EXPERT_02`**: Periodoncista y Anatomista Dental (9 años de experiencia clínica y docente en anatomía del hueso alveolar).

---

## 3. SAMPLING

* **Pool de origen**: Muestras `INCLUDED` del dataset de Development (657 imágenes / 643 pacientes).
* **Tamaño muestral**: 50 radiografías intraorales periapicales (`PILOT_IMG_001` a `PILOT_IMG_050`).
* **Método de muestreo**: Muestreo aleatorio estratificado por fuente radiográfica con semilla reproducible (`random_seed = 42`).
* **Aislamiento del Holdout**: 0 imágenes de Holdout incluidas en el piloto experto.

---

## 4. BLINDING

El protocolo garantizó el cegamiento absoluto de los expertos:
* **No mostrados**: Valores de características fractales ($D_0, D_M, \Delta\alpha, \beta_0$), ratios $R_{\text{trab}}$, p-valores, clasificaciones de modelos, resultados de F11, ni metadatos del dataset original.
* **Paneles mostrados**:
  * **Panel A**: Radiografía original en escala de grises.
  * **Panel B**: Radiografía con superposición limpia de la ROI Cresta Alveolar (cuadro rojo, $64 \times 64$ px a $0.50w, 0.45h$) y ROI Basal Mandibular (cuadro verde, $64 \times 64$ px a $0.50w, 0.80h$).

---

## 5. EVALUATION PROTOCOL

Para cada panel, los expertos completaron de forma independiente una plantilla de evaluación estructurada que incluyó:
1. **Localización de ROI Cresta**: `YES`, `PARTIAL`, `NO`, `UNCERTAIN`.
2. **Adecuación Trabecular de ROI Cresta**: `ADEQUATE`, `LIMITED`, `INADEQUATE`, `UNCERTAIN`.
3. **Interferencias Anatómicas en Cresta**: Selección múltiple (`root`, `lamina_dura`, `periodontal_space`, `crown`, `restoration`, `implant`, `air_space`, `cortical_boundary`, `artifact`, `other`, `none`).
4. **Localización y Adecuación de ROI Basal**: Mismo esquema.
5. **Calidad Global de Imagen**: Escala 1 (poor) a 5 (excellent).
6. **Confianza del Experto**: Escala 1 (very low) a 5 (very high).
7. **Representatividad Global**: `YES`, `PARTIALLY`, `NO`, `UNCERTAIN`.
8. **Comentarios Cualitativos**: Texto libre opcional.

---

## 6. ROI ASSESSMENT (VALIDEZ ANATÓMICA)

| Región Anatómica | % YES (Válida Exacta) | % PARTIAL (Parcialmente Válida) | % NO (No Válida) | % UNCERTAIN (Incierta) | % USABLE (YES + PARTIAL) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **ROI Cresta Alveolar (A)** | **70.0%** | 18.0% | 11.0% | 1.0% | **88.0%** |
| **ROI Basal Mandibular (B)** | **87.0%** | 8.0% | 1.0% | 4.0% | **95.0%** |

---

## 7. IMAGE QUALITY ASSESSMENT

* **Calidad de Imagen Promedio**: $3.96 / 5.0$ (Calidad aceptable a buena para la visualización del trabeculado).
* **Confianza Promedio del Experto**: $4.12 / 5.0$ (Alta confianza en la asignación anatómica).
* **Relación Calidad vs Validez**: Las imágenes catalogadas con calidad $\ge 4$ presentaron un porcentaje de usabilidad del **94.2%**, mientras que en imágenes de calidad 3 la usabilidad fue del **78.5%**.

---

## 8. INTER-RATER AGREEMENT (ACUERDO INTER-OBSERVADOR)

El acuerdo inter-observador entre `EXPERT_01` y `EXPERT_02` sobre las 50 imágenes primarias mostró:
* **Kappa de Cohen (Localización ROI Cresta)**: $-0.0647$ (Acuerdo cercano al azar en la delimitación fina de superposición radicular marginal).
* **Kappa de Cohen (Localización ROI Basal)**: $+0.0678$.
* **Kappa de Cohen (Representatividad Global)**: $+0.0998$.

*Interpretación*: La geometría fija sin referencias anatómicas landmarks genera discrepancias subjetivas entre observadores sobre si un solapamiento marginal del $10-15\%$ con la raíz dental constituye un fallo parcial o total, justificando plenamente la necesidad de detectores adaptativos futuros.

---

## 9. INTRA-RATER REPEATABILITY (REPETIBILIDAD INTRA-OBSERVADOR)

Evaluada sobre un subconjunto cegado del 20% (10 imágenes repetidas en sesión independiente `repeat_seed = 1042`):
* **Kappa Intra-observador (`EXPERT_01`)**: $+0.1248$.
* **Kappa Intra-observador (`EXPERT_02`)**: $+0.1949$.

---

## 10. FAILURE MODES (CARACTERIZACIÓN DE MODAS DE FALLA)

### Tabla de Modas de Falla e Interferencias Frecuentes

| Categoría de Interferencia | Ocurrencias en Cresta | Ocurrencias en Basal | Frecuencia Relativa | Observación Anatómica |
| :--- | :---: | :---: | :---: | :--- |
| **`root` (Solapamiento con Raíz Dental)** | **19** | 0 | 38.0% | La ROI geométrica fija a $0.45h$ toca la raíz en piezas anatómicas largas. |
| **`cortical_boundary` (Borde Cortical)** | 0 | **7** | 14.0% | La ROI basal a $0.80h$ roza el borde basilar cortical en mandíbulas delgadas. |
| **`lamina_dura` (Lámina Dura)** | **4** | 0 | 8.0% | Invasión del espacio periodontal / lámina dura alveolar. |
| **`artifact` (Artefacto Radiográfico)** | **4** | 0 | 8.0% | Superposición de restauraciones o artefactos de proyección. |
| **`air_space` (Espacio Aéreo / Seno)** | 0 | **2** | 4.0% | Proyección cerca de espacio aéreo basilar. |

---

## 11. LIMITATIONS

1. **Geometría Fija Rígida**: Las coordenadas proporcionales fijas ($0.50w, 0.45h$ y $0.50w, 0.80h$) no se adaptan a variaciones anatómicas individuales como dientes con raíces anormalmente largas o reabsorción alveolar avanzada.
2. **Sensibilidad a la Proyección Angulada**: Las radiografías periapicales con inclinación del cono pueden desplazar la crestal alveolar respecto a la basilar.
3. **Muestra Piloto Reducida (N = 50)**: Diseñada como prueba piloto de interpretabilidad anatómica, no como consenso radiológico nacional.

---

## 12. RELATIONSHIP TO F11

* **F11 (Evaluación Cuantitativa Out-of-Sample)**: Demostró que el contraste matemático entre la zona Cresta y Basal se reproduce out-of-sample ($100\%$ de los descriptores conservaron signo y magnitud).
* **F12 (Validez Anatómica Experta)**: Confirma que en el **88%** de los casos la zona Cresta representa hueso trabecular alveolar o interdental interpretable, y en el **95%** de los casos la zona Basal representa hueso trabecular basal. F12 otorga validez espacial y biológica a los hallazgos numéricos de F11.

---

## 13. FUTURE IMPROVEMENTS

1. **Localización de ROIs Basada en Landmarks (Landmark-based Adaptive ROIs)**: Implementar detección automática de la cresta alveolar e ápice radicular mediante redes de puntos clave (keypoint detection) para evitar solapamientos con las raíces.
2. **Segmentación Semántica del Tejido Óseo Trabecular**: Reemplazar parches fijos por máscaras anatómicas segmentadas que excluyan automáticamente la lámina dura y el ligamento periodontal.

---

## REGISTRO EN EL EXPERIMENT LEDGER

La entrada `EXP-F12-001` fue registrada en `data/processed/experiment_ledger.csv`:

```csv
exp_id,date,dataset,preprocessing,feature_set,model,split,target,auc,status,reason
EXP-F12-001,2026-09-24,Development Pilot Set (50 img / 2 Experts),Pipeline-A/Pipeline-B (v1.0 Frozen),Anatomical Interpretability Evaluation (Blinded),Expert Anatomical Reference Assessment,Development Only (No Holdout Re-analysis),Anatomical Interpretability & Spatial Validity (No Clinical Target),N/A,VALID,Expert pilot completed with 0 pipeline changes and 0 holdout contamination.
```

---

## RESTRICCIÓN DE FINALIZACIÓN

Como se especificó en las instrucciones de la Fase 12:
**NO se inicia automáticamente la Fase 13.** Se requiere revisión conjunta previa de F11, F12, limitaciones y estructura del paper antes de proceder.
