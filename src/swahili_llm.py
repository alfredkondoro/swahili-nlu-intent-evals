"""Zero-shot LLM evaluation utilities for SwahiliNLU."""
import json
import re
from sklearn.metrics import accuracy_score, f1_score


def make_system_prompt(intent_list, tone_list):
    """Build the structured JSON output prompt for LLM evaluation."""
    return (
        'You are an NLU classifier for a Swahili virtual assistant.\n'
        'Given a Swahili utterance, output ONLY a valid JSON object with two keys:\n'
        f'  - "intent": one of {intent_list}\n'
        f'  - "tone": one of {tone_list}\n'
        'Do not include any explanation. Output only the JSON object.'
    )


def _parse_response(text):
    """Strip markdown fences and parse JSON response."""
    raw  = re.sub(r'```json|```', '', text).strip()
    data = json.loads(raw)
    return data.get('intent', 'unknown'), data.get('tone', 'unknown')


def predict_claude(client, utterance, system_prompt):
    """Zero-shot prediction using Claude Sonnet."""
    try:
        msg = client.messages.create(
            model='claude-sonnet-4-5', max_tokens=100,
            system=system_prompt,
            messages=[{'role': 'user', 'content': utterance}]
        )
        return _parse_response(msg.content[0].text)
    except Exception as e:
        print(f'  ⚠ Claude: {e}')
        return 'unknown', 'unknown'


def predict_gpt(client, utterance, system_prompt):
    """Zero-shot prediction using GPT-4o mini."""
    try:
        resp = client.chat.completions.create(
            model='gpt-4o-mini', max_tokens=100,
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user',   'content': utterance}
            ]
        )
        return _parse_response(resp.choices[0].message.content)
    except Exception as e:
        print(f'  ⚠ GPT: {e}')
        return 'unknown', 'unknown'


def predict_gemini(model, utterance, system_prompt):
    """Zero-shot prediction using Gemini 2.5 Flash."""
    try:
        resp = model.generate_content(f'{system_prompt}\n\nUtterance: {utterance}')
        return _parse_response(resp.text)
    except Exception as e:
        print(f'  ⚠ Gemini: {e}')
        return 'unknown', 'unknown'


def run_llm_evaluation(llm_registry, test_df, intent_list, tone_list,
                       n_samples=100, seed=42):
    """
    Run zero-shot evaluation for all LLMs in the registry.

    Args:
        llm_registry: dict of {model_name: predict_fn(utterance) -> (intent, tone)}
        test_df:      test split DataFrame
        intent_list:  list of valid intent labels
        tone_list:    list of valid tone labels
        n_samples:    number of test samples to evaluate
        seed:         random seed for sampling

    Returns:
        list of result dicts (one per model per task)
    """
    sample = (test_df
              .sample(n=min(n_samples, len(test_df)), random_state=seed)
              .reset_index(drop=True))
    true_intents = sample['intent'].tolist()
    true_tones   = sample['tone'].tolist()
    results      = []

    for model_name, predict_fn in llm_registry.items():
        print(f'\n{"="*55}\n  {model_name}\n{"="*55}')
        pi_list, pt_list = [], []
        for i, row in sample.iterrows():
            pi, pt = predict_fn(row['utterance'])
            pi_list.append(pi)
            pt_list.append(pt)
            if (i + 1) % 20 == 0:
                print(f'  {i + 1}/{len(sample)} done...')

        i_acc = accuracy_score(true_intents, pi_list)
        i_f1  = f1_score(true_intents, pi_list, average='macro',
                         zero_division=0, labels=intent_list)
        t_acc = accuracy_score(true_tones, pt_list)
        t_f1  = f1_score(true_tones, pt_list, average='macro',
                         zero_division=0, labels=tone_list)

        print(f'  Intent  Acc {i_acc:.4f} | Macro-F1 {i_f1:.4f}')
        print(f'  Tone    Acc {t_acc:.4f} | Macro-F1 {t_f1:.4f}')

        results.extend([
            {'model': model_name, 'task': 'Intent',
             'accuracy': round(i_acc, 4), 'macro_f1': round(i_f1, 4), 'weighted_f1': '—'},
            {'model': model_name, 'task': 'Tone',
             'accuracy': round(t_acc, 4), 'macro_f1': round(t_f1, 4), 'weighted_f1': '—'},
        ])

    return results
