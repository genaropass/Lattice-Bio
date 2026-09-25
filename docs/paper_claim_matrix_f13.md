# PAPER CLAIM MATRIX — F13 — LATTICE BIO

> Every major claim in the manuscript must trace to audited experimental evidence.

| # | Manuscript Claim | Phase Evidence | Artifact Reference | Allowed Wording | Forbidden Wording |
| :---: | :--- | :--- | :--- | :--- | :--- |
| 1 | Dataset: 850 included images from 805 patients | F1, F1.5 | `final_dataset_manifest.csv` | "850 included intraoral periapical radiographs from 805 unique patients" | "850 validated clinical images", "clinically confirmed" |
| 2 | Zero patient overlap between Development and Holdout | F1 | `holdout_test_split.json`, `patient_mapping.csv` | "Zero patients are shared between Development and Holdout" | "perfectly separated", "guaranteed unbiased" |
| 3 | Holdout integrity verified by SHA-256 | F10, F11 | `configs/final_pipeline_lock_v1.json`, `audit_phase11_holdout.py` | "The Holdout split was sealed with SHA-256 hash `85e3a856...`" | "cryptographic proof of unbiasedness" |
| 4 | $D_0$ validated: plane→2, line→1, Sierpinski convergent | F4/F4.1 | `docs/math_validation_phase4_1.md` | "Mathematical validation confirmed expected asymptotic behavior under synthetic test objects" | "perfect mathematical validation", "fully validated" |
| 5 | $D_M$ validated: flat→2; scope limitation at white noise | F4/F4.1 | `docs/math_validation_phase4_1.md` | "A scope limitation was identified: white noise yields $D_M = 4.24$, exceeding the expected $[2,3]$ range" | "D_M is fully validated", "fully correct" |
| 6 | $D_0$ stable under perturbations (ICC = 0.886) | F5 | `phase5_stability_results.csv` | "ICC = 0.886 under synthetic perturbations" | "stable under clinical conditions", "clinically stable" |
| 7 | $\Delta\alpha$ stable (ICC = 0.927) | F5 | `phase5_stability_results.csv` | "ICC = 0.927 under synthetic perturbations" | "clinically stable" |
| 8 | $D_M$ shows lower stability (ICC = 0.445) | F5 | `phase5_stability_results.csv` | "ICC = 0.445; lower perturbation stability than $D_0$" | "unstable descriptor", "should be excluded" |
| 9 | Lacunarity excluded: $\rho = -0.9979$, VIF > 380 | F8, F9 | `phase8_correlation_matrix.csv`, `phase9_feature_redundancy.csv` | "Lacunarity was excluded due to extreme redundancy with $D_0$ under the current pipeline (Spearman $\rho = -0.9979$, VIF > 380)" | "lacunarity is useless", "lacunarity is clinically invalid" |
| 10 | $\beta_1$ excluded: unstable + weaker permutation | F5, F8 | `phase5_stability_results.csv`, `phase8_permutation_results.csv` | "$\beta_1$ was excluded due to instability under binarization and weaker permutation evidence ($p_{\text{perm}} = 0.016$)" | "$\beta_1$ has no scientific value" |
| 11 | All 4 descriptors survive spatial permutation ($p < 0.001$) | F8 | `phase8_permutation_results.csv` | "All four locked descriptors showed statistically significant position-dependence under spatial permutation ($p < 0.001$)" | "proves no domain shortcut", "proves biological validity" |
| 12 | Development: $D_0$ $d_z = -0.199$ (Crest vs Basal) | F7, F10 | `phase7_features.csv`, `final_pipeline_lock_v1.json` | "Development paired Cohen's $d_z$: $D_0 = -0.199$" | "clinical effect size", "diagnostic effect size" |
| 13 | Development: $D_M$ $d_z = -0.816$ | F7, F10 | `phase7_features.csv` | "Development paired Cohen's $d_z$: $D_M = -0.816$" | (same) |
| 14 | Development: $\Delta\alpha$ $d_z = +0.518$ | F7, F10 | `phase7_features.csv` | "Development paired Cohen's $d_z$: $\Delta\alpha = +0.518$" | (same) |
| 15 | Development: $\beta_0$ $d_z = +0.361$ | F7, F10 | `phase7_features.csv` | "Development paired Cohen's $d_z$: $\beta_0 = +0.361$" | (same) |
| 16 | Holdout: all 4 descriptors reproduced in direction | F11 | `phase11_holdout_summary.csv` | "The independent Holdout reproduced the direction and approximately similar magnitude of Development structural contrasts" | "100% reproducible", "fully reproducible", "no overfitting" |
| 17 | Holdout $D_0$ CI: $[-0.407, -0.086]$ | F11 | `phase11_holdout_summary.csv` | "Holdout 95% bootstrap CI for $d_z$: $[-0.407, -0.086]$" | (do not omit the CI) |
| 18 | Holdout $D_M$ CI: $[-1.056, -0.698]$ | F11 | `phase11_holdout_summary.csv` | same | — |
| 19 | Holdout $\Delta\alpha$ CI: $[+0.480, +0.698]$ | F11 | `phase11_holdout_summary.csv` | same | — |
| 20 | Holdout $\beta_0$ CI: $[+0.261, +0.467]$ | F11 | `phase11_holdout_summary.csv` | same | — |
| 21 | Magnitude ratios 0.915–1.168 | F11 | `phase11_holdout_summary.csv` | "Descriptive magnitude ratios: 0.915 ($\beta_0$) to 1.168 ($D_0$) — reported as descriptive comparisons, not formal reproducibility metrics" | "reproducibility metrics", "generalizability score" |
| 22 | Expert pilot: 88% Crest usable, 95% Basal usable | F12 | `phase12_expert_summary.csv` | "88% of expert readings judged Crest ROI usable; 95% judged Basal ROI usable (N = 100 primary readings)" | "anatomically validated", "expert validated ROI" |
| 23 | Inter-rater $\kappa$ range $-0.06$ to $+0.10$ | F12 | `phase12_expert_summary.csv` | "Inter-rater Cohen's $\kappa$: $-0.065$ (Crest location) to $+0.100$ (overall representativeness)" | "good agreement", "acceptable agreement" |
| 24 | Root interference 19/100 Crest readings | F12 | `phase12_expert_pilot.csv` (verified) | "Root overlap identified in 19 of 100 Crest expert readings (19%; categories not mutually exclusive)" | "19% of images failed", "38% root interference" |
| 25 | Cortical boundary 7/100 Basal readings | F12 | `phase12_expert_pilot.csv` (verified) | "Cortical boundary interference in 7 of 100 Basal expert readings (7%)" | "14% of images affected" |
| 26 | Fixed ROI as computational reference, not landmark | F6, F6.1, F12.1.1 | `scientific_review_f12_1.md` | "The fixed ROI geometry provided a reproducible computational reference for paired structural comparison. This should not be interpreted as equivalent to anatomically adaptive localization." | "anatomically validated", "landmark-validated" |
| 27 | No clinical ground truth | F2, F3 | `docs/ground_truth_v1.md`, `docs/research_question_v1.md` | "No clinical diagnoses, disease classifications, or clinical ground truth are available in this dataset" | "clinical ground truth", "disease-labeled dataset" |
| 28 | Domain predictability BA = 0.117 | F8 | `phase8_domain_analysis.csv` | "Balanced Accuracy of domain classifier: 0.117 — did not identify a strong positive domain-predictability signal; below-chance performance does not by itself establish absence of domain shift" | "proves no domain shift", "domain-free" |

---

## Claim Summary: Forbidden Terms Found in Any Claim?

Scan result (manual): All 28 claims verified against the forbidden term list. No violations found in this matrix.

Forbidden terms explicitly banned (checked):
- ❌ `validated ROI` — not used (replaced by "computational reference")
- ❌ `anatomically validated` — not used
- ❌ `100% reproducible` / `fully reproducible` — not used
- ❌ `mathematical robustness` as F11 synonym — not used
- ❌ `absence of overfitting` / `no overfitting` — not used
- ❌ `ground truth` (unqualified) — always qualified as "clinical ground truth" with negation
- ❌ `biomarker` — not used
- ❌ `bone density` — not used
- ❌ `3D microarchitecture` — not used
- ❌ `diagnostic accuracy` — not used
