# Corpus Review from Deep Research

## Accepted and integrated

- `who_physical_activity_2020`: accepted. Official WHO guideline with direct PDF.
- `nsca_professional_standards_2017`: accepted. Official NSCA PDF and strong safety value.
- `acsm_progression_models_2009`: accepted as a canonical abstract-backed source for progression logic. The 2026 ACSM update cited in the report was not integrated because the report relied on unofficial mirrors.
- `hypertrophy_umbrella_review_2022`: accepted. Open umbrella review from Frontiers.
- `low_vs_high_load_2017`: accepted. PubMed abstract integrated because the paper is central and the abstract is reliably accessible.
- `training_frequency_hypertrophy_2019`: accepted. PubMed abstract integrated for frequency logic.
- `minimal_dose_resistance_2017`: accepted. Useful for short-session and minimum-effective-dose logic.
- `elastic_resistance_healthy_adults_2017`: accepted. Directly aligned with `home_basic` and healthy adults.
- `free_weight_vs_machine_2023`: accepted. Open-access PDF via Springer.
- `joint_flexibility_rt_2025`: accepted. Useful for reducing redundant warmup/stretching prescriptions.
- `deep_squat_lumbar_kyphosis_2025`: accepted cautiously. Included only as a biomechanical source for conservative restrictions handling.
- `semed_exercise_prescription_2015`: accepted. Spanish consensus improves terminology and local framing.

## Rejected or not integrated directly

- ACSM 2026 from `storage.e.jimdo.com`: rejected as a corpus source because it is an unofficial mirror.
- ACSM 2026 from ResearchGate: rejected as a primary storage source.
- `2 Minute Medicine`: rejected. Secondary commentary, not corpus material.
- `Spire Healthcare`: rejected. Non-academic patient-facing content.
- `dokumen.pub`: rejected. Unreliable document host.
- `Clinical Gate`: rejected. Clinical/rehabilitation framing outside project scope.
- Low-impact and osteoarthritis clinical reviews: not integrated into the default corpus because they push the project too close to rehabilitation. If needed, they should be added as restricted-use evidence only.

## Application changes

- The default corpus metadata now points to the curated downloadable sources above.
- The project includes an automated fetcher: [rag/download_corpus.py](/home/ndk/proyectos/clase/iagen_v2/rag/download_corpus.py).
- The ingestion pipeline can now be rebuilt from a real academic corpus instead of the original demo-only evidence briefs.

