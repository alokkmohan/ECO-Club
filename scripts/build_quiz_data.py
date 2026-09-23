"""
Regenerate data/quiz.json and the 'quiz' section of data/summary.json from the
Swachhata Hi Seva Quiz workbook, matched against the ECO Club secondary school
master list.

Usage:
    python build_quiz_data.py <path-to-master-data-folder> <path-to-quiz-xlsx>

The master-data folder must contain:
    Secondary School List .xlsx   (sheets: Govt Schools, Aided Schools , UP Board Private School)
The quiz file must be the Swachhata Hi Seva Quiz.xlsx export (sheet: Students).
"""
import pandas as pd
import json, os, sys

if len(sys.argv) < 3:
    print(__doc__)
    sys.exit(1)

BASE = sys.argv[1]
QUIZ_PATH = sys.argv[2]
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
os.makedirs(OUT, exist_ok=True)

def norm_udise(v):
    return str(v).strip().split('.')[0].lstrip('0')

DISTRICT_MAP = {
    'AMBED. NAGAR': 'AMBEDKAR NAGAR', 'AMETHI - CSM NAGAR': 'AMETHI',
    'BULAND.': 'BULANDSHAHR', 'FAIZABAD': 'AYODHYA',
    'G B NAGAR': 'GAUTAM BUDDHA NAGAR', 'HAMIRPUR (U.P.)': 'HAMIRPUR',
    'HAPUR (PANCHSHEEL NAGAR)': 'HAPUR', 'JYOTIBA PHULE NAGAR (AMROHA)': 'AMROHA',
    'KANP. DEHAT': 'KANPUR DEHAT', 'KANP. NAGAR': 'KANPUR NAGAR',
    'KANSHIRAM NAGAR': 'KASGANJ', 'RAE BARELI': 'RAEBARELI',
    'SAMBHAL (BHIM NAGAR)': 'SAMBHAL', 'SANT KABIR NAG.': 'SANT KABIR NAGAR',
    'SHAMLI (PRABUDH NAGAR)': 'SHAMLI', 'BARABANKI': 'BARA BANKI',
    'BHADOI': 'BHADOHI', 'MAHARAJGANJ': 'MAHRAJGANJ', 'SHRAWASTI': 'SHRAVASTI',
}
def norm_dist(v):
    n = str(v).strip().upper()
    return DISTRICT_MAP.get(n, n)

print("Loading quiz data...")
quiz = pd.read_excel(QUIZ_PATH, sheet_name='Students')
quiz['U'] = quiz['UDISE Code'].apply(norm_udise)
quiz['District'] = quiz['District'].apply(norm_dist)

print("Loading school master...")
govt  = pd.read_excel(os.path.join(BASE, 'Secondary School List .xlsx'), sheet_name='Govt Schools')
aided = pd.read_excel(os.path.join(BASE, 'Secondary School List .xlsx'), sheet_name='Aided Schools ')
priv  = pd.read_excel(os.path.join(BASE, 'Secondary School List .xlsx'), sheet_name='UP Board Private School')
priv = priv.rename(columns={c: c.strip() for c in priv.columns})

cat_map = {}
for d, ucol, cat in [(govt, 'UDISE Code', 'G'), (aided, 'UDISE Code', 'A'), (priv, 'Udise Code', 'P')]:
    for u in d[ucol].apply(norm_udise):
        cat_map.setdefault(u, cat)

quiz['Category'] = quiz['U'].map(cat_map)  # G/A/P if matched to our secondary master, else NaN (Basic/other)

# Only Secondary schools (matched to the ECO Club master list) are kept from here on.
quiz = quiz[quiz['Category'].notna()].copy()

by_school = quiz.groupby('U').agg(
    n=('School Name', 'first'),
    d=('District', 'first'),
    p=('Student Name', 'count'),
    pct=('Percent', 'mean'),
).reset_index().rename(columns={'U': 'u'})
by_school['c'] = by_school['u'].map(cat_map)
by_school['pct'] = by_school['pct'].round(1)
by_school = by_school.sort_values('p', ascending=False)

quiz_records = [{
    'u': r.u, 'n': r.n, 'd': r.d, 'c': r.c,
    'p': int(r.p), 'pct': float(r.pct),
} for r in by_school.itertuples(index=False)]

with open(os.path.join(OUT, 'quiz.json'), 'w', encoding='utf-8') as f:
    json.dump(quiz_records, f, ensure_ascii=False, separators=(',', ':'))
print(f"quiz.json: {len(quiz_records):,} secondary school records")

quiz_summary = {
    'totalParticipants': int(len(quiz)),
    'totalSchools': int(quiz['U'].nunique()),
    'govtSchools': int(by_school[by_school['c'] == 'G'].shape[0]),
    'aidedSchools': int(by_school[by_school['c'] == 'A'].shape[0]),
    'privSchools': int(by_school[by_school['c'] == 'P'].shape[0]),
    'avgPercent': round(float(quiz['Percent'].mean()), 1) if len(quiz) else 0,
}

summary_path = os.path.join(OUT, 'summary.json')
with open(summary_path, encoding='utf-8') as f:
    summary = json.load(f)
summary['quiz'] = quiz_summary
with open(summary_path, 'w', encoding='utf-8') as f:
    json.dump(summary, f, ensure_ascii=False, separators=(',', ':'))
print("summary.json updated with 'quiz' section")
print(quiz_summary)
