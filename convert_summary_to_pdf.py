"""
Convert Eco-Club Complete Summary Excel to PDF
"""

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from datetime import datetime
import os


def create_pdf_summary(excel_file='Eco-Club-Complete_Summary.xlsx', output_pdf='Eco-Club-Summary.pdf'):
    """Convert Excel summary to formatted PDF."""
    
    print(f"Loading Excel file: {excel_file}")
    
    # Create PDF document
    doc = SimpleDocTemplate(
        output_pdf,
        pagesize=landscape(A4),
        rightMargin=30,
        leftMargin=30,
        topMargin=40,
        bottomMargin=30
    )
    
    # Container for PDF elements
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1f4788'),
        spaceAfter=30,
        alignment=1  # Center
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#2c5aa0'),
        spaceAfter=12,
        spaceBefore=12
    )
    
    # Title
    title = Paragraph("UP Secondary Schools Eco Club - Complete Summary", title_style)
    elements.append(title)
    
    # Date - Always use current system time
    from datetime import datetime as dt
    current_time = dt.now()
    date_text = Paragraph(f"Generated on: {current_time.strftime('%B %d, %Y at %I:%M %p')}", styles['Normal'])
    elements.append(date_text)
    elements.append(Spacer(1, 0.3*inch))
    
    # Read Excel file
    excel = pd.ExcelFile(excel_file)
    
    for sheet_name in excel.sheet_names:
        print(f"Processing sheet: {sheet_name}")
        
        # Add sheet heading
        sheet_heading = Paragraph(f"{sheet_name}", heading_style)
        elements.append(sheet_heading)
        elements.append(Spacer(1, 0.1*inch))
        
        # Read sheet
        df = pd.read_excel(excel_file, sheet_name=sheet_name)
        
        # Convert DataFrame to list for table
        data = [df.columns.tolist()] + df.values.tolist()
        
        # Limit rows for better display
        if len(data) > 100:
            data = data[:100]
            note = Paragraph(f"<i>Note: Showing first 100 rows out of {len(df)} total rows</i>", styles['Italic'])
        
        # Create table
        table = Table(data, repeatRows=1)
        
        # Table style
        table_style = TableStyle([
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5aa0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # Body
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ])
        
        table.setStyle(table_style)
        elements.append(table)
        
        if len(data) > 100:
            elements.append(Spacer(1, 0.1*inch))
            elements.append(note)
        
        # Page break after each sheet except last
        if sheet_name != excel.sheet_names[-1]:
            elements.append(PageBreak())
    
    # Add footer with website link
    elements.append(Spacer(1, 0.5*inch))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#1f4788'),
        alignment=1,  # Center
        spaceAfter=12
    )
    footer_text = Paragraph(
        "<b>लाइव अपडेट्स और विस्तृत जानकारी के लिए यहां visit करें:</b><br/>"
        "<a href='https://ecoclubup.streamlit.app/' color='blue'>https://ecoclubup.streamlit.app/</a>",
        footer_style
    )
    elements.append(footer_text)
    
    # Build PDF
    print(f"Creating PDF: {output_pdf}")
    doc.build(elements)
    print(f"✅ PDF created successfully: {output_pdf}")
    print(f"File size: {os.path.getsize(output_pdf) / 1024:.2f} KB")


if __name__ == "__main__":
    create_pdf_summary()
