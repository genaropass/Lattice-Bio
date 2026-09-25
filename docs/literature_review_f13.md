# LITERATURE REVIEW — F13 — LATTICE BIO

## Bibliographic Question

This literature review supports the manuscript for **Lattice Bio (Paper 1)**: a methodological study of paired structural characterization of trabecular bone patterns in intraoral periapical radiographs using a fixed-reference computational ROI framework and mathematically validated descriptors.

The literature review was conducted to:
1. Establish the current state of fractal and multi-scale texture analysis in dental radiographs.
2. Position the Minkowski/Peleg surface dimension ($D_M$) and multifractal spectrum width ($\Delta\alpha$) within the field.
3. Identify the known limitations of ROI standardization and reproducibility in radiographic trabecular analysis.
4. Clarify the scope of TDA (persistent homology) applications in bone texture.
5. Confirm that Paper 1 is a methodological contribution and NOT a clinical diagnostic study.

---

## Search Strategy

**Databases consulted**: PubMed/MEDLINE, Google Scholar, arXiv, MDPI Open Access, ResearchGate.

**Key search terms used**:
- `fractal dimension box-counting trabecular bone dental radiograph periapical`
- `multifractal analysis trabecular bone texture radiograph dental`
- `persistent homology TDA bone texture medical imaging`
- `lacunarity trabecular bone osteoporosis dental radiograph reproducibility`
- `Minkowski sausage Peleg fractal surface dimension grayscale 2.5D`
- `ROI standardization reproducibility intraoral radiograph trabecular bone`
- `fixed ROI dental radiograph fractal dimension inter-rater`

> **Note**: The literature review identifies established findings and methodological gaps. No claims about the novelty of individual descriptors are made without bibliographic support.

---

## 2.1 — Fractal Analysis in Dental Radiography / Trabecular Bone

### What Is Established

Fractal dimension (FD) analysis via the **box-counting method** is a widely applied quantitative tool for evaluating trabecular bone complexity in dental radiographs. The method measures the self-similar complexity of bone texture patterns across multiple scales by counting how many square boxes of decreasing size are needed to cover the binary image representation of trabecular structure.

Key established findings from the literature:
- **Periapical radiographs are preferred** over panoramic images for local trabecular analysis due to higher spatial resolution and lower radiation dose (Southard *et al.*, refs in PubMed).
- FD can differentiate healthy bone from **moderate-to-severe periodontitis**, but has limited sensitivity for **early/mild periodontitis** stages.
- FD has been applied to monitor bone healing after endodontic treatment, peri-implant remodeling, and changes during orthodontic procedures.
- As a potential osteoporosis screening tool via dental radiographs, systematic reviews indicate **inconsistent evidence** — FD is not considered a reliable standalone diagnostic marker for this condition.

### Methodological Heterogeneity

A major recognized limitation in the field is the **lack of standardization** regarding:
- ROI selection method (manual, semi-automatic, landmark-based);
- ROI size (variable across studies);
- Image binarization method;
- Preprocessing pipeline.

This heterogeneity directly motivates the methodological contribution of Lattice Bio (explicit pipeline specification, locked preprocessing, reproducibility audit).

### Relevance to Lattice Bio
Lattice Bio uses box-counting $D_0$ (Hausdorff-Besicovitch dimension) under a binary pipeline (CLAHE + Sauvola). Unlike studies that treat ROI placement as an informal step, Lattice Bio explicitly frames its ROI geometry as a **fixed computational reference**, acknowledges its anatomical limitations, and performs permutation controls and out-of-sample evaluation.

---

## 2.2 — Multifractal Analysis

### What Is Established

Multifractal analysis extends single-FD analysis by characterizing the **full distribution** of local scaling exponents (Hölder exponents) via the singularity spectrum $f(\alpha)$. The **spectrum width $\Delta\alpha$** quantifies the degree of heterogeneity or structural irregularity in the image.

In the dental/radiographic context:
- Multifractal approaches have been used to distinguish healthy from osteoporotic bone with higher sensitivity than monofractal FD in some studies.
- Multifractal lacunarity analysis has been proposed for improved characterization of texture variations where visual differences are subtle.
- The application of multifractal analysis to **periapical radiographs** specifically (as opposed to panoramic) is relatively less documented.

