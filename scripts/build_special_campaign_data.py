"""
Regenerate data/special-campaign.json and the 'specialCampaign' section of
data/summary.json from the Special Campaign 6 E-Waste School Reports
workbook, matched against the ECO Club secondary school master list.

This is a SEPARATE campaign from the main E-Waste Collection drive
(build_ewaste_data.py / data/ewaste.json) — a different, standalone data
source, not a newer export of the same one. Every Secondary school
(Government/Aided/Private) is included, whether or not it reported an
activity, so the report can show both Participated and Not Participated
schools (like Notification/Plantation/Quiz/E-Waste).

Usage:
    python build_special_campaign_data.py <path-to-master-data-folder> <path-to-campaign-xlsx>

The master-data folder must contain:
    Secondary School List .xlsx   (sheets: Govt Schools, Aided Schools , UP Board Private School)
The campaign file must be the Special_Campaign_*_EWaste_SchoolReports_*.xlsx
export (same column layout as the main E-Waste report: UDISE Code, Total
Participants, Total Items, Workshops, ...).
"""
import pandas as pd
import json, re, os, sys

if len(sys.argv) < 3:
    print(__doc__)
    sys.exit(1)

BASE = sys.argv[1]
CAMPAIGN_PATH = sys.argv[2]
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

print("Loading Special Campaign data...")
xl = pd.ExcelFile(CAMPAIGN_PATH)
sheet = next((s for s in xl.sheet_names if s.strip().lower() == 'e-waste reports'), xl.sheet_names[0])
camp = pd.read_excel(xl, sheet_name=sheet)
camp['U'] = camp['UDISE Code'].apply(norm_udise)

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

camp_by_udise = camp.drop_duplicates(subset='U', keep='first').set_index('U')
participants_by_udise = camp_by_udise['Total Participants'].to_dict()
items_by_udise = camp_by_udise['Total Items'].to_dict()
workshops_by_udise = camp_by_udise['Workshops'].to_dict()

pool['p'] = pool['UDISE_norm'].map(participants_by_udise).fillna(0).astype(int)
pool['items'] = pool['UDISE_norm'].map(items_by_udise).fillna(0).astype(int)
pool['w'] = pool['UDISE_norm'].map(workshops_by_udise).fillna(0).astype(int)
pool['s'] = pool['UDISE_norm'].isin(set(camp['U'])).astype(int)

campaign_records = [{
    'd': r.District, 'c': r.Category, 'n': r._1, 'u': r.UDISE_norm,
    's': int(r.s), 'p': int(r.p), 'items': int(r.items), 'w': int(r.w),
} for r in pool.itertuples(index=False)]

with open(os.path.join(OUT, 'special-campaign.json'), 'w', encoding='utf-8') as f:
    json.dump(campaign_records, f, ensure_ascii=False, separators=(',', ':'))
print(f"special-campaign.json: {len(campaign_records):,} secondary school records")

participated = pool[pool['s'] == 1]
campaign_summary = {
    'totalSchools': int(len(pool)),
    'participatedSchools': int(len(participated)),
    'notParticipatedSchools': int(len(pool) - len(participated)),
    'totalParticipants': int(participated['p'].sum()),
    'totalItemsCollected': int(participated['items'].sum()),
    'totalWorkshops': int(participated['w'].sum()),
    'govtSchools': int((participated['Category'] == 'G').sum()),
    'aidedSchools': int((participated['Category'] == 'A').sum()),
    'privSchools': int((participated['Category'] == 'P').sum()),
}

summary_path = os.path.join(OUT, 'summary.json')
with open(summary_path, encoding='utf-8') as f:
    summary = json.load(f)
summary['specialCampaign'] = campaign_summary
with open(summary_path, 'w', encoding='utf-8') as f:
    json.dump(summary, f, ensure_ascii=False, separators=(',', ':'))
print("summary.json updated with 'specialCampaign' section")
print(campaign_summary)
