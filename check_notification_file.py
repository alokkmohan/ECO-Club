import pandas as pd

xl = pd.ExcelFile('All_Schools_with_Notifications_UTTAR PRADESH.xlsx')
print('Sheets:', xl.sheet_names)

for sheet in xl.sheet_names:
    df = pd.read_excel(xl, sheet_name=sheet)
    print(f'\n{sheet}:')
    print(f'  Rows: {len(df)}')
    print(f'  Columns: {len(df.columns)}')
    if len(df.columns) > 0:
        print(f'  Column names: {df.columns.tolist()[:5]}')
        if len(df) > 0:
            print(f'  First row sample: {df.iloc[0].tolist()[:3]}')
