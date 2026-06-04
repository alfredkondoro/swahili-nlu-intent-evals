# SwahiliNLU Annotation Guidelines

**Version:** 1.0  
**Dataset:** SwahiliNLU — A Broad-Domain Swahili Intent and Slot-Filling Dataset with Pragmatic Tone Annotations  
**Institution:** University of Dar es Salaam & Hanyang University  
**Last updated:** June 2026  

---

## Table of Contents
1. [Overview](#overview)
2. [Intent Annotation](#intent-annotation)
3. [Slot Annotation](#slot-annotation)
4. [Tone Annotation](#tone-annotation)
5. [Quality Control](#quality-control)
6. [Examples](#examples)
7. [Common Mistakes](#common-mistakes)

---

## 1. Overview

SwahiliNLU is a natively constructed Swahili NLU dataset covering 10 domains and 175+ intent classes. Each utterance is annotated with three layers:

| Layer | Description |
|---|---|
| **Intent** | The action or goal the user wants to accomplish |
| **Slots** | Named entities or parameters relevant to the intent |
| **Tone** | The pragmatic register of the utterance |

Each annotator was responsible for one domain. Utterances were **elicited** (written from scratch by native Swahili speakers), not translated from English.

---

## 2. Intent Annotation

### 2.1 What is an intent?

An intent is the underlying goal or action expressed in an utterance. Each intent belongs to exactly one domain.

### 2.2 Domains and intent classes

| Domain | Example intents |
|---|---|
| Communication | `make_phone_call`, `send_message`, `start_videocall` |
| Device Settings | `control_wifi`, `adjust_brightness`, `set_alarm` |
| Finance | `check_account_balance`, `send_money`, `buy_airtime` |
| Food Ordering | `search_restaurant`, `place_food_order`, `track_food_order` |
| Health & Lifestyle | `track_steps`, `log_meal`, `set_fitness_goal` |
| Home Automation | `control_lights`, `control_ac`, `control_door_lock` |
| Media & Entertainment | `play_music`, `search_video`, `create_playlist` |
| News & Information | `open_news_intent`, `search_news`, `share_news_article` |
| Ride-Hailing & Transport | `request_ride`, `cancel_ride`, `track_ride` |
| Travel & Accommodation | `search_transport_options`, `book_accommodation`, `modify_booking` |

### 2.3 Rules for intent assignment

- **One intent per utterance** — each utterance expresses exactly one primary intent
- **Use the most specific intent** — prefer `send_money_to_mobile_wallet` over `send_money` if the target is clearly a mobile wallet
- **Intent reflects the user's goal, not the action verb** — *"Je, naweza kujua salio langu?"* is `check_account_balance` even though it is phrased as a question

---

## 3. Slot Annotation

### 3.1 What is a slot?

A slot is a named entity or parameter that fills a role relevant to the intent. Slots are stored as a JSON dictionary where the key is the slot type and the value is the exact text span from the utterance.

```json
{"destination": "Kariakoo", "pickup_location": "Goba", "app_name": "Bolt"}
```

### 3.2 Slot extraction rules

- **Exact span** — copy the slot value exactly as it appears in the utterance, preserving case and spelling
- **No inference** — only annotate slots that are explicitly mentioned in the utterance. Do not infer unstated values
- **Multiple slots allowed** — an utterance may have zero, one, or many slots
- **Empty slots** — if an intent has no named entities in the utterance, the slots field should be `{}`

### 3.3 Common slot types by domain

| Slot type | Domain | Example value |
|---|---|---|
| `contact_name` | Communication | `"John"` |
| `phone_number` | Communication | `"0712345678"` |
| `app_name` | Multiple | `"Bolt"`, `"Spotify"`, `"BBC News"` |
| `destination` | Ride-Hailing, Travel | `"Kariakoo"`, `"Nairobi"` |
| `pickup_location` | Ride-Hailing | `"Goba"` |
| `account_type` | Finance | `"M-Pesa"`, `"NMB"` |
| `amount` | Finance | `"5000"` |
| `song_title` | Media | `"Sugua"` |
| `artist_name` | Media | `"Diamond"` |
| `cuisine_type` | Food | `"chipsi"` |
| `time_period` | Health | `"leo"`, `"wiki hii"` |
| `action` | Device, Home | `"on"`, `"off"` |
| `location` | Home | `"sebuleni"` |
| `transport_type` | Travel | `"flight"`, `"bus"` |
| `date` | Travel | `"10 Juni"`, `"kesho"` |

### 3.4 Slot annotation format

Slots are stored as JSON in the `slots` column. Do **not** include the `tone` key in the slots JSON — tone has its own dedicated column.

**Correct:**
```json
{"destination": "Kariakoo", "app_name": "Bolt"}
```

**Incorrect (tone inside slots):**
```json
{"destination": "Kariakoo", "app_name": "Bolt", "tone": "imperative"}
```

---

## 4. Tone Annotation

### 4.1 What is tone?

Tone captures the pragmatic register of an utterance — how the speaker frames their request. SwahiliNLU uses a three-way distinction motivated by real variation in Swahili speech:

### 4.2 Tone categories

#### 🔴 Imperative
A direct command or instruction with no softening markers. The speaker states the action they want performed without politeness hedges.

**Linguistic markers:** imperative verb forms, no *tafadhali* or *naomba*

**Examples:**
- *Piga simu* (Call)
- *Agiza Bolt kutoka Goba hadi Kariakoo* (Order Bolt from Goba to Kariakoo)
- *Zima taa* (Turn off the lights)
- *Cheza wimbo wa Diamond* (Play a Diamond song)

---

#### 🟢 Polite
The speaker uses explicit politeness markers to soften the request. Common markers include *tafadhali* (please), *naomba* (I request/please), *unaweza* (can you), *ningependa* (I would like).

**Linguistic markers:** *tafadhali*, *naomba*, *ningependa*, *unaweza*, subjunctive mood

**Examples:**
- *Tafadhali piga simu kwa John* (Please call John)
- *Naomba unisaidie kuagiza chakula* (Please help me order food)
- *Ningependa kujua salio langu* (I would like to know my balance)
- *Unaweza kunipigia Amina?* (Can you call Amina for me?)

---

#### 🔵 Conversational
Casual, informal, or hedged speech. The utterance has a relaxed, everyday register — as one might speak to a friend or a familiar assistant. May include filler phrases, contractions, or informal phrasing.

**Linguistic markers:** informal register, hedges, colloquial phrasing, question forms without explicit politeness markers

**Examples:**
- *Nipigie tu John haraka* (Just quickly call John)
- *Niambie salio langu iko ngapi?* (Tell me how much my balance is?)
- *Nionyeshe tu nyimbo za Diamond* (Just show me Diamond's songs)
- *Niko wapi basi la Arusha?* (Where is the bus to Arusha?)

---

### 4.3 Tone annotation rules

- **Assign tone based on the utterance as written** — do not infer intent or context
- **One tone per utterance** — every utterance has exactly one tone label
- **When in doubt between imperative and conversational** — if the utterance has no softening markers but sounds casual due to word choice or phrasing, label it **conversational**
- **Polite markers override everything** — if *tafadhali* or *naomba* appears, the tone is always **polite**
- **Questions are not automatically polite** — *Je, unaweza...?* may be polite, but *Niambie...?* is conversational

### 4.4 Tone distribution target

Each intent should have utterances covering all three tone categories. Aim for approximately equal distribution across tones per intent:

| Tone | Target proportion |
|---|---|
| Imperative | ~33% |
| Polite | ~33% |
| Conversational | ~33% |

---

## 5. Quality Control

### 5.1 Self-review checklist

Before submitting your domain's CSV, verify:

- [ ] Every row has a non-empty `intent`, `utterance`, and `slots` value
- [ ] All intent names match the approved taxonomy exactly (no typos, no extra spaces)
- [ ] Slot values are copied exactly from the utterance text
- [ ] Tone is one of: `imperative`, `polite`, `conversational` (lowercase)
- [ ] No duplicate utterances within the same intent
- [ ] Tone is in its own column, not inside the slots JSON
- [ ] Utterances are in Swahili (code-switching with English is acceptable if natural)

### 5.2 File format

Each domain CSV must follow this format:

```
Intent,Utterance,Slots,Label
make_phone_call,Piga simu,{},imperative
make_phone_call,Tafadhali mpigie John,{"contact_name":"John"},polite
```

- Column headers: `Intent`, `Utterance`, `Slots`, `Label`
- `Slots`: valid JSON, no `tone` key
- `Label`: tone value in lowercase

### 5.3 Inter-annotator agreement

A 10% random sample from each domain was validated by a second native Swahili speaker. The target inter-annotator agreement for tone is **κ ≥ 0.80**. The final dataset achieved **κ = 0.87** on tone labels.

---

## 6. Examples

### 6.1 Well-annotated examples

| Intent | Utterance | Slots | Tone |
|---|---|---|---|
| `request_ride` | Agiza Bolt kutoka Goba hadi Kariakoo | `{"destination":"Kariakoo","pickup_location":"Goba","app_name":"Bolt"}` | imperative |
| `request_ride` | Tafadhali nipigie Bolt kutoka Goba | `{"pickup_location":"Goba","app_name":"Bolt"}` | polite |
| `request_ride` | Ninahitaji kwenda Kariakoo, niweze kupata Bolt? | `{"destination":"Kariakoo","app_name":"Bolt"}` | conversational |
| `send_money` | Tuma elfu tano kwa Amina | `{"amount":"elfu tano","contact_name":"Amina"}` | imperative |
| `play_music` | Naomba ucheze wimbo wa Diamond | `{"artist_name":"Diamond"}` | polite |
| `check_account_balance` | Salio langu iko ngapi sasa hivi? | `{}` | conversational |

### 6.2 Borderline cases

| Utterance | Correct tone | Reasoning |
|---|---|---|
| *Nipigie simu Amina* | imperative | No softening markers, direct command |
| *Unaweza kunipigia Amina?* | polite | *Unaweza* is a softening marker |
| *Nipigie tu Amina haraka* | conversational | Casual register (*tu*, *haraka*), not a direct command form |
| *Niambie salio langu* | conversational | Informal phrasing, not a direct imperative |
| *Angalia salio* | imperative | Direct command verb form |

---

## 7. Common Mistakes

| Mistake | Correct approach |
|---|---|
| Using English intent names | Use the approved Swahili-context intent names from the taxonomy |
| Putting tone inside the JSON slots | Tone goes in the `Label` column, not in `slots` |
| Inferring slot values not in the utterance | Only annotate what is explicitly stated |
| Marking all questions as polite | Questions are only polite if they contain explicit politeness markers |
| Marking *naomba* utterances as conversational | *Naomba* always indicates polite tone |
| Inconsistent capitalisation in slot values | Copy the exact text from the utterance |

---

*For questions about these guidelines, contact the project lead.*
