# Data-Use Application Drafts — ADNI, PPMI, AIBL, OASIS
# پیش‌نویس درخواست دسترسی به داده

**Purpose / هدف:** obtain real, independently sourced cohorts for TRL-5 evidence (`docs/TRL5_READINESS.md`, criteria C1–C3).
**Status:** DRAFT. Fields in `[BRACKETS]` must be filled by the applicant. Nothing here has been submitted.

> **یادداشت فارسی:** این متن‌ها پیش‌نویس هستند و فقط توسط خود شما (یا مؤسسه‌تان) قابل ارسال و امضا هستند. هر پورتال فرم و شرایط خودش را دارد و ممکن است تغییر کرده باشد؛ قبل از ارسال، شرایط فعلی هر پورتال را بررسی کنید. اهلیت درخواست‌دهنده (وابستگی سازمانی، کشور، امضای مؤسسه) را هر پورتال جداگانه تعیین می‌کند.

## 0. Before you start / پیش از شروع

| Item | Needed by |
|---|---|
| Named principal investigator with institutional affiliation and institutional email | all |
| Institutional signatory (legal/research office) for the Data Use Agreement | ADNI, PPMI, AIBL, OASIS-3 |
| Ethics/IRB determination (approval **or** exemption letter for secondary use of de-identified data) | usually requested; see `docs/IRB_*` |
| Data-security statement (storage, access control, encryption, no redistribution) | all (Section 2 below) |
| Planned acknowledgement / citation text | all (each portal gives the exact wording) |

Portals (verify current URLs and rules): ADNI via the LONI Image & Data Archive (IDA); PPMI via the PPMI data-access application; AIBL via the AIBL/ADNI-LONI data access route; OASIS-1/2 are openly downloadable, OASIS-3 requires a data use agreement.

## 1. Common project description (paste into every form)

**Project title:** External validation of an explainable multimodal risk-stratification model for Alzheimer's and Parkinson's disease.

**Investigator / institution:** [NAME], [TITLE], [INSTITUTION], [COUNTRY], [INSTITUTIONAL EMAIL].

**Scientific background:** Published deep-learning models for Alzheimer's disease classification from structural MRI reach AUC ≈ 0.99 in internal cross-validation but fall to ≈ 0.94 on external cohorts (Song et al., Front Neurosci 2022, doi:10.3389/fnins.2022.851871). Realistic evaluation therefore needs independent cohorts. Multimodal models in Parkinson's disease have been developed on PPMI (e.g. Yilmaz et al., J Comput Assist Tomogr 2025, doi:10.1097/RCT.0000000000001830), but few are validated across cohorts.

**Aims:**
1. Train a multimodal model (MRI-derived features, clinical/cognitive scores, fluid biomarkers where available) on a development cohort using a patient-level split.
2. Evaluate the frozen model on a **different** cohort (e.g. train ADNI → test AIBL/OASIS; PPMI → held-out site/time split) and report AUC with 95% CI, sensitivity, specificity, calibration (ECE) and age/sex subgroup performance.
3. Compare against logistic-regression and random-forest baselines and report whether the deep model is justified.

**Intended use of results:** research and publication only. The software is a clinical decision-support research prototype, **not** a diagnostic device, and no clinical decisions will be made from it.

**Data requested:** [see per-cohort section]. **Participants:** de-identified; no attempt will be made to re-identify any participant or contact any participant or site.

**Analysis plan:** pre-specified thresholds — external AUC ≥ 0.85 (AD vs CN) / ≥ 0.80 (PD progression), lower 95% CI ≥ 0.75, sensitivity and specificity ≥ 0.80, ECE ≤ 0.10, subgroup AUC gap ≤ 0.05. Results are reported whether or not thresholds are met. The pipeline (`backend/scripts/train_and_validate.py`, `trl5_gate.py`) is version-controlled.

## 2. Data-security and governance statement

