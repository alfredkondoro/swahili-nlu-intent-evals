# SwahiliNLU

**A Broad-Domain Intent and Slot-Filling Dataset with Pragmatic Tone Annotations for Low-Resource NLU**

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20521261.svg)](https://doi.org/10.5281/zenodo.20521261)
[![License: CC BY 4.0](https://img.shields.io/badge/Dataset-CC%20BY%204.0-blue.svg)](https://creativecommons.org/licenses/by/4.0/)
[![License: MIT](https://img.shields.io/badge/Code-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Paper](https://img.shields.io/badge/Paper-CIKM%202026-red.svg)](#citation)

---

## Overview

SwahiliNLU is the first broad-domain, natively constructed intent recognition and slot-filling dataset for Swahili. It covers **10 domains**, **175 intent classes** and **105 slot types**, and introduces the first **pragmatic tone annotation** (imperative / polite / conversational) for any African language NLU dataset.

| Statistic | Value |
|---|---|
| Total utterances | 3,633 |
| Domains | 10 |
| Unique intents | 175 |
| Unique slot types | 105 |
| Total slot annotations | 5,079 |
| Utterances with ≥1 slot | 3,037 (83.6%) |
| Tone categories | 3 |
| Inter-annotator agreement (tone) | κ = 0.87 |
| Language | Swahili (sw) |

---

## Dataset

The dataset is permanently archived on Zenodo:

> **DOI:** [10.5281/zenodo.20521261](https://doi.org/10.5281/zenodo.20521261)

It is organised into 10 CSV files, one per domain:

| Domain | File | Utterances |
|---|---|---|
| Communication | `communication.csv` | 513 |
| Device Settings | `device_settings.csv` | 414 |
| Finance | `finance.csv` | 461 |
| Food Ordering | `food_ordering.csv` | 433 |
| Health & Lifestyle | `health_lifestyle.csv` | 291 |
| Home Automation | `home_automation.csv` | 208 |
| Media & Entertainment | `media_and_entertainment.csv` | 376 |
| News & Information | `news_and_information.csv` | 215 |
| Ride-Hailing & Transport | `ride_hailing_and_transport_services.csv` | 179 |
| Travel & Accommodation | `travel_transport_and_accomodation.csv` | 546 |

### Column format

Each CSV has four columns:

```
Intent, Utterance, Slots, Label
request_ride, Agiza Bolt kutoka Goba hadi Kariakoo, {"destination":"Kariakoo","pickup_location":"Goba","app_name":"Bolt"}, imperative
```

| Column | Description |
|---|---|
| `Intent` | Intent class label |
| `Utterance` | Native Swahili utterance |
| `Slots` | JSON dictionary of slot name → text span |
| `Label` | Tone label: `imperative`, `polite` or `conversational` |

---

## Tone Annotation

SwahiliNLU introduces a three-way pragmatic tone annotation layer — the first in any African language NLU dataset:

| Tone | Description | Example |
|---|---|---|
| **Imperative** | Direct command, no softening markers | *Agiza Bolt kutoka Goba hadi Kariakoo* |
| **Polite** | Uses *tafadhali* (please) or *naomba* (I request) | *Naomba unisaidie kuagiza chakula* |
| **Conversational** | Casual or hedged informal register | *Unaweza kunipigia simu Amina?* |

See [`annotation/annotation_guidelines.md`](annotation/annotation_guidelines.md) for the full annotation protocol.

---

## Baseline Results

### Intent and Tone Classification

| Model | Task | Accuracy | Macro-F1 | Weighted-F1 |
|---|---|---|---|---|
| mBERT | Intent | 0.5734 | 0.4834 | 0.5140 |
| XLM-R | Intent | 0.4418 | 0.3322 | 0.3645 |
| **AfroXLMR** | **Intent** | **0.6316** | **0.5435** | **0.5740** |
| mBERT | Tone | 0.9266 | 0.9259 | 0.9265 |
| XLM-R | Tone | 0.9432 | 0.9427 | 0.9432 |
| **AfroXLMR** | **Tone** | **0.9474** | **0.9474** | **0.9473** |
| Claude Sonnet | Intent | 0.8800 | 0.3972 | — |
| GPT-4o mini | Intent | 0.8600 | 0.7008 | — |
| Gemini 2.5 Flash | Intent | 0.9100 | 0.7553 | — |
| **Claude Sonnet** | **Tone** | **0.7300** | **0.6982** | — |
| Gemini 2.5 Flash | Tone | 0.6800 | 0.6213 | — |
| GPT-4o mini | Tone | 0.5700 | 0.4625 | — |

> Zero-shot LLMs evaluated on a 100-sample test subset. Bold = best per task per model category.

### Slot Filling (seqeval Macro-F1)

| Model | Slot F1 |
|---|---|
| **mBERT** | **0.4686** |
| XLM-R | 0.3396 |
| AfroXLMR | 0.3255 |

Full per-domain results are available in [`baselines/`](baselines/).

---

## Repository Structure

```
swahili-nlu-intent-evals/
├── README.md
├── LICENSE
├── experiments/
│   ├── swahilinlu_experiments_modular.ipynb   # main experiments notebook (Kaggle)
│   └── swahilinlu_eda.ipynb                   # EDA notebook
├── src/                                        # importable Python modules
│   ├── swahili_data.py                         # data loading and cleaning
│   ├── swahili_datasets.py                     # PyTorch Dataset classes + BIO utilities
│   ├── swahili_train.py                        # fine-tuning classifiers and slot models
│   ├── swahili_llm.py                          # zero-shot LLM evaluation
│   └── swahili_eval.py                         # per-domain analysis, charts, LaTeX
├── data/
│   └── datacard.md                             # dataset documentation card
├── annotation/
│   └── annotation_guidelines.md               # full annotation protocol
├── baselines/
│   ├── results_final.csv
│   ├── per_domain_intent_f1.csv
│   └── per_domain_tone_f1.csv
└── paper/
    ├── SwahiliNLU_CIKM_final.tex
    └── references.bib
```

---

## Quickstart

### Load the dataset

```python
from src.swahili_data import load_dataset

df = load_dataset('/path/to/intent/csvs')
print(df.head())
# intent  utterance  slots  tone  source_file
```

### Run intent classification

```python
from sklearn.preprocessing import LabelEncoder
from src.swahili_train import train_classifier

intent_enc = LabelEncoder().fit(df['intent'])
result = train_classifier(
    model_name    = 'Davlan/afro-xlmr-base',
    model_key     = 'AfroXLMR',
    train_df      = train_df,
    dev_df        = dev_df,
    test_df       = test_df,
    label_encoder = intent_enc,
    num_labels    = len(intent_enc.classes_),
    task_name     = 'Intent',
    device        = 'cuda',
    seed          = 42
)
print(result['overall'])
```

### Run on Kaggle

1. Upload the dataset to Kaggle as a dataset
2. Open `experiments/swahilinlu_experiments_modular.ipynb`
3. Set accelerator to **T4 GPU** and enable **Internet**
4. Add API keys under **Add-ons → Secrets**: `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GEMINI_API_KEY`
5. Run all cells

---

## Models Used

| Model | HuggingFace ID |
|---|---|
| mBERT | `bert-base-multilingual-cased` |
| XLM-R | `xlm-roberta-base` |
| AfroXLMR | `Davlan/afro-xlmr-base` |
| Claude Sonnet | `claude-sonnet-4-5` (Anthropic API) |
| GPT-4o mini | `gpt-4o-mini` (OpenAI API) |
| Gemini 2.5 Flash | `gemini-2.5-flash` (Google API) |

---

## Contributors

**Authors:**
- Alfred Malengo Kondoro — Hanyang University, Seoul ([alfr3do@hanyang.ac.kr](mailto:alfr3do@hanyang.ac.kr))
- Alexander Rogath Kivaisi — University of Dar es Salaam ([kivaisi.alexander@udsm.ac.tz](mailto:kivaisi.alexander@udsm.ac.tz))

**Domain Annotation Contributors** (University of Dar es Salaam):

| Contributor | Domain |
|---|---|
| Salum Said Juma | Food Ordering |
| Joseph Henry | Communication |
| Upendo Chacha | Media & Entertainment |
| Esuvath Stanley Lotha | Device Settings |
| Kalistine Gilala Leopold | Ride-Hailing & Transport |
| Asfath Hussein | News & Information |
| Justine Mponzi | Finance |
| Fredrick Kasanga | Shopping |
| Clara Haraka Mittah | Travel & Accommodation |
| Luhende Yusuph Bonda | Health & Lifestyle |
| Mkupete Mkamba Jaah | Home Automation |

---

## License

- **Dataset:** [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/)
- **Code:** [MIT License](https://opensource.org/licenses/MIT)

---

## Citation

The paper describing this dataset is currently under review. A citation will be added upon publication. In the meantime, if you use SwahiliNLU please cite the Zenodo dataset record:

> Kondoro, A. M., & Kivaisi, A. R. (2026). *SwahiliNLU: A Broad-Domain Intent and Slot-Filling Dataset with Pragmatic Tone Annotations*. Zenodo. https://doi.org/10.5281/zenodo.20521261

---

## Related Work

- [INJONGO](https://arxiv.org/abs/2502.09814) — Multicultural intent dataset for 16 African languages
- [Maneno Yetu](https://doi.org/10.1145/3746252.3761628) — Dynamic Swahili corpus and foundational language model
- [AfroXLMR](https://aclanthology.org/2022.coling-1.382/) — Multilingual pre-trained model for African languages
