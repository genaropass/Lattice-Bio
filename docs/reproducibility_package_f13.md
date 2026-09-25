# REPRODUCIBILITY PACKAGE — F13 — LATTICE BIO

> **Version**: v1.0 — F13 (2026-09-25)
> **Status**: DRAFT — Pre-submission
> **Pipeline Lock**: `v1.0_final_lock` (F10)
> **Holdout SHA-256**: `85e3a856e5a1334d53084f242fff50a92c1c662fe1d4c8797053261578d2b335`

---

## 1. Repository Structure

```
Lattice-Bio/
├── configs/
│   ├── final_pipeline_lock_v1.json       ← Pipeline lock specification (F10)
│   ├── phase7_clean_benchmark.json       ← Phase 7 config
│   ├── phase11_holdout_evaluation.json   ← Phase 11 config
│   ├── phase12_expert_pilot.json         ← Phase 12 config
├── data/
│   └── processed/
│       ├── final_dataset_manifest.csv    ← All 2598 images, inclusion status, split
│       ├── holdout_test_split.json       ← Sealed Holdout split (SHA-256 locked)
│       ├── experiment_ledger.csv         ← Full experiment registry (EXP-F0-001 → EXP-F13-001)
│       ├── patient_mapping.csv           ← Patient identity deduplication mapping
│       ├── phase7_features.csv           ← Development features (657 images × 22 columns)
│       ├── phase8_*.csv                  ← Domain/robustness analysis outputs
│       ├── phase9_*.csv                  ← Feature ablation outputs
│       ├── phase11_holdout_results.csv   ← Holdout raw features (193 images)
│       ├── phase11_holdout_summary.csv   ← Holdout summary statistics
│       ├── phase12_expert_pilot.csv      ← Expert pilot evaluations (200 rows)
│       ├── phase12_expert_summary.csv    ← Expert pilot summary metrics
│       └── phase12_pilot_manifest.csv    ← Blinded pilot image manifest
├── docs/
│   ├── scientific_review_f12_1.md        ← F12.1/F12.1.1 claim audit
│   ├── literature_review_f13.md          ← F13 literature review
│   ├── reproducibility_package_f13.md    ← This document
│   ├── experiment_execution_map_f13.md   ← Phase → artifact mapping
│   ├── paper_claim_matrix_f13.md         ← Claims → evidence matrix
│   └── f13_readiness.md                 ← Submission readiness checklist
├── paper/
│   └── manuscript_v1.md                 ← Paper 1 manuscript draft
├── scripts/
│   ├── audit_final_pipeline_lock.py
│   ├── run_phase7_clean_benchmark.py
│   ├── run_phase8_domain_robustness.py
│   ├── run_phase9_feature_ablation.py
│   ├── run_final_pipeline_lock.py
│   ├── run_phase11_holdout.py
│   ├── audit_phase11_holdout.py
│   ├── prepare_phase12_expert_pilot.py
│   ├── run_phase12_expert_pilot.py
│   └── audit_phase12_expert_pilot.py
└── src/
    ├── fractal/
    │   ├── box_counting.py
    │   ├── minkowski.py
    │   ├── lacunarity.py
    │   ├── multifractal.py
    │   ├── tda_features.py
    │   └── feature_extractor.py
    └── preprocessing/
        ├── roi_segmentation.py
        └── contrast_normalization.py
```

---

## 2. Configuration Files

| File | Purpose | Locked |
| :--- | :--- | :---: |
| `configs/final_pipeline_lock_v1.json` | Defines SET_G_LOCKED, ROI coords, preprocessing params, statistical protocol | **YES** |
| `configs/phase11_holdout_evaluation.json` | Holdout evaluation protocol | **YES** |
| `configs/phase12_expert_pilot.json` | Expert pilot protocol | **YES** |

**Pipeline Lock Hash**: The file `configs/final_pipeline_lock_v1.json` specifies version `v1.0_final_lock`. Any modification of this file would constitute a protocol violation.

---

## 3. How to Trace Each Phase

