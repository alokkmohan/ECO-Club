"""
Regenerate data/quiz.json and the 'quiz' section of data/summary.json from the
Swachhata Hi Seva Quiz workbook, matched against the ECO Club secondary school
master list. Every Secondary school (Government/Aided/Private) is included,
whether or not it participated, so the report can show both Participated and
Not Participated schools (like the Notification and Plantation reports).

Usage:
    python build_quiz_data.py <path-to-master-data-folder> <path-to-quiz-xlsx>

The master-data folder must contain:
    Secondary School List .xlsx   (sheets: Govt Schools, Aided Schools , UP Board Private School)
The quiz file must be the Swachhata Hi Seva Quiz.xlsx export (sheet: Students).
"""
import pandas as pd
import json, re, os, sys

if len(sys.argv) < 3:
    print(__doc__)
    sys.exit(1)

BASE = sys.argv[1]
QUIZ_PATH = sys.argv[2]
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
os.makedirs(OUT, exist_ok=True)

def norm_udise(v):
    return str(v).strip().split('.')[0].lstrip('0')

MADARSA_RE = re.compile(r'\b(?:MADARSA|MADARASA|MADARSHA|MADRASA|MADRSA|MADRSHA)\b')

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

print("Loading school master...")
govt  = pd.read_excel(os.path.join(BASE, 'Secondary School List .xlsx'), sheet_name='Govt Schools')
aided = pd.read_excel(os.path.join(BASE, 'Secondary School List .xlsx'), sheet_name='Aided Schools ')
priv  = pd.read_excel(os.path.join(BASE, 'Secondary School List .xlsx'), sheet_name='UP Board Private School')
priv = priv.rename(columns={c: c.strip() for c in priv.columns})

def build_pool(govt, aided, priv):
    pg = govt[['District Name', 'School Name', 'UDISE Code']].copy()
    pg['District'] = pg['District Name'].apply(norm_dist)
    pg['UDISE_norm'] = pg['UDISE Code'].apply(norm_udise)
    pg['Category'] = 'G'

    pa = aided[['District Name', 'School Name', 'UDISE Code']].copy()
    pa['District'] = pa['District Name'].apply(norm_dist)
    pa['UDISE_norm'] = pa['UDISE Code'].apply(norm_udise)
    pa['Category'] = 'A'

    pp = priv[['District Name', 'School Name', 'Udise Code']].copy()
    pp['District'] = pp['District Name'].apply(norm_dist)
    pp['UDISE_norm'] = pp['Udise Code'].apply(norm_udise)
    pp['Category'] = 'P'

    pool = pd.concat([
        pg[['District', 'School Name', 'UDISE_norm', 'Category']],
        pa[['District', 'School Name', 'UDISE_norm', 'Category']],
        pp[['District', 'School Name', 'UDISE_norm', 'Category']],
    ], ignore_index=True)
    pool['School Name'] = pool['School Name'].astype(str).str.strip()
    pool = pool.drop_duplicates(subset='UDISE_norm', keep='first')
    madarsa_mask = pool['School Name'].str.upper().str.contains(MADARSA_RE)
    pool = pool[~madarsa_mask].reset_index(drop=True)
    return pool

pool = build_pool(govt, aided, priv)
print(f"Secondary school pool (Govt+Aided+Private, madarsa excluded): {len(pool):,}")

by_school = quiz.groupby('U').agg(
    p=('Student Name', 'count'),
    pct=('Percent', 'mean'),
).reset_index().rename(columns={'U': 'UDISE_norm'})
by_school['pct'] = by_school['pct'].round(1)
participants_by_udise = by_school.set_index('UDISE_norm')['p'].to_dict()
pct_by_udise = by_school.set_index('UDISE_norm')['pct'].to_dict()

pool['p'] = pool['UDISE_norm'].map(participants_by_udise).fillna(0).astype(int)
pool['pct'] = pool['UDISE_norm'].map(pct_by_udise).fillna(0).astype(float)
pool['s'] = (pool['p'] > 0).astype(int)

quiz_records = [{
    'd': r.District, 'c': r.Category, 'n': r._1, 'u': r.UDISE_norm,
    's': int(r.s), 'p': int(r.p), 'pct': float(r.pct),
} for r in pool.itertuples(index=False)]

with open(os.path.join(OUT, 'quiz.json'), 'w', encoding='utf-8') as f:
    json.dump(quiz_records, f, ensure_ascii=False, separators=(',', ':'))
print(f"quiz.json: {len(quiz_records):,} secondary school records")

participated = pool[pool['s'] == 1]
secondary_udise = set(pool['UDISE_norm'])
quiz_secondary_students = quiz[quiz['U'].isin(secondary_udise)]
quiz_summary = {
    'totalSchools': int(len(pool)),
    'participatedSchools': int(len(participated)),
    'notParticipatedSchools': int(len(pool) - len(participated)),
    'totalParticipants': int(participated['p'].sum()),
    'govtSchools': int((participated['Category'] == 'G').sum()),
    'aidedSchools': int((participated['Category'] == 'A').sum()),
    'privSchools': int((participated['Category'] == 'P').sum()),
    'avgPercent': round(float(quiz_secondary_students['Percent'].mean()), 1) if len(quiz_secondary_students) else 0,
}

summary_path = os.path.join(OUT, 'summary.json')
with open(summary_path, encoding='utf-8') as f:
    summary = json.load(f)
summary['quiz'] = quiz_summary
with open(summary_path, 'w', encoding='utf-8') as f:
    json.dump(summary, f, ensure_ascii=False, separators=(',', ':'))
print("summary.json updated with 'quiz' section")
print(quiz_summary)