### Relevance to Lattice Bio
Lattice Bio computes $\Delta\alpha$ (singularity spectrum width) via a multi-scale method on grayscale ROI patches. The descriptor is explicitly validated mathematically (F4/F4.1) and shown to survive permutation testing under the paired Crest/Basal contrast (F8). Its exclusion from some prior work on periapical radiographs represents a potential methodological gap that Lattice Bio begins to address.

> **Caution**: Novelty of the specific combination cannot be claimed without a systematic review of the multifractal dental periapical literature, which is a task for F13 pre-submission.

---

## 2.3 — Minkowski / Peleg Surface Dimension ($D_M$)

### What Is Established

The **Minkowski sausage / blanket method** (attributed foundationally to Peleg *et al.*, 1984: *"Multiple Resolution Texture Analysis and Classification"*, IEEE Trans.) treats the grayscale image as a 2.5D surface where pixel intensity represents the $z$-coordinate. The method estimates surface area at multiple scales by dilating an upper envelope and eroding a lower envelope, then fits a log-log regression of area versus scale to obtain the surface fractal dimension.

Key characteristics:
- $D_M$ naturally lies in $[2, 3]$ for grayscale surfaces, with $D_M = 2$ for flat surfaces and values near $3$ for maximally rough/noisy surfaces.
- Unlike $D_0$ (box-counting on binary images), $D_M$ does **not require binarization**, making it complementary under different pipeline assumptions.
- $D_M$ has been applied to bone texture characterization, terrain roughness, and tissue microstructure classification.

### Relevance to Lattice Bio
$D_M$ (Pipeline-A: Lanczos4 + MinMax, no binarization) provides a binarization-independent structural measure that is highly stable under the paired Crest/Basal comparison ($d_z = -0.8161$ in Development, $-0.8656$ in Holdout). Its explicit implementation via the blanket method is formally validated in F4.

> **Critical note**: In F4, white noise yielded $D_M = 4.24$ with a high $R^2$, exceeding the expected $[2,3]$ range for 2.5D surfaces. This is a documented behavior of some blanket implementations when the scale range is inappropriate for the signal-to-noise ratio. This finding is explicitly reported as a scope limitation in the mathematical validation section (F4.1) and must be prominently noted in the manuscript.

---

## 2.4 — Lacunarity

### What Is Established

**Lacunarity** quantifies the spatial distribution of gaps ("gappiness") in a binary or grayscale image — specifically, how far the texture is from translationally invariant. Unlike FD, which measures overall complexity, lacunarity measures the **distribution of gap sizes**:
- Low lacunarity: gaps are evenly distributed (more regular texture).
- High lacunarity: gaps are clustered or heterogeneously distributed (more irregular texture).

In trabecular bone, osteoporotic bone shows **increased lacunarity** as the trabecular network becomes more porous and irregular. Studies have used lacunarity as a complement to FD in panoramic and periapical radiographs, and some multifractal-based approaches compute lacunarity directly from the singularity spectrum.

### Relevance to Lattice Bio
In Lattice Bio, lacunarity was included in the exploratory feature set (F7) but **excluded from the final SET_G_LOCKED** in F9/F10 due to extreme mathematical redundancy with $D_0$ under the current binary pipeline (Spearman $\rho = -0.9979$, VIF > 380). This exclusion does **not** imply that lacunarity is clinically useless — it reflects that, under the specific preprocessing pipeline of this study, $D_0$ and lacunarity carry nearly identical information.

---

## 2.5 — Topological Data Analysis (TDA) / Persistent Homology

### What Is Established

**Persistent homology**, the core tool of TDA, captures multi-scale topological structure in data by tracking how connected components (Betti number $\beta_0$) and independent loops (Betti number $\beta_1$) appear and disappear across a filtration of image thresholds. Key established findings:

- TDA has been applied to distinguish bone microstructures in histological and micro-CT data (Oxford, arXiv).
- Topological features have been combined with morphometric descriptors to predict bone biomechanical strength, often outperforming single metrics.
- In 2D radiographic analysis, TDA-based features are less common than in 3D micro-CT or histology, representing an area of relative novelty.
- $\beta_0$ (connected components) reflects the number of distinct trabecular islands in the binarized image; $\beta_1$ (loops/holes) reflects enclosed spaces.

