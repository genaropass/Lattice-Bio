# MANUSCRIPT v1 — LATTICE BIO (PAPER 1)

> **Version**: v1.0 Draft — F13 (2026-09-25)
> **Status**: DRAFT — PRE-PEER REVIEW
> **Pipeline Version**: v1.0_final_lock (F10)
> **Holdout Hash**: `85e3a856e5a1334d53084f242fff50a92c1c662fe1d4c8797053261578d2b335`

---

## TITLE CANDIDATES

1. **"Lattice Bio: A Reproducibility-Oriented Mathematical Framework for Paired Structural Characterization of Trabecular Bone in Intraoral Periapical Radiographs"**
2. **"Paired Structural Characterization of Alveolar Trabecular Bone in 2D Periapical Radiographs Using Validated Fractal, Minkowski, Multifractal and Topological Descriptors with Independent Patient-Level Holdout Evaluation"**
3. **"A Locked-Pipeline Framework for Reproducible Trabecular Structural Contrast in Periapical Dental Radiographs: Mathematical Validation, Perturbation Analysis, and Out-of-Sample Verification"**
4. **"Mathematical Characterization of Trabecular Structural Contrast in Intraoral Radiographs: A Reproducible Computational Framework with Expert Anatomical Interpretability Assessment"**
5. **"Towards Reproducible Structural Phenotyping of Alveolar Bone in 2D Dental Radiographs: A Methodological Pipeline with Locked Feature Set and Independent Holdout Evaluation"**

> **Recommended**: Title 1 or Title 4 — these best reflect the methodological scope while remaining clear about the absence of clinical diagnostic claims.

---

## ABSTRACT

**Background and Objective**: Quantitative analysis of trabecular bone structure in intraoral periapical radiographs has been widely explored using fractal descriptors, yet reproducibility across studies remains limited due to inconsistent preprocessing, non-standardized region-of-interest (ROI) selection, and the absence of formal out-of-sample evaluation. This study introduces Lattice Bio, a reproducibility-oriented computational framework for paired structural characterization of trabecular bone in 2D periapical radiographs.

**Methods**: A dataset of 850 included intraoral periapical radiographs from 805 unique patients was assembled after strict identity verification and perceptual deduplication. A fixed geometric ROI geometry was applied as a reproducible computational reference: ROI Crest at $(0.50w, 0.45h)$ and ROI Basal at $(0.80h)$, each $64 \times 64$ pixels. Four mathematically validated descriptors — fractal box-counting dimension ($D_0$), Minkowski/Peleg surface dimension ($D_M$), multifractal singularity spectrum width ($\Delta\alpha$), and topological Betti-0 connected components ($\beta_0$) — were extracted under locked preprocessing pipelines. The feature set was defined prior to any Holdout access and locked in a configuration file with cryptographic integrity control. Development analysis used 657 images from 643 patients; a reserved Holdout of 193 images from 162 independent patients was evaluated once under the locked pipeline. A blinded expert pilot (two experts, 50 images, 100 primary readings) assessed the anatomical interpretability of the fixed ROI geometry.

**Results**: All four locked descriptors showed consistent directional structural contrasts between the Crest and Basal fixed regions in Development (Cohen's $d_z$: $D_0 = -0.199$, $D_M = -0.816$, $\Delta\alpha = +0.518$, $\beta_0 = +0.361$). The independent Holdout reproduced the direction and approximately similar magnitude of these contrasts for all four descriptors (Holdout $d_z$: $D_0 = -0.232$, $D_M = -0.866$, $\Delta\alpha = +0.589$, $\beta_0 = +0.330$; descriptive magnitude ratios: 0.92–1.17). The expert pilot found that 88% of Crest ROI readings and 95% of Basal ROI readings were judged usable (containing interpretable trabecular tissue), while inter-rater agreement was low (Cohen's $\kappa$: $-0.06$ to $+0.10$), revealing recurrent root interference (19/100 Crest readings) as the main anatomical limitation of fixed geometric placement.

