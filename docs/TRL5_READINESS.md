# NeuroPredict-AI — Technology Readiness Level 5 (TRL 5) Dossier
# سند آمادگی فناوری سطح ۵

**Date / تاریخ:** 2026-10-06 · **Scope:** AD/PD multimodal risk-stratification (clinical decision support, not a diagnostic device)

## 1. Honest status / وضعیت صادقانه

TRL 5 = *component/system validated in a **relevant environment*** (NASA/EU scale; for SaMD: validated on realistic, independent clinical-grade data and integrated with representative interfaces).

| Evidence in repo | Status |
|---|---|
| Patient-level split, CV, class-weighted loss, baselines, calibration, subgroup fairness, gated registry, PSI drift monitor (`backend/app/services/training/*`, commit df7875f) | Implemented (TRL 4 evidence) |
| API/auth/RBAC/audit, Docker/K8s, E2E & load tests, pentest scaffolding | Implemented |
| `models/registry.json` | **Empty — no trained, activated model** |
| Training on real, independently-sourced cohorts (ADNI/PPMI/AIBL/OASIS) | **Not done** |
| External (out-of-cohort) validation + prospective/retrospective pivotal-style study | **Not done** |
| IRB / data-use agreements | In progress (`docs/IRB_*`) |

**Conclusion:** the software side meets TRL 4 and the engineering prerequisites for TRL 5. TRL 5 is **not yet claimable**, because it requires the model-validation evidence above. This dossier defines the exact exit criteria and a machine-checkable gate (`backend/scripts/trl5_gate.py`) so the claim can be made only when evidence exists.

## 2. Real-world benchmarks (database search, 2026-10-06)

Used to set realistic exit thresholds. Source: PubMed and ClinicalTrials.gov searches.

**PubMed**
- Song et al., *Front Neurosci* 2022 — AD vs CN, T1 MRI CNN; 5-fold CV AUC 0.987 / acc 0.948, but **external ADNI AUC 0.940 / acc 0.876**; low-res MRI external AUC 0.875. Multi-cohort, multi-vendor design. [doi:10.3389/fnins.2022.851871](https://doi.org/10.3389/fnins.2022.851871)
- Bloch & Friedrich, *Comput Biol Med* 2024 — 3D DL vs classical ML (RF/SVM/XGB…) trained on ADNI, externally validated on AIBL and OASIS; DL ≈ ML performance, different salient regions (SHAP/LIME/GradCAM). Supports our "deep model must beat baseline" rule. [doi:10.1016/j.compbiomed.2024.108029](https://doi.org/10.1016/j.compbiomed.2024.108029)
- Jo et al., *EBioMedicine* 2023 — ADNI serum lipidomics, n=997, AUC 0.808. Realistic biomarker-only ceiling. [doi:10.1016/j.ebiom.2023.104820](https://doi.org/10.1016/j.ebiom.2023.104820)
- Yilmaz et al., *J Comput Assist Tomogr* 2025 — PPMI, rapid PD progression, SVM AUC 0.86 (95% CI 0.78–0.91), 5-fold CV. [doi:10.1097/RCT.0000000000001830](https://doi.org/10.1097/RCT.0000000000001830)
- Powell & Dzamko, *Neurobiol Dis* 2026 — PPMI multimodal, 9-year cognitive impairment, AUC 0.88. [doi:10.1016/j.nbd.2026.107570](https://doi.org/10.1016/j.nbd.2026.107570)
- Biffi et al., *IEEE TMI* 2020 — explainable hippocampal shape model, ADNI. [doi:10.1109/TMI.2020.2964499](https://doi.org/10.1109/TMI.2020.2964499)

**ClinicalTrials.gov** (design precedents)
- [NCT05383053](https://clinicaltrials.gov/study/NCT05383053) — NeuroAI (Neurozen): retrospective pivotal study, n=227 MCI, blinded, randomized-order, MRI+APOE → amyloid-PET positivity; primary endpoints sensitivity/specificity, secondary AUC/accuracy; excludes images used in training. **Template for our relevant-environment validation.**
- [NCT06877182](https://clinicaltrials.gov/study/NCT06877182) — AI-assisted neuroradiology workflow for dementia, n=80,000 (workflow integration precedent).
- [NCT04093908](https://clinicaltrials.gov/study/NCT04093908) — multicenter retrospective ML validation in PD (n=322).
- [NCT07651085](https://clinicaltrials.gov/study/NCT07651085) — AD/PD risk-factor + biomarker AI study (n=65).

Key lesson: internal CV overstates performance (AUC 0.987 → 0.940 externally), so **TRL 5 gates are on external data only.**

## 3. TRL 5 exit criteria / معیارهای خروج

| # | Criterion | Threshold |
|---|---|---|
| C1 | Model trained on real de-identified cohort (ADNI and/or PPMI), patient-level split | registry has an active model; `data_source != synthetic` |
| C2 | External validation on a cohort **not used in training** (e.g. train ADNI → test AIBL/OASIS; PPMI → local site) | n ≥ 200, AUC ≥ 0.85 (AD vs CN) / ≥ 0.80 (PD progression), lower 95% CI ≥ 0.75 |
| C3 | Pivotal-style blinded evaluation (NCT05383053 design) | sensitivity & specificity reported with 95% CI, both ≥ 0.80 |
| C4 | Deep model justified vs baselines | `deep_model_justified() == True` |
| C5 | Calibration | ECE ≤ 0.10 |
| C6 | Subgroup fairness (age, sex) | max AUC gap ≤ 0.05 |
| C7 | Drift reference captured, PSI alert thresholds set | reference file present |
| C8 | System integration in representative environment | docker-compose/K8s stack up; E2E + load tests green in CI |
| C9 | Explainability delivered (SHAP/attention) in API output | present in prediction response |
| C10 | Regulatory/ethics | IRB/DUA status recorded; intended use = decision support |

## 4. Path / مسیر

1. Obtain ADNI/PPMI/AIBL/OASIS data via their data-use applications (no redistribution in repo).
2. `python backend/scripts/train_and_validate.py --data <csv> ...` on the training cohort.
3. Run `evaluate_model.py` on the held-out external cohort; save JSON to `models/validation/external_<cohort>.json` (schema: `auc, auc_ci_low, n, sensitivity, specificity, ece, subgroup_auc_gap, data_source`).
4. Run `python backend/scripts/trl5_gate.py` — prints PASS/FAIL per criterion; exit code 0 only when all machine-checkable criteria pass.
5. Update this dossier with measured values and only then state TRL 5.