### Relevance to Lattice Bio
Lattice Bio includes $\beta_0$ in SET_G_LOCKED and uses it as a topology-based complement to fractal descriptors. $\beta_1$ was excluded from the final set due to high sensitivity to Sauvola binarization parameters and relatively weak permutation evidence ($p_{perm} = 0.016$ in F8). The use of TDA in paired 2D periapical radiograph analysis represents a relatively underexplored direction in the dental radiography literature.

---

## 2.6 — ROI Methodology

### What Is Established

ROI standardization is widely recognized as one of the most critical factors affecting the reproducibility of trabecular bone measurements. Key issues documented in the literature:

- **Manual ROI placement** introduces observer variability; multiple observers or repeated measurements are recommended.
- **Fixed ROI dimensions** (e.g., 50×50 or 64×64 pixels) are important: varying ROI size directly affects FD values.
- **Anatomical consistency** requires careful avoidance of cortical bone margins, tooth roots, lamina dura, and radiographic artifacts.
- **Automated / landmark-based ROI methods** are being developed but are not yet the standard in most published radiographic fractal analysis studies.
- **Inter-rater reproducibility for ROI selection** is often reported as moderate to good when anatomical anchors are available, but falls when precise boundaries must be drawn near ambiguous structures.

### Specific Gap Relevant to Lattice Bio
Most published fractal dimension studies in dental radiography either (a) place ROIs at specific anatomical landmarks, or (b) use fixed-size ROIs in researcher-defined positions without formal anatomical concordance testing. Lattice Bio addresses this gap by:
1. Using a deterministic, non-landmark-based fixed geometric reference (reproducibility guaranteed by design).
2. Performing a formal blinded expert pilot (F12) to assess anatomical interpretability.
3. Transparently documenting the limitations of fixed-coordinate placement (root interference, cortical edge).

The literature does not report studies that combine locked-pipeline out-of-sample evaluation with a formal expert anatomical interpretability pilot as a distinct validation layer.

---

## 2.7 — Computer Vision / Self-Supervised Learning (Context Only)

Self-supervised visual representation learning (e.g., DINO, DINOv2, MAE) has shown strong performance in natural and medical image understanding. DINOv2 (Oquab *et al.*, 2023, Meta AI) produces dense visual features applicable to downstream tasks without fine-tuning.

> **Position in Paper 1**: DINOv2 is **not included in Paper 1 experimental results**. It is mentioned only as a motivating context for future work (Paper 2), where mathematical descriptors and learned visual representations may be combined for structural characterization.

---

## 3. Summary of Literature Findings

| Topic | Status in Literature | Gap Addressed by Lattice Bio |
| :--- | :--- | :--- |
| Box-counting FD in periapical radiographs | Well-established | Formal mathematical validation + out-of-sample evaluation |
| Multifractal $\Delta\alpha$ in periapical radiographs | Partially explored | Paired contrast with permutation control and locked pipeline |
| Minkowski/Peleg $D_M$ in periapical radiographs | Less common | Binarization-independent complement, mathematical validation |
| Lacunarity | Documented, used as FD complement | Identified as redundant with $D_0$ under current pipeline |
| TDA $\beta_0$ in 2D periapical radiographs | Rare | Explores topological complement to fractal descriptors |
| ROI standardization | Known limitation; no consensus | Fixed computational reference + formal expert pilot + explicit limitations |
| Locked holdout evaluation | Rarely reported in dental radiograph texture studies | Patient-level Holdout with cryptographic firewall |

---

## 4. What Cannot Be Claimed Based on Literature

Based on this review, the following claims should **not** appear in the manuscript without further dedicated literature search:

- "First study to apply TDA to intraoral periapical radiographs" — requires systematic search to confirm.
- "First study to combine fractal + multifractal + TDA" — requires verification.
- "Novel descriptors" — individual descriptors are established; the methodological pipeline combination may be novel in dental radiographs but requires confirmation.

> **Required Action (F13 pre-submission)**: Systematic literature search for multi-descriptor pipelines combining $D_0$, $D_M$, $\Delta\alpha$, and $\beta_0$ on periapical radiographs. This is the remaining gap in the novelty assessment.