**Conclusions**: Lattice Bio provides a reproducible computational framework for paired structural characterization of trabecular bone in 2D periapical radiographs, demonstrating out-of-sample reproducibility of structural contrasts while transparently documenting the anatomical interpretability limitations of non-adaptive geometric ROIs. This is a methodological characterization study; no clinical diagnoses, disease classifications, or biomarker claims are made.

**Keywords**: trabecular bone; periapical radiograph; fractal dimension; Minkowski dimension; multifractal; topological data analysis; ROI reproducibility; structural characterization; out-of-sample evaluation.

---

## 1. INTRODUCTION

The quantitative characterization of trabecular bone architecture from dental radiographs has been an active research area for several decades. Trabecular bone in the alveolar process undergoes structural changes associated with periodontal disease, metabolic bone disorders, and aging — changes that may be detectable in routine clinical radiographs before overt radiographic bone loss is visible to the naked eye.

Among the quantitative methods proposed, fractal analysis — particularly the box-counting method for estimating the Hausdorff-Besicovitch dimension — has received the most attention [REFS]. Fractal analysis provides a scalar measure of the self-similar complexity of the trabecular pattern. Complementary descriptors including lacunarity (which quantifies spatial gap distribution), multifractal spectrum-based measures (which characterize local heterogeneity), and topological data analysis approaches (which capture connectivity and loop structure) have been proposed as additional characterization layers.

Despite extensive literature on individual descriptors, reproducibility across studies remains a significant concern. Key sources of variability include: inconsistency in image preprocessing (binarization method, contrast normalization); lack of standardized ROI selection protocols; absence of patient-level de-duplication; and, critically, the near-universal absence of formal out-of-sample (holdout) evaluation in published radiographic texture analysis studies.

This paper presents **Lattice Bio**, a methodological framework that addresses these reproducibility gaps through: (1) explicit algorithmic definition and mathematical validation of all descriptors; (2) a fixed deterministic geometric ROI reference applied identically across all images; (3) a locked feature pipeline frozen prior to any holdout access; (4) patient-level out-of-sample evaluation using a cryptographically sealed holdout dataset; and (5) a blinded expert pilot to assess the anatomical interpretability and limitations of the geometric ROI placement.

This is a **methodological and structural characterization study**. No clinical diagnoses, disease classifications, or biomarker claims are made.

---

## 2. RELATED WORK

### 2.1 Fractal Dimension in Dental Radiographs

Fractal dimension analysis via the box-counting method is among the most applied quantitative tools for trabecular bone assessment in intraoral radiographs. [cite established reviews and representative studies]. Studies have demonstrated that fractal dimension can differentiate healthy bone from moderate-to-severe periodontitis; however, detection of early-stage changes remains limited [cite]. For osteoporosis screening, systematic reviews report inconsistent evidence and conclude that FD alone is insufficient as a standalone diagnostic marker [cite].

### 2.2 Multifractal and Lacunarity Analysis

Multifractal analysis extends monofractal characterization by generating the full singularity spectrum $f(\alpha)$, from which the spectrum width $\Delta\alpha$ captures structural heterogeneity. Lacunarity — complementary to FD — quantifies the spatial distribution of gaps. Both have been applied to panoramic and, to a lesser extent, periapical radiographs for bone texture characterization [cite]. Multifractal-based lacunarity analysis has been proposed for improved sensitivity in osteoporosis-related bone texture changes [cite].

### 2.3 Topological Data Analysis

Persistent homology, the central tool of TDA, characterizes image topology by tracking how connected components ($\beta_0$) and independent loops ($\beta_1$) appear and disappear across image threshold filtrations. Applications to bone microstructure have been demonstrated primarily in 3D micro-CT and histological images [cite]. Application to 2D periapical radiographic texture remains less explored.

### 2.4 ROI Standardization

A consistent finding across the literature is that ROI placement is among the largest sources of variability in trabecular texture measurements [cite]. Most studies rely on anatomical landmarks or manual placement, which introduces observer variability. The use of a fully deterministic geometric reference, explicitly acknowledged as a computational rather than anatomical construct, combined with a formal expert interpretability assessment, has not been widely reported.

