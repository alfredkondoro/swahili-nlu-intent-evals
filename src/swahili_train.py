"""Fine-tuning utilities for classification and slot filling tasks."""
import gc
import numpy as np
import pandas as pd
import torch
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    accuracy_score, f1_score, classification_report, confusion_matrix
)
from transformers import (
    AutoTokenizer, AutoModelForSequenceClassification,
    AutoModelForTokenClassification,
    TrainingArguments, Trainer,
    DataCollatorForTokenClassification
)
from seqeval.metrics import f1_score as seq_f1
from seqeval.metrics import classification_report as seq_report

from swahili_datasets import IntentDataset, SlotDataset


def train_classifier(model_name, model_key, train_df, dev_df, test_df,
                     label_encoder, num_labels, task_name,
                     device='cuda', seed=42, max_len=128):
    """
    Fine-tune a sequence classification model for intent or tone prediction.

    Returns:
        dict with keys 'overall' (metrics dict) and 'per_domain' (list of dicts)
    """
    print(f'\n{"="*60}\n  {task_name} | {model_key}\n{"="*60}')

    tokenizer    = AutoTokenizer.from_pretrained(model_name)
    col          = 'intent' if task_name == 'Intent' else 'tone'
    train_labels = label_encoder.transform(train_df[col])
    dev_labels   = label_encoder.transform(dev_df[col])
    test_labels  = label_encoder.transform(test_df[col])

    train_ds = IntentDataset(train_df['utterance'], train_labels, tokenizer, max_len)
    dev_ds   = IntentDataset(dev_df['utterance'],   dev_labels,   tokenizer, max_len)
    test_ds  = IntentDataset(test_df['utterance'],  test_labels,  tokenizer, max_len)

    model = AutoModelForSequenceClassification.from_pretrained(
        model_name, num_labels=num_labels, ignore_mismatched_sizes=True
    ).to(device)

    def compute_metrics(eval_pred):
        logits, labels = eval_pred
        preds = np.argmax(logits, axis=-1)
        return {
            'accuracy' : accuracy_score(labels, preds),
            'macro_f1' : f1_score(labels, preds, average='macro', zero_division=0)
        }

    args = TrainingArguments(
        output_dir                  = f'./results/{task_name.lower()}_{model_key}',
        num_train_epochs            = 10,
        per_device_train_batch_size = 32,
        per_device_eval_batch_size  = 64,
        warmup_ratio                = 0.1,
        weight_decay                = 0.01,
        learning_rate               = 2e-5,
        eval_strategy               = 'epoch',
        save_strategy               = 'no',
        load_best_model_at_end      = False,
        logging_steps               = 20,
        seed                        = seed,
        report_to                   = 'none',
        fp16                        = (device == 'cuda'),
    )

    trainer = Trainer(
        model=model, args=args,
        train_dataset=train_ds, eval_dataset=dev_ds,
        compute_metrics=compute_metrics
    )
    trainer.train()

    # Overall evaluation
    preds_out  = trainer.predict(test_ds)
    preds      = np.argmax(preds_out.predictions, axis=-1)
    pred_names = label_encoder.inverse_transform(preds)
    true_names = label_encoder.inverse_transform(test_labels)

    acc = accuracy_score(test_labels, preds)
    mf1 = f1_score(test_labels, preds, average='macro',    zero_division=0)
    wf1 = f1_score(test_labels, preds, average='weighted', zero_division=0)

    print(f'\n  Accuracy {acc:.4f} | Macro-F1 {mf1:.4f} | Weighted-F1 {wf1:.4f}')
    print(classification_report(true_names, pred_names, zero_division=0))

    # Per-domain Macro-F1
    tc = test_df.reset_index(drop=True).copy()
    tc['pred']   = pred_names
    tc['true']   = true_names
    tc['domain'] = (tc['source_file']
                    .str.replace('.csv', '', regex=False)
                    .str.replace('_', ' ').str.title())

    domain_rows = []
    print(f'\n  {"Domain":<45} {"N":>4}  {"Macro-F1":>9}  {"Acc":>6}')
    for domain in sorted(tc['domain'].unique()):
        sub    = tc[tc['domain'] == domain]
        dm_f1  = f1_score(sub['true'], sub['pred'], average='macro', zero_division=0)
        dm_acc = accuracy_score(sub['true'], sub['pred'])
        domain_rows.append({
            'model': model_key, 'task': task_name, 'domain': domain,
            'n': len(sub), 'macro_f1': round(dm_f1, 4), 'accuracy': round(dm_acc, 4)
        })
        print(f'  {domain:<45} {len(sub):>4}  {dm_f1:>9.4f}  {dm_acc:>6.4f}')

    # Confusion matrix
    cm  = confusion_matrix(true_names, pred_names, labels=label_encoder.classes_)
    n   = num_labels
    fig, ax = plt.subplots(figsize=(max(8, n * 0.55), max(6, n * 0.45)))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', linewidths=0.4,
                xticklabels=label_encoder.classes_,
                yticklabels=label_encoder.classes_, ax=ax)
    ax.set_xlabel('Predicted'); ax.set_ylabel('True')
    ax.set_title(f'{task_name} — {model_key}', fontweight='bold')
    plt.xticks(rotation=45, ha='right', fontsize=7)
    plt.yticks(fontsize=7)
    plt.tight_layout(); plt.show(); plt.close(fig)

    del model, trainer, train_ds, dev_ds, test_ds
    torch.cuda.empty_cache()
    gc.collect()

    return {
        'overall': {
            'model': model_key, 'task': task_name,
            'accuracy': round(acc, 4), 'macro_f1': round(mf1, 4),
            'weighted_f1': round(wf1, 4)
        },
        'per_domain': domain_rows
    }


