import csv
import json
import os
import sys
from collections import Counter, defaultdict

def analyze_csv(path, max_unique_vals=50):
    res = {}
    res['file'] = path
    res['format'] = 'csv'
    with open(path, encoding='utf-8', errors='replace') as f:
        reader = csv.reader(f)
        try:
            header = next(reader)
        except StopIteration:
            return {'file': path, 'error': 'empty'}
        res['columns'] = header
        n_cols = len(header)
        row_count = 0
        col_types = [Counter() for _ in range(n_cols)]
        missing = [0]*n_cols
        uniques = [set() for _ in range(n_cols)]
        dup_counter = Counter()
        for row in reader:
            row_count += 1
            # normalize row length
            if len(row) < n_cols:
                row += ['']*(n_cols-len(row))
            for i, v in enumerate(row[:n_cols]):
                if v is None or v.strip() == '':
                    missing[i] += 1
                    col_types[i]['blank'] += 1
                else:
                    # detect numeric
                    try:
                        float(v)
                        col_types[i]['numeric'] += 1
                    except Exception:
                        col_types[i]['text'] += 1
                    if len(uniques[i]) <= max_unique_vals:
                        uniques[i].add(v)
            dup_counter[tuple(row[:n_cols])] += 1
        res['n_rows'] = row_count
        res['n_columns'] = n_cols
        res['missing_values'] = {header[i]: missing[i] for i in range(n_cols)}
        res['duplicate_rows'] = sum(1 for c in dup_counter.values() if c>1)
        res['column_types'] = {header[i]: dict(col_types[i]) for i in range(n_cols)}
        res['unique_values_sample'] = {header[i]: list(uniques[i]) for i in range(n_cols)}
    return res

def analyze_json(path):
    res = {'file': path, 'format': 'json'}
    try:
        with open(path, encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        return {'file': path, 'error': str(e)}
    if isinstance(data, list):
        res['n_rows'] = len(data)
        # keys union
        keys = set()
        for obj in data:
            if isinstance(obj, dict):
                keys.update(obj.keys())
        res['columns'] = list(keys)
    elif isinstance(data, dict):
        res['type'] = 'object'
        res['keys'] = list(data.keys())
    return res

def main(paths):
    report = []
    for p in paths:
        if not os.path.exists(p):
            report.append({'file': p, 'error': 'not found'})
            continue
        if p.lower().endswith('.csv'):
            report.append(analyze_csv(p))
        elif p.lower().endswith('.json'):
            report.append(analyze_json(p))
        else:
            report.append({'file': p, 'error': 'unsupported format'})
    out = {'report_for': len(report), 'files': report}
    print(json.dumps(out, indent=2))

if __name__ == '__main__':
    if len(sys.argv) > 1:
        paths = sys.argv[1:]
    else:
        # default: common dataset files in repository
        base = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw_dataset')
        base = os.path.abspath(base)
        paths = [os.path.join(base, f) for f in os.listdir(base) if f.lower().endswith('.csv')]
        # include data/users.json if exists
        users = os.path.join(os.path.dirname(__file__), '..', 'data', 'users.json')
        users = os.path.abspath(users)
        if os.path.exists(users):
            paths.append(users)
        # include ml jsons
        ml_dir = os.path.join(os.path.dirname(__file__), '..', 'backend', 'ml')
        ml_dir = os.path.abspath(ml_dir)
        if os.path.isdir(ml_dir):
            for f in os.listdir(ml_dir):
                if f.lower().endswith('.json'):
                    paths.append(os.path.join(ml_dir, f))
    main(paths)