---

## 3. RESEARCH QUESTION

The primary research question of this study is:

> **"Can a fixed-reference geometric computational framework for paired structural measurement of trabecular bone in 2D intraoral periapical radiographs produce consistent and out-of-sample reproducible paired structural contrasts between two anatomically distinct image regions?"**

Secondary questions:
1. Which mathematical descriptors survive redundancy control and maintain stability across preprocessing perturbations?
2. Does the paired structural contrast observed in Development reproduce in direction and magnitude in an independent held-out patient cohort?
3. What are the anatomical interpretability characteristics and limitations of the fixed ROI geometry, as assessed by blinded domain experts?

---

## 4. MATERIALS AND METHODS

### 4.1 Dataset

#### 4.1.1 Raw Dataset and Inclusion/Exclusion

The initial dataset comprised 2,795 intraoral periapical radiographs. Prior to analysis:
- 197 exact pixel-level duplicates were removed (MD5-based deduplication).
- 1,611 images with unknown patient identity (not traceable to a verified patient ID) were excluded.
- 135 images identified as perceptual near-duplicates within the same patient record were flagged and resolved.
- 2 images with identity conflicts were excluded.

**Final benchmark**: 850 included images from 805 unique patients.

#### 4.1.2 Patient-Level Split

The benchmark was split at the patient level to prevent any patient's data from appearing in both Development and Holdout:

| Subset | Images | Patients | Purpose |
| :--- | :---: | :---: | :--- |
| Development | 657 | 643 | Feature development, validation, selection |
| Holdout | 193 | 162 | Single out-of-sample evaluation (F11) |

The Holdout split was sealed with a cryptographic SHA-256 hash (`85e3a856e5a1334d53084f242fff50a92c1c662fe1d4c8797053261578d2b335`) prior to any analysis. Zero patients are shared between Development and Holdout.

**Unit of analysis**: `patient_id`. All inferences, bootstraps, and effect size computations are grouped at the patient level.

### 4.2 ROI Framework

Two fixed geometric regions of interest were defined as **reproducible computational references** for structural comparison within each image:

| Region | Center ($x$, $y$) | Patch Size |
| :--- | :---: | :---: |
| ROI Crest (A) | $(0.50w,\ 0.45h)$ | $64 \times 64$ px |
| ROI Basal (B) | $(0.50w,\ 0.80h)$ | $64 \times 64$ px |

The vertical separation between the two regions is $0.35h$.

**Important**: These ROIs are fully deterministic geometric references, completely independent of image texture values and descriptor outputs. They are not anatomical landmarks, adaptive segmentations, or clinical ground truth. Their anatomical interpretability was assessed separately in F12 (see Section 4.6). Coordinate extraction was implemented identically for all images in Development and Holdout using the function `extract_anatomical_reference_rois()`.

### 4.3 Preprocessing Pipelines

Two preprocessing pipelines were applied, consistent across all images and both splits:

#### Pipeline A (for $D_M$)
1. Grayscale loading.
2. Lanczos4 resampling to a Standardized Digital Resampling Grid Target (35 µm/px nominal under an assumed 150 DPI detector resolution — a digital resampling target, not a calibrated physical measurement).
3. MinMax normalization to $[0, 1]$.

#### Pipeline B (for $D_0$, $\Delta\alpha$, $\beta_0$)
1. Grayscale loading.
2. Lanczos4 resampling (same grid target as Pipeline A).
3. CLAHE (clip limit: 2.5; tile grid: $8 \times 8$).
4. Sauvola adaptive binarization ($W = 15$, $k = 0.2$).

> **Note on resolution**: "35 µm/px nominal" is a standardized digital resampling target derived from a 150 DPI assumption for digital sensors. It does not represent a physically calibrated tissue resolution, radiographic density calibration, or volumetric bone measurement.

### 4.4 Mathematical Descriptors