def train_slot_model(model_name, model_key, bio_train, bio_dev, bio_test,
                     tag2id, id2tag, device='cuda', seed=42):
    """
    Fine-tune a token classification model for slot filling.

    Returns:
        dict with 'model', 'task', 'slot_f1'
    """
    print(f'\n{"="*60}\n  Slot Filling | {model_key}\n{"="*60}')

    num_tags  = len(tag2id)
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model     = AutoModelForTokenClassification.from_pretrained(
        model_name, num_labels=num_tags,
        id2label=id2tag, label2id=tag2id,
        ignore_mismatched_sizes=True
    ).to(device)

    train_ds = SlotDataset(bio_train, tokenizer, tag2id)
    dev_ds   = SlotDataset(bio_dev,   tokenizer, tag2id)
    test_ds  = SlotDataset(bio_test,  tokenizer, tag2id)

    def compute_metrics(eval_pred):
        logits, labels = eval_pred
        preds = np.argmax(logits, axis=-1)
        ts, ps = [], []
        for pr, lr in zip(preds, labels):
            t, p = [], []
            for pi, li in zip(pr, lr):
                if li == -100:
                    continue
                t.append(id2tag[li])
                p.append(id2tag[pi])
            ts.append(t); ps.append(p)
        return {'slot_f1': seq_f1(ts, ps, zero_division=0)}

    args = TrainingArguments(
        output_dir                  = f'./results/slot_{model_key}',
        num_train_epochs            = 10,
        per_device_train_batch_size = 32,
        per_device_eval_batch_size  = 64,
        warmup_ratio                = 0.1,
        weight_decay                = 0.01,
        learning_rate               = 2e-5,
        eval_strategy               = 'epoch',
        save_strategy               = 'no',
        load_best_model_at_end      = False,
        logging_steps               = 20,
        seed                        = seed,
        report_to                   = 'none',
        fp16                        = (device == 'cuda'),
    )

    trainer = Trainer(
        model=model, args=args,
        train_dataset=train_ds, eval_dataset=dev_ds,
        compute_metrics=compute_metrics,
        data_collator=DataCollatorForTokenClassification(tokenizer)
    )
    trainer.train()

    preds_out = trainer.predict(test_ds)
    preds     = np.argmax(preds_out.predictions, axis=-1)
    ts, ps    = [], []
    for pr, lr in zip(preds, preds_out.label_ids):
        t, p = [], []
        for pi, li in zip(pr, lr):
            if li == -100:
                continue
            t.append(id2tag[li])
            p.append(id2tag[pi])
        ts.append(t); ps.append(p)

    sf1 = seq_f1(ts, ps, zero_division=0)
    print(f'\n  Slot F1 (seqeval): {sf1:.4f}')
    print(seq_report(ts, ps, zero_division=0))

    del model, trainer, train_ds, dev_ds, test_ds
    torch.cuda.empty_cache()
    gc.collect()

    return {'model': model_key, 'task': 'Slot Filling', 'slot_f1': round(sf1, 4)}
