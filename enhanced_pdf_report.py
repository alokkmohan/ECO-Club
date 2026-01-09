"""
Enhanced Comprehensive PDF Report Generator
Creates professional, data-rich PDF reports with visualizations, insights, and action plans
"""

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from datetime import datetime
import os


class EnhancedPDFReport:
    """Generate comprehensive PDF reports with visualizations and insights"""
    
    def __init__(self, school_df):
        self.school_df = school_df.copy()
        self.create_district_summary()
        
    def create_district_summary(self):
        """Create district-wise summary from school data"""
        self.district_summary = self.school_df.groupby('District').agg({
            'UDISE Code': 'count',
            'Notification Uploaded': lambda x: (x == 'Yes').sum(),
            'Trees Planted': 'sum',
            'Tree Uploaded': lambda x: (x == 'Yes').sum()
        }).reset_index()
        
        self.district_summary.columns = ['District', 'Total Schools', 'Notification Uploaded', 'Total Saplings', 'Schools with Tree Data']
        self.district_summary['Notification %'] = (
            self.district_summary['Notification Uploaded'] / self.district_summary['Total Schools'] * 100
        ).round(2)
        self.district_summary['Tree Upload %'] = (
            self.district_summary['Schools with Tree Data'] / self.district_summary['Total Schools'] * 100
        ).round(2)
        
        # Categorize
        self.district_summary['Category'] = self.district_summary['Notification %'].apply(self._get_category)
        self.district_summary = self.district_summary.sort_values('Notification %', ascending=False)
    
    def _get_category(self, percentage):
        """Categorize districts"""
        if percentage >= 75:
            return "Excellent"
        elif percentage >= 50:
            return "Good"
        elif percentage >= 25:
            return "Average"
        else:
            return "Needs Attention"
    
    def get_key_findings(self):
        """Generate key findings"""
        df = self.district_summary
        
        findings = {
            'total_districts': len(df),
            'excellent': len(df[df['Notification %'] >= 75]),
            'good': len(df[(df['Notification %'] >= 50) & (df['Notification %'] < 75)]),
            'average': len(df[(df['Notification %'] >= 25) & (df['Notification %'] < 50)]),
            'needs_attention': len(df[df['Notification %'] < 25]),
            'avg_notification_pct': df['Notification %'].mean(),
            'total_schools': self.school_df.shape[0],
            'notification_uploaded': len(self.school_df[self.school_df['Notification Uploaded'] == 'Yes']),
            'total_saplings': self.school_df['Trees Planted'].sum(),
            'top_5_districts': df.head(5),
            'bottom_5_districts': df.tail(5)
        }
        
        return findings
    
    def generate_pdf(self, output_file='Enhanced_Eco_Club_Report.pdf'):
        """Generate comprehensive PDF report"""
        
        doc = SimpleDocTemplate(
            output_file,
            pagesize=landscape(A4),
            rightMargin=30,
            leftMargin=30,
            topMargin=40,
            bottomMargin=30
        )
        
        elements = []
        styles = getSampleStyleSheet()
        
        # ==================== COVER PAGE ====================
        
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=28,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=30,
            alignment=1
        )
        
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#2c5aa0'),
            spaceAfter=20,
            alignment=1
        )
        
        # Title
        title = Paragraph("UP SECONDARY SCHOOLS<br/>ECO CLUB MONITORING REPORT", title_style)
        elements.append(title)
        
        # Subtitle
        subtitle = Paragraph("Enhanced Data Analysis with Insights & Action Plans", subtitle_style)
        elements.append(subtitle)
        
        elements.append(Spacer(1, 0.3*inch))
        
        # Report Date
        date_text = Paragraph(
            f"<b>Report Generated:</b> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
            styles['Normal']
        )
        elements.append(date_text)
        
        elements.append(Spacer(1, 0.5*inch))
        
        # QR Code info
        qr_info = Paragraph(
            "<b>Scan for Live Dashboard:</b><br/>"
            "<i>Visit: https://ecoclubup.streamlit.app/ for interactive data</i>",
            styles['Italic']
        )
        elements.append(qr_info)
        
        elements.append(PageBreak())
        
        # ==================== EXECUTIVE SUMMARY ====================
        
        elements.append(Paragraph("EXECUTIVE SUMMARY", styles['Heading1']))
        elements.append(Spacer(1, 0.2*inch))
        
        findings = self.get_key_findings()
        
        # Key Metrics
        summary_data = [
            ['Metric', 'Value', 'Status'],
            ['Total Districts', str(findings['total_districts']), '✓'],
            ['Total Schools', str(findings['total_schools']), '✓'],
            [
                'Notification Uploaded',
                f"{findings['notification_uploaded']:,} ({findings['notification_uploaded']/findings['total_schools']*100:.2f}%)",
                '✓' if findings['notification_uploaded']/findings['total_schools'] > 0.5 else '⚠️'
            ],
            ['Average Notification %', f"{findings['avg_notification_pct']:.2f}%", '✓'],
            ['Total Saplings Planted', f"{findings['total_saplings']:,}", '✓'],
        ]
        
        summary_table = Table(summary_data)
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        elements.append(summary_table)
        
        elements.append(Spacer(1, 0.3*inch))
        elements.append(PageBreak())
        
        # ==================== PERFORMANCE CATEGORIZATION ====================
        
        elements.append(Paragraph("PERFORMANCE CATEGORIZATION", styles['Heading1']))
        elements.append(Spacer(1, 0.2*inch))
        
        category_data = [['Category', 'Count', 'Description']]
        category_data.append(['Excellent', str(findings['excellent']), '≥ 75% Notification Upload'])
        category_data.append(['Good', str(findings['good']), '50-75% Notification Upload'])
        category_data.append(['Average', str(findings['average']), '25-50% Notification Upload'])
        category_data.append(['Needs Attention', str(findings['needs_attention']), '< 25% Notification Upload'])
        
        category_table = Table(category_data, colWidths=[2*inch, 1.5*inch, 2.5*inch])
        category_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5aa0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        elements.append(category_table)
        
        elements.append(Spacer(1, 0.3*inch))
        elements.append(PageBreak())
        
        # ==================== ALL DISTRICTS SUMMARY ====================
        
        elements.append(Paragraph("DISTRICT-WISE SUMMARY", styles['Heading1']))
        elements.append(Spacer(1, 0.2*inch))
        
        summary_df = self.district_summary[['District', 'Total Schools', 'Notification Uploaded', 'Notification %', 'Category']]
        
        summary_data = [['District', 'Schools', 'Notified', 'Notif %', 'Category']]
        for _, row in summary_df.iterrows():
            summary_data.append([
                row['District'],
                str(int(row['Total Schools'])),
                str(int(row['Notification Uploaded'])),
                f"{row['Notification %']:.2f}%",
                row['Category']
            ])
        
        # Add total row
        total_schools = self.district_summary['Total Schools'].sum()
        total_notified = self.district_summary['Notification Uploaded'].sum()
        summary_data.append([
            'TOTAL',
            str(int(total_schools)),
            str(int(total_notified)),
            f"{total_notified/total_schools*100:.2f}%",
            ''
        ])
        
        summary_table = Table(summary_data, colWidths=[2.5*inch, 1*inch, 1*inch, 1.2*inch, 1.5*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5aa0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.lightgrey]),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#f39c12')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ]))
        elements.append(summary_table)
        
        elements.append(Spacer(1, 0.3*inch))
        elements.append(PageBreak())
        
        # ==================== TOP & BOTTOM PERFORMERS ====================
        
        elements.append(Paragraph("TOP 5 BEST PERFORMING DISTRICTS", styles['Heading1']))
        elements.append(Spacer(1, 0.2*inch))
        
        top_data = [['District', 'Notification %', 'Schools', 'Notified']]
        for _, row in findings['top_5_districts'].iterrows():
            top_data.append([
                row['District'],
                f"{row['Notification %']:.2f}%",
                str(int(row['Total Schools'])),
                str(int(row['Notification Uploaded']))
            ])
        
        top_table = Table(top_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
        top_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#27AE60')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(top_table)
        
        elements.append(Spacer(1, 0.4*inch))
        
        elements.append(Paragraph("BOTTOM 5 DISTRICTS - IMMEDIATE ATTENTION NEEDED", styles['Heading1']))
        elements.append(Spacer(1, 0.2*inch))
        
        bottom_data = [['District', 'Notification %', 'Gap %', 'Priority']]
        for _, row in findings['bottom_5_districts'].iterrows():
            gap = 100 - row['Notification %']
            priority = '🔴 CRITICAL' if row['Notification %'] < 20 else '🟠 HIGH'
            bottom_data.append([
                row['District'],
                f"{row['Notification %']:.2f}%",
                f"{gap:.2f}%",
                priority
            ])
        
        bottom_table = Table(bottom_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
        bottom_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8B0000')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(bottom_table)
        
        elements.append(PageBreak())
        
        # ==================== ACTION PLAN ====================
        
        elements.append(Paragraph("ACTION PLAN FOR UNDERPERFORMING DISTRICTS", styles['Heading1']))
        elements.append(Spacer(1, 0.2*inch))
        
        action_text = Paragraph("""
        <b>🎯 PRIORITY-BASED ACTION ITEMS:</b><br/><br/>
        
        <b>🔴 CRITICAL (< 20% Notification Upload):</b><br/>
        • Immediate contact with District Education Officer<br/>
        • On-ground field visit within 1 week<br/>
        • Daily progress tracking and reporting<br/>
        • Dedicated focal person for coordination<br/>
        • Technical support and training sessions<br/>
        <br/>
        
        <b>🟠 HIGH PRIORITY (20-60% Upload):</b><br/>
        • Weekly coordination meetings<br/>
        • Peer mentoring from high-performing districts<br/>
        • Bi-weekly progress reviews and updates<br/>
        • Incentive programs for early uploads<br/>
        • Share best practices from top performers<br/>
        <br/>
        
        <b>📋 MONITORING MECHANISM:</b><br/>
        • Real-time tracking dashboard<br/>
        • Weekly district-wise reports<br/>
        • Monthly district officer meetings<br/>
        • Quarterly review with state officials<br/>
        """, styles['Normal'])
        elements.append(action_text)
        
        elements.append(PageBreak())
        
        # ==================== FOOTER ====================
        
        elements.append(Spacer(1, 0.5*inch))
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#1f4788'),
            alignment=1,
            spaceAfter=12
        )
        footer_text = Paragraph(
            "<b>For live updates and detailed information, visit:</b><br/>"
            "<a href='https://ecoclubup.streamlit.app/' color='blue'>https://ecoclubup.streamlit.app/</a>",
            footer_style
        )
        elements.append(footer_text)
        
        # Build PDF
        print(f"Creating enhanced PDF: {output_file}")
        doc.build(elements)
        print(f"✅ Enhanced PDF created successfully: {output_file}")
        print(f"File size: {os.path.getsize(output_file) / 1024:.2f} KB")
        
        return output_file


if __name__ == "__main__":
    # Load school data
    from data_service import DataService
    
    data_service = DataService(data_folder=".")
    df, success, error_message = data_service.load_data()
    
    if success:
        # Generate enhanced PDF
        report = EnhancedPDFReport(df)
        report.generate_pdf('Enhanced_Eco_Club_Report.pdf')
    else:
        print(f"Error loading data: {error_message}")