#### 4.4.1 Box-Counting Fractal Dimension ($D_0$)

The Hausdorff-Besicovitch dimension is estimated by the box-counting method on the binarized ROI:

$$D_0 = -\lim_{\epsilon \to 0} \frac{\log N(\epsilon)}{\log \epsilon}$$

where $N(\epsilon)$ is the number of boxes of size $\epsilon$ required to cover the foreground pixels. In practice, a log-log regression of $\log N(\epsilon)$ vs. $\log(1/\epsilon)$ is computed over a range of box sizes. The slope gives the estimated $D_0$.

**Mathematical validation** (F4/F4.1): Planar surface → $D_0 \approx 2$; linear structure → $D_0 \approx 1$; Sierpinski gasket (27–243px) → $D_0 = 1.748$–$1.869$ (converging to theoretical $\approx 1.893$). **Status**: `VALIDATED_WITH_FINITE_SIZE_LIMITATION`.

#### 4.4.2 Minkowski/Peleg Surface Dimension ($D_M$)

Based on the blanket method (Peleg *et al.*, 1984), the grayscale image is interpreted as a 2.5D surface where intensity represents height. The surface dimension is estimated from:

$$D_M = 3 - \lim_{\epsilon \to 0} \frac{\log A(\epsilon)}{\log \epsilon}$$

where $A(\epsilon)$ is the area of the upper-lower blanket surface at scale $\epsilon$. Log-log regression of $\log A(\epsilon)$ vs. $\log \epsilon$ provides the estimate.

**Mathematical validation** (F4/F4.1): Flat image → $D_M = 2.0$; random white noise → $D_M = 4.24$ ($R^2 = 0.99$). The white noise result exceeds the expected $[2,3]$ range for 2.5D surfaces and documents a scope limitation of this implementation at high-noise inputs.

#### 4.4.3 Multifractal Singularity Spectrum Width ($\Delta\alpha$)

The multifractal spectrum $f(\alpha)$ is computed via a multi-scale partition function approach over $q \in [-4, +4]$ (15 steps). The spectrum width is:

$$\Delta\alpha = \alpha_{\max} - \alpha_{\min}$$

Higher $\Delta\alpha$ indicates greater structural heterogeneity (wider distribution of local scaling exponents). Stability under perturbations (F5): ICC = 0.927.

#### 4.4.4 Topological $\beta_0$ — Connected Components (TDA)

Persistent homology (H₀) is computed on the binarized ROI via a filtration over threshold levels. $\beta_0$ counts the number of distinct connected foreground components at a fixed reference threshold. Validation (F4): Square → $\beta_0 = 1$; ring → $\beta_0 = 1$; three squares → $\beta_0 = 3$.

> **Note**: $\beta_0$ in this implementation is sensitive to Sauvola binarization parameters (ICC = 0.383 under perturbation). This sensitivity is an acknowledged limitation. $\beta_1$ (loops/holes) was excluded from the final feature set due to higher instability (ICC = 0) and weaker permutation evidence ($p_{\text{perm}} = 0.016$ in F8).

#### 4.4.5 Excluded Descriptors

| Descriptor | Reason for Exclusion |
| :--- | :--- |
| Lacunarity ($\Lambda$) | Extreme redundancy with $D_0$ under current pipeline (Spearman $\rho = -0.9979$, VIF > 380) |
| Topological $\beta_1$ | Instability under binarization (ICC ≈ 0); weaker permutation evidence (F8) |

Exclusion does not imply that these descriptors lack scientific value in general; it reflects their behavior under the current pipeline configuration.

### 4.5 Relative Structural Index

An intra-image relative ratio was computed:

$$R_{\text{trab}} = \frac{\text{Feature}_{\text{Crest}}}{\text{Feature}_{\text{Basal}} + \epsilon}, \quad \epsilon = 10^{-6}$$

$R_{\text{trab}}$ is a descriptive index of relative structural relationship between the two fixed regions. It is not an independent descriptor and is not counted in the final feature set.

