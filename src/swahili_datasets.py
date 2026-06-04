"""PyTorch Dataset classes and BIO tagging utilities for SwahiliNLU."""
import json
import torch
import pandas as pd
from torch.utils.data import Dataset


class IntentDataset(Dataset):
    """Dataset for sequence classification (intent or tone)."""

    def __init__(self, texts, labels, tokenizer, max_len=128):
        self.encodings = tokenizer(
            list(texts), truncation=True, padding=True,
            max_length=max_len, return_tensors='pt'
        )
        self.labels = torch.tensor(labels, dtype=torch.long)

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        item = {k: v[idx] for k, v in self.encodings.items()}
        item['labels'] = self.labels[idx]
        return item


class SlotDataset(Dataset):
    """Dataset for token classification (slot filling)."""

    def __init__(self, data_df, tokenizer, tag2id, max_len=128):
        self.tokenizer = tokenizer
        self.tag2id    = tag2id
        self.max_len   = max_len
        self.data      = data_df.reset_index(drop=True)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        tokens = self.data.loc[idx, 'tokens']
        tags   = self.data.loc[idx, 'tags']
        enc    = self.tokenizer(
            tokens, is_split_into_words=True,
            truncation=True, padding='max_length',
            max_length=self.max_len, return_tensors='pt'
        )
        word_ids  = enc.word_ids(batch_index=0)
        label_ids = []
        prev_word = None
        for wid in word_ids:
            if wid is None:
                label_ids.append(-100)
            elif wid != prev_word:
                label_ids.append(self.tag2id.get(tags[wid], 0))
            else:
                tag = tags[wid]
                if tag.startswith('B-'):
                    tag = 'I-' + tag[2:]
                label_ids.append(self.tag2id.get(tag, 0))
            prev_word = wid
        return {
            'input_ids':      enc['input_ids'].squeeze(),
            'attention_mask': enc['attention_mask'].squeeze(),
            'labels':         torch.tensor(label_ids, dtype=torch.long)
        }


def make_bio_tags(utterance, slots_str):
    """Convert utterance + slots JSON string to a list of BIO tags."""
    tokens = utterance.strip().split()
    tags   = ['O'] * len(tokens)
    try:
        slots = json.loads(slots_str) if slots_str not in ('', '{}', 'nan') else {}
    except:
        slots = {}
    for slot_name, slot_value in slots.items():
        if not slot_value:
            continue
        sv_toks = str(slot_value).strip().split()
        n = len(sv_toks)
        ul = [t.lower() for t in tokens]
        sl = [t.lower() for t in sv_toks]
        for i in range(len(tokens) - n + 1):
            if ul[i:i + n] == sl:
                tags[i] = f'B-{slot_name}'
                for j in range(1, n):
                    tags[i + j] = f'I-{slot_name}'
                break
    return tokens, tags


def build_bio_df(source_df):
    """Build a BIO-tagged DataFrame from a source DataFrame."""
    rows = []
    for _, row in source_df.iterrows():
        t, g = make_bio_tags(row['utterance'], row['slots'])
        rows.append({'tokens': t, 'tags': g})
    return pd.DataFrame(rows)
