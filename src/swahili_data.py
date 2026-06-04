"""Data loading and cleaning utilities for SwahiliNLU."""
import json
import glob
import re
from pathlib import Path
import pandas as pd

VALID_TONES = {'imperative', 'polite', 'conversational'}


def _extract_tone(slots_str):
    try:
        d = json.loads(str(slots_str))
        return d.get('tone', None)
    except:
        return None


def _clean_slots(slots_str):
    for attempt in [str(slots_str), str(slots_str).replace('""', '"')]:
        try:
            d = json.loads(attempt)
            d.pop('tone', None)
            return json.dumps(d)
        except:
            pass
    return str(slots_str)


def parse_line(line):
    """Parse one CSV data line — handles plain and double-escaped JSON."""
    line = line.strip().rstrip(',')
    if not line:
        return None

    js = line.find('{')
    je = line.rfind('}')

    if js == -1:
        parts = line.split(',', 2)
        if len(parts) < 2:
            return None
        return {
            'intent': parts[0].strip(),
            'utterance': parts[1].strip(),
            'slots': '',
            'tone': parts[2].strip() if len(parts) > 2 else None
        }

    before     = line[:js]
    slots_json = line[js:je + 1]
    after      = line[je + 1:].strip().strip('"').strip(',').strip()
    parts      = [p.strip().strip('"') for p in before.rstrip(',"').split(',', 1)]

    if len(parts) < 2:
        return None

    slots_fixed = slots_json.replace('""', '"')

    # Extract tone: Label column → JSON → regex
    tone = None
    if after and after.lower() in VALID_TONES:
        tone = after.lower()

    if not tone:
        for attempt in [slots_fixed, slots_json]:
            try:
                d = json.loads(attempt)
                if d.get('tone'):
                    tone = d['tone']
                    break
            except:
                pass

    if not tone:
        m = re.search(r'"tone"\s*:\s*"([a-z]+)"', slots_json, re.I)
        if m and m.group(1).lower() in VALID_TONES:
            tone = m.group(1).lower()

    # Clean slots — remove tone key
    slots_clean = '{}'
    for attempt in [slots_fixed, slots_json]:
        try:
            d = json.loads(attempt)
            d.pop('tone', None)
            slots_clean = json.dumps(d)
            break
        except:
            pass

    return {
        'intent': parts[0].strip(),
        'utterance': parts[1].strip(),
        'slots': slots_clean,
        'tone': tone
    }


def load_file(f):
    """Load one domain CSV — returns a DataFrame."""
    fname = Path(f).name
    rows  = []
    with open(f, 'r', encoding='utf-8-sig') as fh:
        lines = fh.readlines()
    for line in lines[1:]:
        parsed = parse_line(line)
        if parsed:
            parsed['source_file'] = fname
            rows.append(parsed)
    return pd.DataFrame(rows) if rows else pd.DataFrame()


def load_dataset(data_dir):
    """Load and clean all domain CSVs. Returns a clean DataFrame."""
    csv_files = sorted(glob.glob(f'{data_dir}/*.csv'))
    frames    = [load_file(f) for f in csv_files]
    df        = pd.concat([fr for fr in frames if len(fr) > 0], ignore_index=True)

    df['tone']      = df['tone'].astype(str).str.strip().str.lower().str.replace('"', '', regex=False)
    df['slots']     = df['slots'].astype(str).str.strip()
    df['utterance'] = df['utterance'].astype(str).str.strip().str.strip(',"')

    before = len(df)
    df = df[df['tone'].isin(VALID_TONES)]
    df = df.dropna(subset=['intent', 'utterance'])
    df = df[df['utterance'].str.strip() != '']
    df = df.reset_index(drop=True)

    print(f'Loaded {len(df):,} rows from {df["source_file"].nunique()} domains '
          f'(dropped {before - len(df)} invalid rows)')
    return df