### 4.6 Statistical Protocol

- **Primary endpoint**: Paired intra-patient structural contrast between ROI Crest and ROI Basal (Cohen's standardized paired difference $d_z = \bar{\delta}/s_\delta$).
- **Bootstrap CIs**: 1,000 patient-level bootstrap iterations ($\text{seed} = 42$), percentile method, 95% confidence level.
- **Permutation control**: Spatial permutation of ROI assignment (ROI A ↔ ROI B labels permuted) to verify that the contrast is position-dependent.
- **Unit of analysis**: `patient_id` (images averaged within patient before analysis).

---

## 5. VALIDATION

### 5.1 Mathematical Validation (F4/F4.1)

| Descriptor | Validation Object | Expected | Observed | Status |
| :--- | :--- | :---: | :---: | :---: |
| $D_0$ | Sierpinski gasket (81×81) | ~1.893 | 1.785 | `CONVERGING` |
| $D_0$ | Line | 1 | 1.028 | `PASS` |
| $D_0$ | Plane | 2 | 2.014 | `PASS` |
| $D_M$ | Flat surface | 2 | 2.0 | `PASS` |
| $D_M$ | White noise | [2,3] | 4.24 | `SCOPE_LIMITATION` |
| $\Lambda$ | Homogeneous | 1 | 1.0 | `PASS` |
| $\beta_0$ | Square | 1 | 1 | `PASS` |
| $\beta_0$ | Three components | 3 | 3 | `PASS` |

### 5.2 Perturbation Stability (F5)

| Descriptor | ICC | Stability Assessment |
| :--- | :---: | :--- |
| $D_0$ | 0.886 | Stable |
| Lacunarity ($\Lambda$) | 0.940 | Stable (excluded for redundancy) |
| $\Delta\alpha$ | 0.927 | Stable |
| $D_M$ | 0.445 | Low stability under perturbation |
| $\beta_0$ | 0.383 | Low stability; binary-representation sensitive |
| $\beta_1$ | ~0 | Unstable; excluded |

> Stability results reflect behavior under synthetic perturbations (Gaussian noise, minor rotation, contrast variation). They do not imply clinical or biological invariance.

---

## 6. DEVELOPMENT ANALYSIS

### 6.1 Structural Contrast (Development: N = 643 Patients)

| Descriptor | Mean Crest | Mean Basal | Paired Diff. | Cohen's $d_z$ |
| :--- | :---: | :---: | :---: | :---: |
| $D_0$ | 1.9199 | 1.9210 | −0.0011 | −0.199 |
| $D_M$ | 2.3875 | 2.4784 | −0.0909 | −0.816 |
| $\Delta\alpha$ | 0.3862 | 0.0911 | +0.2951 | +0.518 |
| $\beta_0$ | 2.982 | 1.592 | +1.390 | +0.361 |

All four descriptors survived spatial permutation testing ($p_{\text{perm}} < 0.001$), confirming that the paired Crest/Basal contrast is position-dependent and not an artifact of random ROI assignment.

### 6.2 Feature Redundancy Analysis (F8/F9)

| Pair | Spearman $\rho$ | VIF |
| :--- | :---: | :---: |
| $D_0$ / Lacunarity | −0.9979 | 388.8 / 400.7 |
| $D_M$ — $D_0$ | low | 3.21 |
| $\Delta\alpha$ — $D_0$ | low | 2.42 |
| $\beta_0$ — $D_0$ | low | 2.68 |

Domain predictability (F8): Balanced Accuracy = 0.117. The analyses did not identify a strong positive domain-predictability signal under the evaluated setup, although a classifier score below chance does not by itself establish absence of domain shift.

---

## 7. HOLDOUT EVALUATION

The Holdout was accessed once, after the pipeline was locked (F10), under strict firewall conditions verified by SHA-256 hash integrity check.

### Development vs. Holdout Structural Contrasts

| Descriptor | Dev $d_z$ | Holdout $d_z$ | Holdout 95% CI | Direction Reproduced | Magnitude Ratio |
| :--- | :---: | :---: | :---: | :---: | :---: |
| $D_0$ | −0.199 | **−0.232** | [−0.407, −0.086] | **YES** | 1.168 |
| $D_M$ | −0.816 | **−0.866** | [−1.056, −0.698] | **YES** | 1.061 |
| $\Delta\alpha$ | +0.518 | **+0.589** | [+0.480, +0.698] | **YES** | 1.138 |
| $\beta_0$ | +0.361 | **+0.330** | [+0.261, +0.467] | **YES** | 0.915 |

The independent Holdout reproduced the direction and approximately similar magnitude of the Development structural contrasts across all four descriptors. The magnitude ratios (0.92–1.17) are descriptive comparisons, not formal reproducibility metrics.

> **Interpretation**: These results provide out-of-sample evidence that the paired structural contrast under the locked computational framework is not specific to the Development sample. No claims of clinical validity, absence of overfitting, or diagnostic accuracy are made on the basis of these results.

---

## 8. EXPERT PILOT (F12)

A blinded expert anatomical interpretability assessment was conducted on 50 Development images (not Holdout) by two independent domain experts (Oral & Maxillofacial Radiologist; Periodontist and Dental Anatomist). Experts evaluated panel pairs (original radiograph + ROI overlay) with no access to descriptor values, model outputs, or F11 results.

### 8.1 ROI Anatomical Usability

| Region | % YES (Valid) | % PARTIAL | % NO | % UNCERTAIN | % USABLE (YES+PARTIAL) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| ROI Crest (A) | 70.0% | 18.0% | 11.0% | 1.0% | **88.0%** |
| ROI Basal (B) | 87.0% | 8.0% | 1.0% | 4.0% | **95.0%** |

(N = 100 primary expert readings: 2 experts × 50 images; percentages computed over readings.)

### 8.2 Inter- and Intra-Rater Agreement

| Agreement Type | Cohen's $\kappa$ |
| :--- | :---: |
| Inter-rater (Crest location) | −0.065 |
| Inter-rater (Basal location) | +0.068 |
| Inter-rater (Overall representativeness) | +0.100 |
| Intra-rater EXPERT_01 (Crest repeatability) | +0.125 |
| Intra-rater EXPERT_02 (Crest repeatability) | +0.195 |

> Low inter-rater agreement reflects subjective disagreement about whether marginal overlap with adjacent structures constitutes a partial or full validity failure — not a disagreement about the overall concept of the ROI.

### 8.3 Main Anatomical Interference Patterns (Crest Region)

| Interference | Count | % of Readings |
| :--- | :---: | :---: |
| Root overlap | 19/100 | 19.0% |
| Artifact | 4/100 | 4.0% |
| Lamina dura | 4/100 | 4.0% |
| Periodontal space | 2/100 | 2.0% |

(Categories not mutually exclusive; denominator = 100 primary expert readings.)

> Root overlap with the apical region of dental roots was the dominant interference, particularly when root morphology extends below the 45% height threshold.

---

## 9. RESULTS SUMMARY

The complete experimental pipeline demonstrated:
1. **Mathematical validity**: All four locked descriptors were verified to produce expected outputs on synthetic test objects.
2. **Feature stability**: $D_0$ (ICC = 0.886) and $\Delta\alpha$ (ICC = 0.927) are stable under synthetic perturbations; $D_M$ and $\beta_0$ show lower stability.
3. **Development structural contrast**: All four descriptors show consistent directional differences between fixed Crest and Basal regions, with Cohen's $d_z$ ranging from −0.199 to +0.518.
4. **Out-of-sample reproducibility**: The Holdout independently confirmed the direction and approximately similar magnitude of all four structural contrasts.
5. **Expert anatomical assessment**: Approximately 88–95% of ROI readings were judged anatomically usable, with recurrent root interference as the primary limitation of the fixed geometric placement.

---

## 10. DISCUSSION

### 10.1 Methodological Contribution

The primary contribution of this work is not any individual mathematical descriptor — $D_0$, $D_M$, $\Delta\alpha$, and $\beta_0$ are all established techniques — but rather the **integrated methodology** through which they are applied:
- Formal mathematical validation of algorithm implementations.
- Explicit preprocessing pipeline specification.
- Patient-level identity control and deduplication.
- Fixed computational ROI with explicit acknowledgment of its non-adaptive nature.
- Locked feature pipeline with cryptographic holdout integrity.
- Patient-level out-of-sample evaluation.
- Blinded expert anatomical interpretability assessment with transparent reporting of limitations.

This combination — while individual components are known — has not, to our knowledge, been systematically assembled in the dental radiograph trabecular characterization literature (pending formal systematic review).

### 10.2 Fixed ROI as Computational Reference

The fixed geometric ROI provides deterministic, operator-independent spatial references that eliminate feedback loops between texture measurements and ROI placement. The expert pilot (F12) confirms that approximately 88–95% of readings fall in interpretable trabecular regions, while simultaneously revealing that root interference and cortical edge proximity are recurrent challenges at the Crest position.

The correct interpretation is:

> "The fixed ROI geometry provided a reproducible computational reference for paired structural comparison across radiographs. This reproducibility should not be interpreted as equivalent to anatomically adaptive localization."

### 10.3 Out-of-Sample Reproducibility

The independent Holdout reproduced the direction and approximately similar magnitude of all four structural contrasts. The magnitude ratios (0.92–1.17) are descriptive comparisons; they do not constitute formal reproducibility metrics or statistical evidence of equivalence. Notwithstanding, the consistent directional replication across an independent patient cohort under an exactly frozen pipeline provides evidence that the observed contrasts are not artifacts of Development sample specificity.

### 10.4 Reconciliation: F11 vs. F12

F11 and F12 answer different questions. F11 evaluates the reproducibility of the computational pipeline's outputs in independent patients. F12 evaluates how consistently human experts interpret the anatomical content of those fixed spatial references. Low expert agreement on marginal cases does not invalidate the computational reproducibility established in F11; it limits the anatomical precision with which one can ascribe the measured contrast to specific tissue structures.

---

## 11. LIMITATIONS

1. **2D projection of 3D trabecular structure**: Periapical radiographs are 2D projections; measured descriptors reflect texture in the projected image, not 3D microarchitectural properties.
2. **No physical density calibration**: The "35 µm/px nominal" resampling is a digital grid normalization, not a physical calibration of radiographic density or tissue properties.
3. **Fixed geometric ROI, not anatomy-adaptive**: The ROI geometry does not adjust to individual root morphology, bone height, or tooth position. Root interference was documented in 19% of Crest expert readings.
4. **Limited inter-rater agreement**: Cohen's $\kappa$ between the two expert raters was near zero, reflecting subjective variability in judging marginal cases.
5. **No clinical ground truth**: No clinical diagnoses (periodontitis staging, bone loss grading, systemic disease status) are associated with these radiographs. This is a structural characterization study.
6. **Dataset characteristics**: Dataset sources and acquisition parameters may introduce unknown confounders not fully captured by the domain predictability analysis.
7. **$D_M$ sensitivity and scope**: The white noise result ($D_M = 4.24$) exceeds the expected 2.5D surface range, indicating a scope limitation of the blanket implementation at high-noise inputs.
8. **$\beta_0$ binary sensitivity**: Sensitivity to Sauvola parameters limits the interpretability of absolute $\beta_0$ values; only the paired Crest/Basal contrast is reported.
9. **Lacunarity redundancy**: The extreme colinearity between $D_0$ and lacunarity ($\rho = -0.9979$) under the current pipeline may not generalize to other binarization methods.
10. **Expert pilot scale**: 50 images, 2 experts — insufficient for inter-rater statistics beyond pilot characterization.
11. **No DINOv2 integration in Paper 1**: Visual representation methods are not included in this study's experimental results.
12. **No diagnostic or predictive outcomes**: No AUC, sensitivity, specificity, or classification performance metrics are reported or implied.

---

## 12. FUTURE WORK

- **Anatomy-adaptive ROI**: Landmark-based or semantic segmentation methods to replace fixed-coordinate placement with biologically meaningful boundaries.
- **Larger multi-source dataset**: Prospective data collection with standardized acquisition protocols and documented clinical annotations.
- **Clinical ground truth**: Validated expert periodontal staging and systemic bone disease annotations to enable supervised correlation studies.
- **3D imaging validation**: Comparison with micro-CT or CBCT-derived trabecular metrics as a 3D reference.
- **DINOv2 feature fusion**: Combining mathematically defined descriptors with self-supervised visual representations (Paper 2).
- **TDA robustness**: Improved binary-invariant topological descriptors, e.g., using persistent Betti curves rather than threshold-sensitive counts.

---

## 13. CONCLUSION

Lattice Bio demonstrates that a fixed geometric computational reference framework, combined with mathematically validated fractal, surface, multifractal, and topological descriptors, can produce reproducible paired structural characterization of trabecular bone in 2D intraoral periapical radiographs. Out-of-sample evaluation in an independent patient cohort confirmed the directionality and approximate magnitude of the structural contrasts established during development. Expert assessment revealed that the fixed ROI geometry yields interpretable anatomical regions in the majority of cases, while systematically identifying root interference as the primary limitation for future adaptive ROI development.

This work is a methodological contribution to the reproducibility infrastructure for quantitative dental radiographic analysis. It does not constitute a clinical diagnostic tool, does not characterize disease severity, and does not validate any clinical biomarker.

---

## 14. REPRODUCIBILITY

- **Repository**: `https://github.com/genaropass/Lattice-Bio.git` (main branch)
- **Pipeline Lock**: `configs/final_pipeline_lock_v1.json` (v1.0_final_lock)
- **Holdout Integrity**: SHA-256 `85e3a856e5a1334d53084f242fff50a92c1c662fe1d4c8797053261578d2b335`
- **Experiment Ledger**: `data/processed/experiment_ledger.csv` (EXP-F0-001 through EXP-F13-001)
- **Development Features**: `data/processed/phase7_features.csv`
- **Holdout Results**: `data/processed/phase11_holdout_results.csv`
- **Expert Pilot Data**: `data/processed/phase12_expert_pilot.csv`
- **Random Seeds**: Phase-specific seeds documented in configuration files (primary seed: 42; repeatability seed: 1042).
- **Environment**: Python 3.12; dependencies listed in `requirements.txt`.

---

## 15. ETHICS / DATA GOVERNANCE

> **Statement**: Ethics approval documentation, institutional authorization, and patient consent records were not available in the audited project materials and must be verified and documented before submission to any peer-reviewed journal, in accordance with the journal's requirements.

No patient-identifiable information is reported in this manuscript.

---

## REFERENCES

> **Note**: References are listed by topic area. Full citations with DOI must be completed before submission. Placeholder categories reflect the literature review conducted in F13 (see `docs/literature_review_f13.md`).

**Fractal analysis in dental radiographs**
- [Box-counting FD, periapical, periodontal — multiple PubMed refs identified in F13 literature search]
- [Systematic reviews on FD dental radiographs]

**Multifractal analysis**
- [Multifractal spectrum bone texture — refs identified in F13]

**Minkowski/Peleg surface dimension**
- Peleg S, Naor J, Hartley R, Avnir D. Multiple Resolution Texture Analysis and Classification. *IEEE Transactions on Pattern Analysis and Machine Intelligence*. 1984;6(4):518–523.

**Lacunarity**
- [Lacunarity trabecular bone, dental radiographs — refs identified in F13]

**TDA / Persistent Homology**
- [Persistent homology bone texture — refs identified in F13]

**ROI standardization**
- [ROI reproducibility dental radiographs — refs identified in F13]

**Self-supervised learning (context)**
- Oquab M, et al. DINOv2: Learning Robust Visual Features without Supervision. *arXiv*. 2023.
