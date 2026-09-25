# EXPERIMENT EXECUTION MAP — F13 — LATTICE BIO

> Maps each Phase (F0–F12.1.1) to its execution artifacts, output files, and documentation.

| Phase | Description | Execution Script(s) | Key Output Files | Documentation | Status |
| :--- | :--- | :--- | :--- | :--- | :---: |
| **F0** | Freeze + Experiment Ledger | N/A (manual) | `experiment_ledger.csv` (init) | — | `CLOSED` |
| **F1** | Patient Identity + Deduplication | `audit_phase0_phase1.py`, `finalize_phase1_manifest.py` | `final_phase1_audit.json`, `patient_mapping.csv`, `final_dataset_manifest.csv` | — | `CLOSED` |
| **F1.5** | Perceptual Deduplication | `run_phase1_5_perceptual_duplicates.py`, `generate_phase1_5_review_gallery.py` | `perceptual_duplicate_candidates.csv`, `perceptual_duplicate_summary.json` | — | `CLOSED` |
| **F2** | Research Question / Scope | N/A (document) | — | `docs/research_question_v1.md` | `CLOSED` |
| **F3** | Ground Truth / Structural Reference | N/A (document) | — | `docs/ground_truth_v1.md` | `CLOSED` |
| **F4 / F4.1** | Mathematical Validation | `audit_phase4_math.py` | — | `docs/math_validation_phase4_1.md` | `CLOSED` |
| **F5** | Computational Feature Stability | `run_phase5_stability_evaluation.py`, `audit_phase5_stability.py` | `phase5_stability_results.csv` | `docs/feature_stability_phase5.md` | `CLOSED` |
| **F6** | ROI / Preprocessing Technical Audit | `generate_phase6_roi_audit.py`, `audit_phase6_roi.py` | `phase6_roi_audit.csv` | `docs/roi_preprocessing_phase6.md` | `CLOSED` |
| **F6.1** | Anatomical / Scientific ROI Validation | `run_phase6_1_visual_audit.py`, `audit_phase6_1_roi.py` | `phase6_1_roi_validation.csv` | `docs/roi_validation_phase6_1.md` | `CLOSED_WITH_LIMITATIONS` |
| **F7** | Clean Development Benchmark | `run_phase7_clean_benchmark.py`, `audit_phase7_clean_benchmark.py` | `phase7_features.csv`, `phase7_figures/` | `docs/clean_benchmark_phase7.md` | `CLOSED` |
| **F8** | Domain / Shortcut / Permutation / Robustness | `run_phase8_domain_robustness.py`, `audit_phase8_domain_robustness.py` | `phase8_*.csv`, `phase8_figures/` | `docs/domain_robustness_phase8.md` | `CLOSED` |
| **F9** | Feature Ablation & Complementarity | `run_phase9_feature_ablation.py`, `audit_phase9_feature_ablation.py` | `phase9_*.csv`, `phase9_figures/` | `docs/feature_ablation_phase9.md` | `CLOSED` |
| **F10** | Final Pipeline & Model Lock | `run_final_pipeline_lock.py`, `audit_final_pipeline_lock.py` | `configs/final_pipeline_lock_v1.json` | `docs/final_pipeline_lock_f10.md` | `LOCKED_WITH_LIMITATIONS` |
| **F11** | One-Time Holdout Evaluation | `run_phase11_holdout.py`, `audit_phase11_holdout.py` | `phase11_holdout_results.csv`, `phase11_holdout_summary.csv`, `phase11_figures/` | `docs/phase11_holdout_evaluation.md` | `CLOSED` |
| **F12** | Expert Pilot & Anatomical Interpretability | `prepare_phase12_expert_pilot.py`, `run_phase12_expert_pilot.py`, `audit_phase12_expert_pilot.py` | `phase12_expert_pilot.csv`, `phase12_expert_summary.csv`, `phase12_expert_panels/` | `docs/phase12_expert_pilot.md` | `CLOSED` |
| **F12.1** | Scientific Review & Computational Reference Audit | N/A (document) | — | `docs/scientific_review_f12_1.md` | `READY_WITH_REQUIRED_CORRECTIONS` |
| **F12.1.1** | Final Scientific Wording Correction | N/A (document) | — | `docs/scientific_review_f12_1.md` (updated) | `CLOSED` |
| **F13** | Manuscript & Reproducibility Package | — | `paper/manuscript_v1.md`, `docs/literature_review_f13.md`, `docs/reproducibility_package_f13.md`, `docs/experiment_execution_map_f13.md`, `docs/paper_claim_matrix_f13.md`, `docs/f13_readiness.md` | (this document) | `IN_PROGRESS` |

---

## Git Commit Reference

| Phase | Commit Hash | Message |
| :--- | :--- | :--- |
| F10 | `ee048a5` | `F10: final pipeline lock` |
| F11 | `27751f3` | `F11: one-time holdout evaluation` |
| F12 | `8bbb914` | `F12: expert pilot anatomical interpretability` |
| F12.1 | `92d060d` | `F12.1: scientific review, claim audit and computational reference documentation` |
| F12.1.1 | `14261be` | `F12.1.1: final scientific wording correction` |
| F13 | TBD | `F13: manuscript and reproducibility package v1` |
