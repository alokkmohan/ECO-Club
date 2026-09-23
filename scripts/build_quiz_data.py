"""
Regenerate data/quiz.json and the 'quiz' section of data/summary.json from
the Swachhata Hi Seva School Activity Report workbook, matched against the
ECO Club secondary school master list. Every Secondary school
(Government/Aided/Private) is included, whether or not it submitted a
report, so the report can show both Participated and Not Participated
schools (like Notification/Plantation/E-Waste).

NOTE: this replaced the old per-student quiz-score export (sheet 'Students',
with Score/Percent/Badge columns). The current source is a school-level
self-reported activity checklist (sheet 'School reports') covering things
like four-bin waste segregation, awareness activities, waste audits,
composting and exposure visits, plus Students/Teachers/Community Members
Participated counts. There is no score/percent anymore.

Usage:
    python build_quiz_data.py <path-to-master-data-folder> <path-to-swachhata-xlsx>

The master-data folder must contain:
    Secondary School List .xlsx   (sheets: Govt Schools, Aided Schools , UP Board Private School)
The source file must be the SwachhataHiSeva_SchoolReports_*.xlsx export (sheet: School reports).
"""
import pandas as pd
import json, re, os, sys

if len(sys.argv) < 3:
    print(__doc__)
    sys.exit(1)

BASE = sys.argv[1]
SWACHHATA_PATH = sys.argv[2]
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

print("Loading Swachhata Hi Seva school activity data...")
sw = pd.read_excel(SWACHHATA_PATH, sheet_name='School reports')
sw['U'] = sw['UDISE Code'].apply(norm_udise)

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

sw_by_udise = sw.drop_duplicates(subset='U', keep='first').set_index('U')
students_by_udise = sw_by_udise['Q4 Students Participated'].to_dict()
teachers_by_udise = sw_by_udise['Q5 Teachers Participated'].to_dict()
community_by_udise = sw_by_udise['Q6 Community Members Participated'].to_dict()
bins_by_udise = (sw_by_udise['Q1 Four Bins Installed'] == 'Yes, all four installed').to_dict()
audit_by_udise = (sw_by_udise['Q7 Solid Waste Audit'] == 'Yes').to_dict()

pool['st'] = pool['UDISE_norm'].map(students_by_udise).fillna(0).astype(int)
pool['tc'] = pool['UDISE_norm'].map(teachers_by_udise).fillna(0).astype(int)
pool['cm'] = pool['UDISE_norm'].map(community_by_udise).fillna(0).astype(int)
pool['p'] = pool['st'] + pool['tc'] + pool['cm']
pool['bins'] = pool['UDISE_norm'].map(bins_by_udise).fillna(False).astype(int)
pool['audit'] = pool['UDISE_norm'].map(audit_by_udise).fillna(False).astype(int)
pool['s'] = pool['UDISE_norm'].isin(set(sw['U'])).astype(int)

quiz_records = [{
    'd': r.District, 'c': r.Category, 'n': r._1, 'u': r.UDISE_norm,
    's': int(r.s), 'st': int(r.st), 'tc': int(r.tc), 'cm': int(r.cm), 'p': int(r.p),
    'bins': int(r.bins), 'audit': int(r.audit),
} for r in pool.itertuples(index=False)]

with open(os.path.join(OUT, 'quiz.json'), 'w', encoding='utf-8') as f:
    json.dump(quiz_records, f, ensure_ascii=False, separators=(',', ':'))
print(f"quiz.json: {len(quiz_records):,} secondary school records")

participated = pool[pool['s'] == 1]
quiz_summary = {
    'totalSchools': int(len(pool)),
    'participatedSchools': int(len(participated)),
    'notParticipatedSchools': int(len(pool) - len(participated)),
    'totalParticipants': int(participated['p'].sum()),
    'totalStudents': int(participated['st'].sum()),
    'totalTeachers': int(participated['tc'].sum()),
    'totalCommunity': int(participated['cm'].sum()),
    'binsInstalledSchools': int(participated['bins'].sum()),
    'wasteAuditSchools': int(participated['audit'].sum()),
    'govtSchools': int((participated['Category'] == 'G').sum()),
    'aidedSchools': int((participated['Category'] == 'A').sum()),
    'privSchools': int((participated['Category'] == 'P').sum()),
}

summary_path = os.path.join(OUT, 'summary.json')
with open(summary_path, encoding='utf-8') as f:
    summary = json.load(f)
summary['quiz'] = quiz_summary
with open(summary_path, 'w', encoding='utf-8') as f:
    json.dump(summary, f, ensure_ascii=False, separators=(',', ':'))
print("summary.json updated with 'quiz' section")
print(quiz_summary)