| Phase | Execution Script | Key Output | Report |
| :--- | :--- | :--- | :--- |
| F7 | `scripts/run_phase7_clean_benchmark.py` | `phase7_features.csv` | `docs/clean_benchmark_phase7.md` |
| F8 | `scripts/run_phase8_domain_robustness.py` | `phase8_*.csv` | `docs/domain_robustness_phase8.md` |
| F9 | `scripts/run_phase9_feature_ablation.py` | `phase9_*.csv` | `docs/feature_ablation_phase9.md` |
| F10 | `scripts/run_final_pipeline_lock.py` | Lock config + Development summary | `docs/final_pipeline_lock_f10.md` |
| F11 | `scripts/run_phase11_holdout.py` | `phase11_holdout_results.csv` | `docs/phase11_holdout_evaluation.md` |
| F12 | `scripts/run_phase12_expert_pilot.py` | `phase12_expert_pilot.csv` | `docs/phase12_expert_pilot.md` |

---

## 4. Frozen Holdout Protocol

The Holdout was sealed before any Holdout image was processed:

1. The split file `data/processed/holdout_test_split.json` was created during F1/F7 dataset construction.
2. Its SHA-256 hash (`85e3a856e5a1334d53084f42fff50a92c1c662fe1d4c8797053261578d2b335`) was recorded in `configs/final_pipeline_lock_v1.json` before F11.
3. Every F11 script verifies this hash before accessing any Holdout image.
4. F11 was executed once; results were not modified post-hoc.
5. No Holdout images were included in the expert pilot (F12).

**To verify Holdout integrity**:
```python
import hashlib
with open('data/processed/holdout_test_split.json', 'rb') as f:
    h = hashlib.sha256(f.read()).hexdigest()
assert h == '85e3a856e5a1334d53084f242fff50a92c1c662fe1d4c8797053261578d2b335'
```

---

## 5. Experiment Ledger

All experiments are registered in `data/processed/experiment_ledger.csv`. Each row contains:
- `exp_id`: Unique experiment identifier (EXP-F0-001 through EXP-F13-001)
- `date`: Execution date
- `dataset`: Dataset scope
- `preprocessing`: Pipeline version
- `feature_set`: Features used
- `model`: Analysis type
- `split`: Data split used
- `target`: Endpoint
- `status`: `VALID` or `INVALID`
- `reason`: Textual justification

---

## 6. Random Seeds

| Component | Seed | Purpose |
| :--- | :---: | :--- |
| Bootstrap CIs (F7, F11) | 42 | Patient-level paired bootstrap |
| Expert pilot sample | 42 | Stratified image sampling |
| Repeatability subset | 1042 | Repeatability image selection |
| Permutation tests (F8) | 42 | Spatial permutation |

---

## 7. What Cannot Be Rerun Without Reopening the Protocol

The following are **sealed** and must not be re-executed without explicitly reopening and documenting the protocol deviation:

1. **F11 (Holdout Evaluation)**: The one-time Holdout rule means re-running F11 with any modifications would violate the sealed evaluation protocol.
2. **F10 (Pipeline Lock)**: The pipeline lock must not be modified. Any changes require a new version number and justification.
3. **Holdout Split**: The `holdout_test_split.json` file must not be regenerated.

---

## 8. Environment / Dependencies

- **Python**: 3.12
- **Key packages**: `numpy`, `pandas`, `scipy`, `scikit-learn`, `opencv-python`, `matplotlib`, `scikit-image` (Sauvola), `gudhi` or equivalent (TDA)
- **Platform**: Windows 10/11 (tested); UTF-8/cp1252 compatibility maintained in all scripts.

> **Note**: A `requirements.txt` or `environment.yml` must be added to the repository before submission.

---

## 9. Data Availability

Raw radiograph images are not publicly available due to privacy considerations. The processed feature CSV files (`phase7_features.csv`, `phase11_holdout_results.csv`, `phase12_expert_pilot.csv`) and all configuration files are available in the repository. The dataset manifest provides image counts and split assignments without identifying information.

> **Ethics documentation required**: See Section 15 of the manuscript.
