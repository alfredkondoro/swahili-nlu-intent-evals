# Dataset Card — SwahiliNLU

> Following the data documentation framework of Gebru et al. (2021), *Datasheets for Datasets*. Communications of the ACM, 64(12), 86–92. https://doi.org/10.1145/3458723

---

## Dataset Summary

**SwahiliNLU** is a broad-domain, natively constructed intent recognition and slot-filling dataset for Swahili. It comprises 3,633 utterances spanning 10 domains and 175 intent classes, annotated with BIO-compatible slot labels and a three-way pragmatic tone annotation layer (imperative, polite, conversational). It is the first Swahili intent dataset to include tone annotations and the largest natively constructed Swahili intent resource to date.

| Property | Value |
|---|---|
| **Language** | Swahili (sw) |
| **Task** | Intent classification, slot filling, tone classification |
| **Total utterances** | 3,633 |
| **Domains** | 10 |
| **Intent classes** | 175 |
| **Slot types** | 105 |
| **Total slot annotations** | 5,079 |
| **Utterances with ≥1 slot** | 3,037 (83.6%) |
| **Tone categories** | 3 (imperative, polite, conversational) |
| **Inter-annotator agreement (overall)** | κ = 0.87 (intent, tone and slot, 10% subset) |
| **Avg. tokens / utterance** | ~7.2 |
| **License** | CC BY 4.0 |
| **Paper** | SwahiliNLU: A Broad-Domain Intent and Slot-Filling Dataset with Pragmatic Tone Annotations for Low-Resource NLU (CIKM 2026, under review) |
| **DOI (dataset)** | [10.5281/zenodo.20521261](https://doi.org/10.5281/zenodo.20521261) |

---

## Motivation

### Why was this dataset created?

Swahili is spoken by over 200 million people across East and Central Africa and serves as an official language in Tanzania, Kenya, Uganda and the Democratic Republic of Congo. Despite this reach, Swahili remains severely under-resourced for NLU tasks. Existing multilingual benchmarks either omit Swahili or include it via translation from English, which fails to capture authentic linguistic structures and pragmatic conventions.

SwahiliNLU was created to:
1. Provide a natively constructed Swahili NLU benchmark for the research community
2. Cover mobile virtual assistant use cases relevant to East African users
3. Introduce pragmatic tone annotation with a compound inter-annotator agreement of κ = 0.87 across intent, tone and slot on a 10% double-annotated subset — a dimension absent from prior Swahili and African-language intent datasets

### Who created the dataset?

The dataset was created by Alfred Malengo Kondoro (Hanyang University) and Alexander Rogath Kivaisi (University of Dar es Salaam), with domain-specific utterance elicitation and annotation by 11 native Swahili speakers at the University of Dar es Salaam:

| Contributor | Domain |
|---|---|
| Salum Said Juma | Food Ordering |
| Joseph Henry | Communication |
| Upendo Chacha | Media & Entertainment |
| Esuvath Stanley Lotha | Device Settings |
| Kalistine Gilala Leopold | Ride-Hailing & Transport |
| Asfath Hussein | News & Information |
| Justine Mponzi | Finance |
| Fredrick Kasanga | Food Ordering |
| Clara Haraka Mittah | Travel & Accommodation |
| Luhende Yusuph Bonda | Health & Lifestyle |
| Mkupete Mkamba Jaah | Home Automation |

### Who funded the creation?

This work was supported by Hanyang University and the University of Dar es Salaam.

---

## Composition

### What does the dataset consist of?

The dataset consists of text utterances in Swahili, each annotated with:
- **Intent label** — one of 175 fine-grained intent classes across 10 domains
- **Slot annotations** — a JSON dictionary mapping slot types to their text span values
- **Tone label** — one of three pragmatic tone categories

### Domain breakdown

| Domain | Utterances | Intents |
|---|---|---|
| Travel & Accommodation | 546 | 22 |
| Communication | 513 | 21 |
| Finance | 461 | 20 |
| Food Ordering | 433 | 18 |
| Device Settings | 414 | 24 |
| Media & Entertainment | 376 | 19 |
| Health & Lifestyle | 291 | 17 |
| News & Information | 215 | 9 |
| Ride-Hailing & Transport | 179 | 14 |
| Home Automation | 208 | 11 |
| **Total** | **3,633** | **175** |

### Tone distribution

| Tone | Count | Percentage |
|---|---|---|
| Polite | 1,382 | 38.0% |
| Conversational | 1,299 | 35.7% |
| Imperative | 952 | 26.2% |

### Does the dataset contain all possible instances or a sample?

The dataset is a curated sample of possible Swahili utterances. It does not claim to be exhaustive. Each intent has between 3 and approximately 20 utterances depending on domain complexity.

### Is there any information that could be used to identify individuals?

No. The dataset contains no personal information. All utterances are elicited — created by annotators for the purpose of this dataset. Contact names (e.g. "John", "Amina") and phone numbers used as slot values are fictional.

### Does the dataset contain offensive, harmful, or sensitive content?

No. All utterances describe benign everyday mobile assistant interactions. No offensive language, sensitive topics, or harmful content is present.

---

## Collection Process

### How was the data collected?

Utterances were **elicited** from native Swahili speakers — contributors wrote utterances from scratch based on intent definitions and slot schemas provided in the annotation guidelines. This approach was chosen over translation (used in MASSIVE) to ensure authentic Swahili morphosyntax and pragmatic conventions.

Each contributor was assigned one domain and asked to produce utterances covering:
- All intent classes in their domain
- All three tone categories per intent (imperative, polite, conversational)
- Variety in phrasing and slot combinations

### What mechanisms were used to collect the data?

Utterances were submitted as CSV files with columns: `Intent`, `Utterance`, `Slots`, `Label`. Contributors used Google Sheets, which introduces double-escaped JSON formatting (`""key""`) that was normalised programmatically during data preparation.

### Over what time period was the data collected?

Data collection took place between January and May 2026.

### Were any ethical review processes conducted?

The dataset involves no human subjects data, personal information, or sensitive content. All contributors are co-authors or credited in the acknowledgements and provided informed consent for their contributions to be used in this research dataset.

---

## Preprocessing

### Was any preprocessing done?

Yes. The following preprocessing steps were applied:

1. **Column normalisation** — standardised column names across files with different headers (`Intent`/`intent`, `Label`/`tone`)
2. **JSON normalisation** — fixed double-escaped JSON from Google Sheets export (`""key""` → `"key"`)
3. **Tone extraction** — for files where tone was embedded in the slots JSON, it was extracted to a dedicated column and removed from the slots dictionary
4. **Duplicate removal** — exact duplicate utterances were identified and removed
5. **Rare intent filtering** — intents with fewer than 3 samples were excluded from train/dev/test splits (2 intents removed: `arm_security_system`, `schedule_ride`)

### Is the raw data available?

Yes. The raw CSV files (one per domain) are available in the dataset release on Zenodo. Preprocessing code is available in the GitHub repository.

---

## Distribution

### How is the dataset distributed?

| Resource | Location |
|---|---|
| Dataset (CSV files) | Zenodo: [10.5281/zenodo.20521261](https://doi.org/10.5281/zenodo.20521261) |
| Code and notebooks | https://github.com/alfredkondoro/swahili-nlu-intent-evals |
| Paper | CIKM 2026 Proceedings *(link to be added after publication)* |

### What license does the dataset use?

The dataset is released under **Creative Commons Attribution 4.0 International (CC BY 4.0)**.
Code is released under the **MIT License**.

You are free to share and adapt the dataset for any purpose, provided appropriate credit is given.

### Have any third parties imposed restrictions on the data?

No. All utterances were created by the annotation team and are not derived from any copyrighted source.

---

## Maintenance

### Who is responsible for maintaining the dataset?

Alfred Malengo Kondoro (alfr3do@hanyang.ac.kr) is the primary point of contact.

### Will the dataset be updated?

Yes. Planned updates include:
- Additional utterances for under-represented domains (Ride-Hailing, Home Automation, Communication)
- Code-switching (Swahili-English) utterances
- Slot-level inter-annotator agreement scores
- Audio and visual extensions to support multimodal intent recognition

### How can errors or issues be reported?

Please open a GitHub issue at https://github.com/alfredkondoro/swahili-nlu-intent-evals/issues or contact the maintainer by email.

---

## Intended Uses

### What are the intended uses?

- Training and evaluating Swahili intent classification models
- Training and evaluating Swahili slot filling models
- Tone-aware dialogue system research
- Low-resource NLU benchmarking
- Cross-lingual transfer learning research for African languages

### Are there uses that should be avoided?

- This dataset should not be used to train systems for surveillance or social profiling
- The dataset does not represent all Swahili dialects — systems trained on it may not generalise to Congolese Swahili or other regional varieties
- The dataset should not be used as-is for safety-critical applications without further validation

---

## Known Limitations

1. **Dataset size** — 3,633 utterances is modest compared to English benchmarks. Models trained on this dataset may not generalise to out-of-distribution intents.
2. **Class imbalance** — intent class sizes range from approximately 3 to 20 utterances, which affects Macro-F1 reliability for rare intents.
3. **Elicited utterances** — utterances were written by contributors rather than collected from real user interactions. Distribution may differ from real-world usage.
4. **No code-switching** — Swahili-English code-switching, common in urban East Africa, is not covered in this version.
5. **Single-turn utterances** — the dataset does not cover multi-turn dialogue.
6. **Dialect coverage** — the dataset reflects Tanzanian Standard Swahili. Kenyan Swahili and Congolese Swahili variants are not covered.
7. **IAA scope** — κ = 0.87 is a compound score across intent, tone and slot annotations on a 10% subset. Per-layer breakdown (intent, tone and slot separately) is a priority for the next release.

---

## Citation

The paper describing this dataset is currently under review. A full citation will be added upon publication. In the meantime, if you use SwahiliNLU please cite the Zenodo dataset record:

> Kondoro, A. M., & Kivaisi, A. R. (2026). *SwahiliNLU: A Broad-Domain Intent and Slot-Filling Dataset with Pragmatic Tone Annotations*. Zenodo. https://doi.org/10.5281/zenodo.20521261

### Framework reference

This datacard follows:

> Gebru, T., Morgenstern, J., Vecchione, B., Wortman Vaughan, J., Wallach, H., Daumé III, H., & Crawford, K. (2021). Datasheets for datasets. *Communications of the ACM*, 64(12), 86–92. https://doi.org/10.1145/3458723

---

*Dataset card version 1.1 — June 2026*
