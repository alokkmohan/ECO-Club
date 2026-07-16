"""
Regenerate data/*.json from the ECO Club master workbook.

Usage:
    python build_site_data.py <path-to-master-data-folder>

The source folder must contain:
    Secondary School List .xlsx        (sheets: Govt Schools, Aided Schools , UP Board Private School)
    All_Schools_with_Notifications_UTTAR PRADESH.xlsx
    Eco_Clubs_plantation_Uttar_Pradesh_all_schools.xlsx  (sheet: Schools)
    block.xlsx                         (sheet: Enrolment Details - Class Wise , columns: District Name, Block Name, School Name, UDISE Code)
"""
import pandas as pd
import json, re, os, sys

if len(sys.argv) < 2:
    print(__doc__)
    sys.exit(1)

BASE = sys.argv[1]
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

print("Loading source data...")
notif = pd.read_excel(os.path.join(BASE, 'All_Schools_with_Notifications_UTTAR PRADESH.xlsx'))
plant = pd.read_excel(os.path.join(BASE, 'Eco_Clubs_plantation_Uttar_Pradesh_all_schools.xlsx'), sheet_name='Schools')
govt  = pd.read_excel(os.path.join(BASE, 'Secondary School List .xlsx'), sheet_name='Govt Schools')
aided = pd.read_excel(os.path.join(BASE, 'Secondary School List .xlsx'), sheet_name='Aided Schools ')
priv  = pd.read_excel(os.path.join(BASE, 'Secondary School List .xlsx'), sheet_name='UP Board Private School')
block = pd.read_excel(os.path.join(BASE, 'block.xlsx'), sheet_name='Enrolment Details - Class Wise ')

notif['U'] = notif['UDISE ID'].apply(norm_udise)
uploaded_udise = set(notif['U'])

plant['U'] = plant['UDISE'].apply(norm_udise)
done_udise = set(plant['U'])
trees_by_udise = plant.groupby('U')['Trees Planted'].sum().to_dict()

block['U'] = block['UDISE Code'].apply(norm_udise)
block_by_udise = block.drop_duplicates(subset='U', keep='first').set_index('U')['Block Name']

def build_pool(govt, aided, priv):
    pg = govt[['District Name', 'School Name', 'UDISE Code']].copy()
    pg['District'] = pg['District Name'].apply(norm_dist)
    pg['UDISE_norm'] = pg['UDISE Code'].apply(norm_udise)
    pg['Category'] = 'G'

    pa = aided[['District Name', 'School Name', 'UDISE Code']].copy()
    pa['District'] = pa['District Name'].apply(norm_dist)
    pa['UDISE_norm'] = pa['UDISE Code'].apply(norm_udise)
    pa['Category'] = 'A'

    priv2 = priv.rename(columns={c: c.strip() for c in priv.columns})
    pp = priv2[['District Name', 'School Name', 'Udise Code']].copy()
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
    pool['Block'] = pool['UDISE_norm'].map(block_by_udise).fillna('')
    return pool

full_pool = build_pool(govt, aided, priv)
print(f"Full pool (Govt+Aided+Private, madarsa excluded): {len(full_pool):,}")

notif_pool = full_pool.copy()
notif_pool['status'] = notif_pool['UDISE_norm'].isin(uploaded_udise).astype(int)

notif_records = [{
    'd': r.District, 'b': r.Block, 'c': r.Category,
    'n': r._1, 'u': r.UDISE_norm, 's': r.status,
} for r in notif_pool.itertuples(index=False)]

with open(os.path.join(OUT, 'notification.json'), 'w', encoding='utf-8') as f:
    json.dump(notif_records, f, ensure_ascii=False, separators=(',', ':'))
print(f"notification.json: {len(notif_records):,} records")

plant_pool = full_pool[full_pool['Category'].isin(['G', 'A'])].copy()
plant_pool['status'] = plant_pool['UDISE_norm'].isin(done_udise).astype(int)
plant_pool['trees'] = plant_pool['UDISE_norm'].map(trees_by_udise).fillna(0).astype(int)

plant_records = [{
    'd': r.District, 'b': r.Block, 'c': r.Category,
    'n': r._1, 'u': r.UDISE_norm, 's': r.status, 't': r.trees,
} for r in plant_pool.itertuples(index=False)]

with open(os.path.join(OUT, 'plantation.json'), 'w', encoding='utf-8') as f:
    json.dump(plant_records, f, ensure_ascii=False, separators=(',', ':'))
print(f"plantation.json: {len(plant_records):,} records")

def agg_district(pool, is_plant):
    rows = []
    for dist, grp in pool.groupby('District'):
        is_g = grp['Category'].eq('G')
        is_a = grp['Category'].eq('A')
        is_p = grp['Category'].eq('P')
        s = grp['status']
        row = {
            'district': dist,
            'govtTotal': int(is_g.sum()), 'govtDone': int((is_g & (s == 1)).sum()),
            'aidedTotal': int(is_a.sum()), 'aidedDone': int((is_a & (s == 1)).sum()),
        }
        if not is_plant:
            row['privTotal'] = int(is_p.sum())
            row['privDone'] = int((is_p & (s == 1)).sum())
        else:
            row['treesPlanted'] = int(grp['trees'].sum())
        rows.append(row)
    return sorted(rows, key=lambda r: r['district'])

summary = {
    'generated': pd.Timestamp.now().strftime('%d %b %Y, %I:%M %p'),
    'notification': {
        'totalSchools': len(notif_pool),
        'uploaded': int(notif_pool['status'].sum()),
        'pending': int((notif_pool['status'] == 0).sum()),
        'govtTotal': int(notif_pool['Category'].eq('G').sum()),
        'govtDone': int((notif_pool['Category'].eq('G') & (notif_pool['status']==1)).sum()),
        'aidedTotal': int(notif_pool['Category'].eq('A').sum()),
        'aidedDone': int((notif_pool['Category'].eq('A') & (notif_pool['status']==1)).sum()),
        'privTotal': int(notif_pool['Category'].eq('P').sum()),
        'privDone': int((notif_pool['Category'].eq('P') & (notif_pool['status']==1)).sum()),
        'byDistrict': agg_district(notif_pool, is_plant=False),
    },
    'plantation': {
        'totalSchools': len(plant_pool),
        'done': int(plant_pool['status'].sum()),
        'pending': int((plant_pool['status'] == 0).sum()),
        'treesPlanted': int(plant_pool['trees'].sum()),
        'govtTotal': int(plant_pool['Category'].eq('G').sum()),
        'govtDone': int((plant_pool['Category'].eq('G') & (plant_pool['status']==1)).sum()),
        'aidedTotal': int(plant_pool['Category'].eq('A').sum()),
        'aidedDone': int((plant_pool['Category'].eq('A') & (plant_pool['status']==1)).sum()),
        'byDistrict': agg_district(plant_pool, is_plant=True),
    },
}

with open(os.path.join(OUT, 'summary.json'), 'w', encoding='utf-8') as f:
    json.dump(summary, f, ensure_ascii=False, separators=(',', ':'))
print("summary.json written")
