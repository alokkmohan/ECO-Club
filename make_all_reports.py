# -*- coding: utf-8 -*-
"""
Unified Reports Generator (UDISE-based, Excel-only)
"""

import re
import pandas as pd
from pathlib import Path

# ================= BASE DIRECTORY =================
BASE_DIR = Path("/home/alok-mohan/Documents/Naukri /Eco club")

# ------------- INPUT FILES -------------
MASTER_XLSX = BASE_DIR / "School Master.xlsx"
NOTIF_XLSX  = BASE_DIR / "Notifications.xlsx"
TREE_XLSX   = BASE_DIR / "Tree Sampled Report.xlsx"

# ------------- OUTPUT FILES -------------
OUT_NONNOT_XLSX          = BASE_DIR / "NonNotifiers_AllTypes.xlsx"
OUT_TREE_XLSX            = BASE_DIR / "Tree_WithMgmtCategory.xlsx"
OUT_NONPLANT_XLSX        = BASE_DIR / "NonPlanters_AllTypes.xlsx"
OUT_NOTIF_WITH_META_XLSX = BASE_DIR / "Notifications_WithMgmtCategory.xlsx"
OUT_ALL_CONSOLIDATED     = BASE_DIR / "All_Reports_Consolidated.xlsx"

# ---------- helpers ----------
def normalize_udise_series(s: pd.Series, width: int = 11) -> pd.Series:
    s = s.astype(str).str.strip()
    s = s.str.replace(r"\.0$", "", regex=True)
    s = s.apply(lambda x: re.sub(r"\D", "", x))
    s = s.apply(lambda x: x.zfill(width) if x else x)
    return s

def find_udise_col(df: pd.DataFrame) -> str:
    for col in df.columns:
        name = str(col).lower()
        if "udise" in name and ("code" in name or "id" in name):
            return col
    for col in ("UDISE Code", "UDISE ID"):
        if col in df.columns:
            return col
    raise KeyError("UDISE column not found")

def trim_spaces(df: pd.DataFrame) -> pd.DataFrame:
    for c in df.columns:
        if pd.api.types.is_object_dtype(df[c]):
            df[c] = df[c].astype(str).str.strip()
    return df

# ---------- load ----------
master = pd.read_excel(MASTER_XLSX, engine="openpyxl", dtype=str)
notif  = pd.read_excel(NOTIF_XLSX,  engine="openpyxl", dtype=str)
tree   = pd.read_excel(TREE_XLSX,   engine="openpyxl", dtype=str)

master = trim_spaces(master)
notif  = trim_spaces(notif)
tree   = trim_spaces(tree)

for col in ["School Management", "School Category"]:
    if col not in master.columns:
        raise KeyError(f"Master missing column: {col}")

master_udise_col = find_udise_col(master)
notif_udise_col  = find_udise_col(notif)
tree_udise_col   = find_udise_col(tree)

master[master_udise_col] = normalize_udise_series(master[master_udise_col])
notif[notif_udise_col]   = normalize_udise_series(notif[notif_udise_col])
tree[tree_udise_col]     = normalize_udise_series(tree[tree_udise_col])

master = master[master[master_udise_col].astype(bool)]
notif  = notif[notif[notif_udise_col].astype(bool)]
tree   = tree[tree[tree_udise_col].astype(bool)]

if master_udise_col != "UDISE Code":
    master = master.rename(columns={master_udise_col: "UDISE Code"})

master = master.drop_duplicates(subset=["UDISE Code"], keep="first")

# ================= A) Non-Notifiers =================
notif_codes = set(notif[notif_udise_col])
non_notifiers = master[~master["UDISE Code"].isin(notif_codes)]
non_notifiers.to_excel(OUT_NONNOT_XLSX, index=False)

# ================= B) Tree with Meta =================
tree_with_meta = tree.merge(
    master[["UDISE Code", "School Management", "School Category"]],
    left_on=tree_udise_col, right_on="UDISE Code", how="left"
).drop(columns=["UDISE Code"])
tree_with_meta.to_excel(OUT_TREE_XLSX, index=False)

# ================= C) Non-Planters =================
tree_codes = set(tree[tree_udise_col])
non_planters = master[~master["UDISE Code"].isin(tree_codes)]
non_planters.to_excel(OUT_NONPLANT_XLSX, index=False)

# ================= D) Notifications with Meta =================
notif_with_meta = notif.merge(
    master[["UDISE Code", "School Management", "School Category"]],
    left_on=notif_udise_col, right_on="UDISE Code", how="left"
).drop(columns=["UDISE Code"])
notif_with_meta.to_excel(OUT_NOTIF_WITH_META_XLSX, index=False)

# ================= Consolidated =================
with pd.ExcelWriter(OUT_ALL_CONSOLIDATED, engine="openpyxl") as writer:
    non_notifiers.to_excel(writer, index=False, sheet_name="A_NonNotifiers")
    tree_with_meta.to_excel(writer, index=False, sheet_name="B_Tree_With_Meta")
    non_planters.to_excel(writer, index=False, sheet_name="C_NonPlanters")
    notif_with_meta.to_excel(writer, index=False, sheet_name="D_Notif_With_Meta")

print("✅ Eco Club reports generated successfully")