- Data are stored only on [ENCRYPTED SERVER/WORKSTATION, LOCATION] with full-disk encryption, role-based access limited to the named investigators, and an access log.
- Data are never committed to a code repository, never uploaded to third-party services or external AI APIs, and never redistributed or shared with persons not named on the approved application.
- Derived artifacts shared publicly (model weights, metrics, figures) contain no participant-level data; small cells (< 10) are suppressed in published tables.
- Copies are deleted [WITHIN N DAYS] after the project ends or when the agreement requires.
- Any security incident is reported to the data provider and institution within [N] hours.
- Publications will use the acknowledgement and citation text required by each data provider and will list the data provider's investigators where requested.

## 3. Per-cohort texts

### 3.1 ADNI (Alzheimer's Disease Neuroimaging Initiative) — development cohort for AD
**Request:** baseline and longitudinal 3T T1-weighted MRI, clinical diagnosis (CN/MCI/AD), MMSE/CDR/ADAS-Cog, APOE genotype, CSF/plasma biomarkers (amyloid, tau), demographics.
**Justification:** ADNI is the reference cohort for multimodal AD modelling and is the development set against which external generalisation (AIBL, OASIS) is tested.
**Special notes:** state that results will be reported with the ADNI acknowledgement; the ADNI data-use terms require that publications include the ADNI acknowledgement text and that ADNI investigators need not be authors unless they contribute to the analysis.

### 3.2 AIBL (Australian Imaging, Biomarker & Lifestyle Study) — external AD test cohort
**Request:** T1-weighted MRI, diagnosis, cognitive scores, APOE, demographics for the participants available through the data-access route.
**Justification:** AIBL is acquired on different scanners/protocols and country from ADNI. Evaluating a frozen ADNI-trained model on AIBL measures cross-site, cross-population generalisation, the central TRL-5 criterion (C2). Related work: Bloch & Friedrich, Comput Biol Med 2024, doi:10.1016/j.compbiomed.2024.108029 (ADNI → AIBL/OASIS).
**Special notes:** AIBL-specific publication policy and acknowledgement apply.

### 3.3 OASIS (Open Access Series of Imaging Studies) — second external AD test cohort
**Request:** OASIS-3 T1w MRI with clinical assessments and diagnoses; OASIS-1/2 if useful (openly available).
**Justification:** independent third source for external validation and robustness across age ranges; OASIS-3 includes longitudinal cognitively normal and impaired adults.
**Special notes:** sign the OASIS-3 data use terms; cite the OASIS-3 reference and funding acknowledgement as specified by the data owner.

### 3.4 PPMI (Parkinson's Progression Markers Initiative) — PD cohort
**Request:** clinical assessments (MDS-UPDRS, MoCA), DaTscan SBR values, MRI where available, CSF/blood biomarkers, genetics (only if permitted), medication and demographic data, longitudinal follow-up.
**Justification:** PPMI is the standard multimodal PD cohort. We predict rapid motor progression and future cognitive impairment, with an external check on a held-out site/time period or a second PD dataset, if available.
**Special notes:** follow PPMI's publication policy (including the PPMI authorship/acknowledgement language and any data-and-publications-committee review).

## 4. Cover email template

> Subject: Data access request — [PROJECT TITLE]
>
> Dear [DATA ACCESS COMMITTEE],
>
> I am [NAME], [TITLE] at [INSTITUTION], [COUNTRY]. I am applying for access to [COHORT] data for research on explainable multimodal risk stratification of Alzheimer's/Parkinson's disease, as described in the attached application. All data will be handled under the security measures in Section 2, used only for the stated research, and never redistributed. My institution's signatory, [NAME/EMAIL], will countersign the data use agreement. Please let me know if any further information is required.
>
> Sincerely,
> [NAME], [ORCID], [INSTITUTIONAL EMAIL]

## 5. After approval / پس از تأیید

1. Download into the encrypted location from Section 2 only; keep `data/` out of git (check `.gitignore`).
2. Record cohort, version, download date and file checksums in `models/validation/DATA_PROVENANCE.md`.
3. Train: `python backend/scripts/train_and_validate.py --data <dev_cohort.csv> ...`
4. Evaluate on the external cohort, write `models/validation/external_<cohort>.json` with `data_source` set to the real cohort name.
5. Run `python backend/scripts/trl5_gate.py`; claim TRL 5 only when every criterion passes.
