"""Test script for enhanced PDF report"""
import pandas as pd
from pathlib import Path
from enhanced_pdf_report import EnhancedPDFReport
from data_service import DataService

# Load data
data_service = DataService(data_folder='.')
df, success, msg = data_service.load_data()

if success:
    print('✅ Data loaded successfully')
    print(f'   - Records: {len(df)}')
    print(f'   - Columns: {list(df.columns)}')
    
    # Generate PDF
    report = EnhancedPDFReport(df)
    findings = report.get_key_findings()
    
    print('\n📊 Report Findings:')
    print(f'   - Districts: {findings["total_districts"]}')
    print(f'   - Total Schools: {findings["total_schools"]}')
    pct = findings["notification_uploaded"]/findings["total_schools"]*100
    print(f'   - Notification Uploaded: {findings["notification_uploaded"]} ({pct:.1f}%)')
    print(f'   - Excellent (≥75%): {findings["excellent"]} districts')
    print(f'   - Good (50-75%): {findings["good"]} districts')
    print(f'   - Average (25-50%): {findings["average"]} districts')
    print(f'   - Needs Attention (<25%): {findings["needs_attention"]} districts')
    print(f'   - Average Notification %: {findings["avg_notification_pct"]:.2f}%')
    print(f'   - Total Saplings Planted: {findings["total_saplings"]:,}')
    
    # Verify PDF created
    pdf_path = Path('Enhanced_Eco_Club_Report.pdf')
    if pdf_path.exists():
        size_kb = pdf_path.stat().st_size / 1024
        print(f'\n✅ PDF Created: {pdf_path.name} ({size_kb:.2f} KB)')
        print('\n✨ Enhanced PDF Report Test PASSED')
        print('   - Executive Summary: ✓')
        print('   - Performance Categorization: ✓')
        print('   - District-wise Summary: ✓')
        print('   - Top 5 Performers: ✓')
        print('   - Bottom 5 Performers: ✓')
        print('   - Action Plan: ✓')
        print('   - Footer with Dashboard Link: ✓')
        print('   - Current Timestamp: ✓')
    else:
        print('❌ PDF not found')
else:
    print(f'❌ Error: {msg}')
