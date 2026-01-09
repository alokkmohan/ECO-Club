"""
Convert Eco-Club Complete Summary Excel to PDF with Comprehensive Enhancements
Includes all 7 data presentation improvements
"""

import pandas as pd
import qrcode
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from datetime import datetime
from io import BytesIO
import os
import pytz


def generate_qr_code():
    """Generate QR code for Streamlit app"""
    try:
        qr = qrcode.QRCode(version=1, box_size=5, border=2)
        qr.add_data('https://ecoclubup.streamlit.app/')
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img_buffer = BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        return img_buffer
    except:
        return None


def create_pdf_summary(excel_file='Eco-Club-Complete_Summary.xlsx', output_pdf='Eco-Club-Summary.pdf'):
    """Convert Excel summary to enhanced PDF with all 7 data presentation improvements."""
    
    print(f"Loading Excel file: {excel_file}")
    
    # Create PDF document
    doc = SimpleDocTemplate(
        output_pdf,
        pagesize=landscape(A4),
        rightMargin=25,
        leftMargin=25,
        topMargin=35,
        bottomMargin=30
    )
    
    # Container for PDF elements
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=26,
        textColor=colors.HexColor('#1f4788'),
        spaceAfter=10,
        alignment=1  # Center
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#2c5aa0'),
        spaceAfter=12,
        spaceBefore=12,
        alignment=1  # Center
    )
    
    # ==================== COVER PAGE ====================
    title = Paragraph("UP Secondary Schools Eco Club<br/>Complete Summary Report", title_style)
    elements.append(title)
    
    subtitle = Paragraph("Comprehensive Data Analysis with Insights & Action Plans", styles['Italic'])
    elements.append(subtitle)
    elements.append(Spacer(1, 0.3*inch))
    
    # Date - Always use current system time in Indian timezone (IST)
    ist_timezone = pytz.timezone('Asia/Kolkata')
    current_time = datetime.now(ist_timezone)
    date_text = Paragraph(f"<b>Generated on:</b> {current_time.strftime('%B %d, %Y at %I:%M %p IST')}", styles['Normal'])
    elements.append(date_text)
    
    elements.append(Spacer(1, 0.3*inch))
    
    # QR Code
    try:
        qr_img = generate_qr_code()
        if qr_img:
            img = Image(qr_img, width=0.9*inch, height=0.9*inch)
            elements.append(img)
            elements.append(Spacer(1, 0.1*inch))
    except:
        pass
    
    elements.append(Paragraph(
        "<b>Scan for Live Dashboard:</b><br/>https://ecoclubup.streamlit.app/",
        styles['Normal']
    ))
    
    elements.append(PageBreak())
    
    # ==================== EXECUTIVE SUMMARY ====================
    elements.append(Paragraph("EXECUTIVE SUMMARY", heading_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Load data for analysis - ACTUAL DATA
    try:
        excel = pd.ExcelFile(excel_file)
        if 'All Districts' in excel.sheet_names:
            df = pd.read_excel(excel_file, sheet_name='All Districts')
        else:
            df = pd.read_excel(excel_file, sheet_name=excel.sheet_names[0])
        
        # Calculate REAL metrics from data
        total_districts = len(df)
        total_schools = df['Total Schools'].sum() if 'Total Schools' in df.columns else 0
        total_notified = df['Eco-Club Notification Uploaded'].sum() if 'Eco-Club Notification Uploaded' in df.columns else 0
        
        # Calculate average percentage
        if total_schools > 0:
            avg_pct = (total_notified / total_schools * 100)
        else:
            avg_pct = 0
        
        # Categorize districts
        excellent = len(df[df['Percentage (%)'] >= 75]) if 'Percentage (%)' in df.columns else 0
        good = len(df[(df['Percentage (%)'] >= 50) & (df['Percentage (%)'] < 75)]) if 'Percentage (%)' in df.columns else 0
        average = len(df[(df['Percentage (%)'] >= 25) & (df['Percentage (%)'] < 50)]) if 'Percentage (%)' in df.columns else 0
        critical = len(df[df['Percentage (%)'] < 25]) if 'Percentage (%)' in df.columns else 0
        
        summary_data = [
            ['Metric', 'Value', 'Performance'],
            ['Total Districts', str(total_districts), '75 Districts'],
            ['Total Schools', f"{int(total_schools):,}", f'{int(total_schools):,} Schools'],
            ['Notifications Uploaded', f"{int(total_notified):,}", f'{avg_pct:.1f}% Complete'],
            ['', '', ''],
            ['EXCELLENT (≥75%)', str(excellent), f'{excellent} Districts'],
            ['GOOD (50-75%)', str(good), f'{good} Districts'],
            ['AVERAGE (25-50%)', str(average), f'{average} Districts'],
            ['CRITICAL (<25%)', str(critical), f'{critical} Districts'],
        ]
    except Exception as e:
        summary_data = [['Metric', 'Value', 'Performance'], ['Error loading data', str(e), 'N/A']]
    
    summary_table = Table(summary_data, colWidths=[2.8*inch, 1.8*inch, 2*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, 4), [colors.white, colors.lightgrey]),
        # Color-code category rows
        ('BACKGROUND', (0, 5), (-1, 5), colors.HexColor('#90EE90')),  # Light green for Excellent
        ('BACKGROUND', (0, 6), (-1, 6), colors.HexColor('#FFFFE0')),  # Light yellow for Good
        ('BACKGROUND', (0, 7), (-1, 7), colors.HexColor('#FFE4B5')),  # Moccasin for Average
        ('BACKGROUND', (0, 8), (-1, 8), colors.HexColor('#FFB6C1')),  # Light pink for Critical
        ('FONTNAME', (0, 5), (-1, 8), 'Helvetica-Bold'),
    ]))
    elements.append(summary_table)
    
    elements.append(PageBreak())
    
    # Detailed Category Breakdown Section with Tables (Start from Page 2)
    category_heading = Paragraph("PERFORMANCE CATEGORY DETAILS", heading_style)
    elements.append(category_heading)
    elements.append(Spacer(1, 0.2*inch))
    
    # Helper function to create category table
    def create_category_table(category_df, category_name, bg_color):
        if len(category_df) == 0:
            return
        
        cat_heading = Paragraph(category_name, heading_style)
        elements.append(cat_heading)
        elements.append(Spacer(1, 0.1*inch))
        
        # Add Sr. No. and prepare data
        cat_df = category_df.copy()
        cat_df.insert(0, 'Sr. No.', range(1, len(cat_df) + 1))
        cat_data = [cat_df.columns.tolist()] + cat_df.values.tolist()
        
        cat_table = Table(cat_data, repeatRows=1)
        cat_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5aa0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 1), (-1, -1), bg_color),
        ]))
        elements.append(cat_table)
        elements.append(Spacer(1, 0.2*inch))
    
    # Get category data if percentage column exists
    if 'Percentage (%)' in df.columns:
        # EXCELLENT Districts Table (sorted by % descending - best first)
        excellent_df = df[df['Percentage (%)'] >= 75][['District', 'Total Schools', 'Eco-Club Notification Uploaded', 'Percentage (%)']].copy()
        excellent_df = excellent_df.sort_values('Percentage (%)', ascending=False)
        create_category_table(excellent_df, f"EXCELLENT PERFORMERS (≥75%) - {excellent} Districts", colors.HexColor('#90EE90'))
        
        # GOOD Districts Table (sorted by % descending - best first)
        good_df = df[(df['Percentage (%)'] >= 50) & (df['Percentage (%)'] < 75)][['District', 'Total Schools', 'Eco-Club Notification Uploaded', 'Percentage (%)']].copy()
        good_df = good_df.sort_values('Percentage (%)', ascending=False)
        create_category_table(good_df, f"GOOD PERFORMERS (50-75%) - {good} Districts", colors.HexColor('#FFFFE0'))
        
        # AVERAGE Districts Table (sorted by % ascending - worst first)
        average_df = df[(df['Percentage (%)'] >= 25) & (df['Percentage (%)'] < 50)][['District', 'Total Schools', 'Eco-Club Notification Uploaded', 'Percentage (%)']].copy()
        average_df = average_df.sort_values('Percentage (%)', ascending=True)
        create_category_table(average_df, f"AVERAGE PERFORMERS (25-50%) - {average} Districts", colors.HexColor('#FFE4B5'))
        
        # CRITICAL Districts Table (sorted by % ascending - worst first)
        critical_df = df[df['Percentage (%)'] < 25][['District', 'Total Schools', 'Eco-Club Notification Uploaded', 'Percentage (%)']].copy()
        critical_df = critical_df.sort_values('Percentage (%)', ascending=True)
        create_category_table(critical_df, f"CRITICAL - NEEDS IMMEDIATE ATTENTION (<25%) - {critical} Districts", colors.HexColor('#FFB6C1'))
    
    elements.append(Spacer(1, 0.3*inch))
    elements.append(PageBreak())
    
    # ==================== PERFORMANCE CATEGORIZATION ====================
    elements.append(Paragraph("PERFORMANCE CATEGORIZATION SYSTEM", heading_style))
    elements.append(Spacer(1, 0.2*inch))
    
    category_data = [['Category', 'Performance Range', 'Status', 'Action Required']]
    category_data.append(['GREEN - Excellent', '>= 75% Completion', 'Leader', 'Recognition & Mentoring'])
    category_data.append(['YELLOW - Good', '50-75% Completion', 'On Track', 'Guidance & Support'])
    category_data.append(['ORANGE - Average', '25-50% Completion', 'Developing', 'Intensive Support'])
    category_data.append(['RED - Critical', '< 25% Completion', 'Critical', 'Immediate Intervention'])
    
    category_table = Table(category_data, colWidths=[1.6*inch, 1.6*inch, 1.6*inch, 1.8*inch])
    category_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
    ]))
    elements.append(category_table)
    
    elements.append(Spacer(1, 0.3*inch))
    elements.append(PageBreak())
    
    # ==================== KEY INSIGHTS ====================
    elements.append(Paragraph("KEY FINDINGS & ACTIONABLE INSIGHTS", heading_style))
    elements.append(Spacer(1, 0.2*inch))
    
    insights = """
    <b>IMPROVEMENT AREAS:</b><br/>
    • Significant variation in district performance across UP<br/>
    • Tree planting data needs better integration with notification uploads<br/>
    • Several districts require intensive support and intervention<br/>
    <br/>
    
    <b>BEST PERFORMERS - MODEL DISTRICTS:</b><br/>
    • Refer 'Top 10' sheet for districts achieving excellent results<br/>
    • Document and share best practices from high performers<br/>
    • Establish peer mentoring programs<br/>
    <br/>
    
    <b>CRITICAL AREAS REQUIRING ATTENTION:</b><br/>
    • Refer 'Bottom 25' sheet for urgent intervention districts<br/>
    • Weekly monitoring and daily reporting required<br/>
    • Senior leadership engagement necessary<br/>
    <br/>
    
    <b>NEXT STEPS:</b><br/>
    • Implement categorization-based action plans<br/>
    • Deploy field officers to critical districts<br/>
    • Schedule weekly progress review meetings<br/>
    • Monitor tree data integration improvements<br/>
    """
    
    elements.append(Paragraph(insights, styles['Normal']))
    
    elements.append(Spacer(1, 0.3*inch))
    elements.append(PageBreak())
    
    # ==================== ACTION PLAN ====================
    elements.append(Paragraph("STRATEGIC ACTION PLAN", heading_style))
    elements.append(Spacer(1, 0.2*inch))
    
    action_text = """
    <b>IMPLEMENTATION TIMELINE:</b><br/><br/>
    
    <b>RED ZONES (< 25% Completion) - CRITICAL INTERVENTION:</b><br/>
    • Week 1: Emergency district mobilization<br/>
    • Week 1-2: Root cause analysis and barrier identification<br/>
    • Week 2-3: Resource deployment and training<br/>
    • Daily: Progress monitoring and reporting<br/>
    • Target: 50% completion within 4 weeks<br/>
    <br/>
    
    <b>ORANGE ZONES (25-50% Completion) - INTENSIVE SUPPORT:</b><br/>
    • Week 1: Support team deployment<br/>
    • Week 1-2: Capacity building and resource allocation<br/>
    • Weekly: Progress monitoring<br/>
    • Target: 70% completion within 8 weeks<br/>
    <br/>
    
    <b>YELLOW ZONES (50-75% Completion) - GUIDANCE & SUPPORT:</b><br/>
    • Bi-weekly: Progress review and support<br/>
    • Monthly: Performance assessment<br/>
    • Target: Achieve 85% completion<br/>
    <br/>
    
    <b>GREEN ZONES (>= 75% Completion) - RECOGNITION & MENTORING:</b><br/>
    • Monthly: Recognition and appreciation<br/>
    • Leadership role in state initiatives<br/>
    • Best practice documentation and sharing<br/>
    • Peer mentoring of other districts<br/>
    <br/>
    
    <b>ACCOUNTABILITY FRAMEWORK:</b><br/>
    • District Education Officers: Daily reporting for critical zones<br/>
    • Block Coordinators: Bi-weekly field visits<br/>
    • State Officials: Weekly review meetings<br/>
    • Real-time data: Dashboard access at https://ecoclubup.streamlit.app/<br/>
    """
    
    elements.append(Paragraph(action_text, styles['Normal']))
    
    elements.append(PageBreak())
    
    # ==================== DETAILED DATA SHEETS ====================
    elements.append(Paragraph("DETAILED DATA SHEETS", heading_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Process All Districts
    sheet_heading = Paragraph("All Districts", heading_style)
    elements.append(sheet_heading)
    elements.append(Spacer(1, 0.1*inch))
    
    # Use df as district_summary_sorted (sort by percentage descending)
    district_summary_sorted = df.copy()
    if 'Percentage (%)' in district_summary_sorted.columns:
        district_summary_sorted = district_summary_sorted.sort_values('Percentage (%)', ascending=False).reset_index(drop=True)
    
    # Add Sr. No. column at the beginning
    df_display = district_summary_sorted.copy()
    df_display.insert(0, 'Sr. No.', range(1, len(df_display) + 1))
    
    # Add Performance Category column
    def categorize(pct):
        if pct >= 75:
            return 'EXCELLENT'
        elif pct >= 50:
            return 'GOOD'
        elif pct >= 25:
            return 'AVERAGE'
        else:
            return 'CRITICAL'
    df_display['Category'] = df_display['Percentage (%)'].apply(categorize)
    
    # Convert DataFrame to list for table
    data = [df_display.columns.tolist()] + df_display.values.tolist()
    
    # Create table
    table = Table(data, repeatRows=1)
    
    # Base table style
    table_style = TableStyle([
        # Header
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5aa0')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        
        # Body
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 7),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ])
    
    # Apply color-coding based on performance
    pct_col_idx = list(df_display.columns).index('Percentage (%)')
    for row_idx in range(1, len(data)):  # Start from 1 to skip header
        pct_value = data[row_idx][pct_col_idx]
        try:
            pct_num = float(pct_value)
            if pct_num >= 75:
                table_style.add('BACKGROUND', (0, row_idx), (-1, row_idx), colors.HexColor('#90EE90'))  # Light green
            elif pct_num >= 50:
                table_style.add('BACKGROUND', (0, row_idx), (-1, row_idx), colors.HexColor('#FFFFE0'))  # Light yellow
            elif pct_num >= 25:
                table_style.add('BACKGROUND', (0, row_idx), (-1, row_idx), colors.HexColor('#FFE4B5'))  # Moccasin
            else:
                table_style.add('BACKGROUND', (0, row_idx), (-1, row_idx), colors.HexColor('#FFB6C1'))  # Light pink
        except:
            table_style.add('BACKGROUND', (0, row_idx), (-1, row_idx), colors.white)
    
    table.setStyle(table_style)
    elements.append(table)
    elements.append(PageBreak())
    
    # Process Bottom 25
    sheet_heading = Paragraph("Bottom 25 Districts", heading_style)
    elements.append(sheet_heading)
    elements.append(Spacer(1, 0.1*inch))
    
    # Add Sr. No. column
    df_bottom = bottom_25.copy()
    df_bottom.insert(0, 'Sr. No.', range(1, len(df_bottom) + 1))
    
    data_bottom = [df_bottom.columns.tolist()] + df_bottom.values.tolist()
    table_bottom = Table(data_bottom, repeatRows=1)
    table_bottom.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5aa0')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 7),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
    ]))
    elements.append(table_bottom)
    
    # Process Overall Summary
    elements.append(PageBreak())
    sheet_heading = Paragraph("Overall Summary", heading_style)
    elements.append(sheet_heading)
    elements.append(Spacer(1, 0.1*inch))
    
    overall_data = [
        ['Metric', 'Value'],
        ['Total Districts', str(total_districts)],
        ['Total Schools', f'{int(total_schools):,}'],
        ['Total Notifications Uploaded', f'{int(total_notified):,}'],
        ['Average Completion %', f'{avg_pct:.2f}%'],
        ['Districts with ≥75%', str(excellent)],
        ['Districts with 50-75%', str(good)],
        ['Districts with 25-50%', str(average)],
        ['Districts with <25%', str(critical)],
    ]
    
    overall_table = Table(overall_data)
    overall_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5aa0')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
    ]))
    elements.append(overall_table)
    
    # ==================== FOOTER ====================
    elements.append(Spacer(1, 0.8*inch))
    
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#1f4788'),
        alignment=1,  # Center
    )
    
    footer_text = Paragraph(
        "<b>For live updates and detailed information, visit:</b><br/>"
        "<a href='https://ecoclubup.streamlit.app/' color='blue'>https://ecoclubup.streamlit.app/</a><br/>"
        f"Report Generated: {current_time.strftime('%d-%m-%Y %H:%M:%S')}",
        footer_style
    )
    elements.append(footer_text)
    
    # Build PDF
    print(f"Creating PDF: {output_pdf}")
    doc.build(elements)
    print(f"[OK] PDF created successfully: {output_pdf}")
    print(f"File size: {os.path.getsize(output_pdf) / 1024:.2f} KB")


if __name__ == "__main__":
    create_pdf_summary('All_Schools_with_Notifications_UTTAR PRADESH.xlsx', 'Eco-Club-Summary.pdf')
