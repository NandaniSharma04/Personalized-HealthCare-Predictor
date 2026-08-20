import pandas as pd
import numpy as np
from pathlib import Path

csv_path = Path(r"c:\Users\G SAI SHARANYA\OneDrive\Desktop\Personalized-HealthCare-Predictor-main\data\raw_dataset\Diseases_and_Symptoms_dataset.csv")

df = pd.read_csv(csv_path)

print("="*60)
print("1. DATASET OVERVIEW")
print("="*60)
print(f"Dataset File: {csv_path.name}")
print(f"Total Rows: {len(df)}")
print(f"Total Columns: {len(df.columns)}")

# Target column identification
target_col = [c for c in df.columns if c.lower() in ['diseases', 'disease', 'target', 'label', 'prognosis']][0]
print(f"Target Column Name: '{target_col}'")

symptom_cols = [c for c in df.columns if c != target_col]
print(f"Total Symptom Columns: {len(symptom_cols)}")

unique_diseases = df[target_col].value_counts()
print(f"Total Unique Diseases: {len(unique_diseases)}")

print("\nTop 15 Diseases by Sample Count:")
print(unique_diseases.head(15))
print("\nBottom 10 Diseases by Sample Count:")
print(unique_diseases.tail(10))

print("\nMissing Values:")
print(f"Total NaN in Dataset: {df.isna().sum().sum()}")

duplicates = df.duplicated().sum()
print(f"Duplicate Rows Count: {duplicates}")

print("\n" + "="*60)
print("2. VERIFY DATASET RELATIONSHIP FOR EXAMPLE SYMPTOMS")
print("Symptoms: ['fever', 'chills', 'sweating', 'headache']")
print("="*60)

# Clean column names for search
col_clean_map = {c: c.strip().lower().replace('_', ' ') for c in symptom_cols}

target_syms = ['fever', 'chills', 'sweating', 'headache']
matched_cols = []

for target in target_syms:
    found = [orig for orig, cl in col_clean_map.items() if cl == target or target in cl]
    print(f"Target '{target}' -> Matched Columns in Dataset: {found}")
    matched_cols.extend(found)

if matched_cols:
    # Filter dataset rows where ALL matched symptoms are 1
    cond = pd.Series(True, index=df.index)
    for col in matched_cols:
        cond = cond & (df[col] == 1)
    
    matching_rows = df[cond]
    print(f"\nNumber of matching records in Dataset for ALL {target_syms}: {len(matching_rows)}")
    if len(matching_rows) > 0:
        print("Disease distribution for matching records:")
        print(matching_rows[target_col].value_counts())
    else:
        print("No exact row has ALL 4 set to 1. Checking rows with subset of symptoms:")
        # Check matching 3 or more
        sub_df = df[matched_cols]
        sub_sum = sub_df.sum(axis=1)
        sub_matching = df[sub_sum >= 3]
        print(f"Number of records with at least 3 of {target_syms}: {len(sub_matching)}")
        if len(sub_matching) > 0:
            print("Disease distribution for >= 3 matching symptoms:")
            print(sub_matching[target_col].value_counts())
