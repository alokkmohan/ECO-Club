"""
Comprehensive Eco-Club Data Presentation with Advanced Analytics
Includes charts, performance categorization, insights, tree data integration, and action plans
"""

import pandas as pd
import numpy as np
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak,
    Image, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from datetime import datetime
from io import BytesIO
import qrcode
import os


class ComprehensiveEcoReport:
    """Generate comprehensive PDF report with visualizations and analytics"""
    
    def __init__(self, school_df, tree_df=None):
        self.school_df = school_df.copy()
        self.tree_df = tree_df.copy() if tree_df is not None else None
        self.create_district_summary()
        self.categorize_districts()
        
    def create_district_summary(self):
        """Create district-wise summary with tree data integration"""
        self.district_summary = self.school_df.groupby('District').agg({
            'UDISE Code': 'count',
            'Notification Uploaded': lambda x: (x == 'Yes').sum(),
            'Trees Planted': 'sum',
            'Tree Uploaded': lambda x: (x == 'Yes').sum()
        }).reset_index()
        
        self.district_summary.columns = [
            'District', 'Total Schools', 'Notification Uploaded', 
            'Total Saplings', 'Schools with Tree Data'
        ]
        
        # Calculate percentages
        self.district_summary['Notification %'] = (
            self.district_summary['Notification Uploaded'] / 
            self.district_summary['Total Schools'] * 100
        ).round(2)
        
        self.district_summary['Tree Upload %'] = (
            self.district_summary['Schools with Tree Data'] / 
            self.district_summary['Total Schools'] * 100
        ).round(2)
        
        # Merge tree data if available
        if self.tree_df is not None:
            tree_summary = self.tree_df.groupby('District').agg({
                'Saplings': 'sum'
            }).reset_index()
            tree_summary.columns = ['District', 'Tree Data Saplings']
            self.district_summary = self.district_summary.merge(
                tree_summary, on='District', how='left'
            ).fillna(0)
            
            # Calculate gap analysis
            self.district_summary['Tree Gap'] = (
                self.district_summary['Notification %'] - 
                self.district_summary['Tree Upload %']
            ).round(2)
        
        self.district_summary = self.district_summary.sort_values(
            'Notification %', ascending=False
        )
    
    def categorize_districts(self):
        """Categorize districts by performance"""
        def get_category(pct):
            if pct >= 75:
                return "Excellent"
            elif pct >= 50:
                return "Good"
            elif pct >= 25:
                return "Average"
            else:
                return "Needs Attention"
        
        def get_color(pct):
            if pct >= 60:
                return colors.HexColor('#27AE60')  # Green
            elif pct >= 30:
                return colors.HexColor('#F39C12')  # Yellow
            else:
                return colors.HexColor('#E74C3C')  # Red
        
        self.district_summary['Category'] = self.district_summary['Notification %'].apply(get_category)
        self.district_summary['Color'] = self.district_summary['Notification %'].apply(get_color)
        
        # Statistics
        self.excellent = len(self.district_summary[self.district_summary['Category'] == 'Excellent'])
        self.good = len(self.district_summary[self.district_summary['Category'] == 'Good'])
        self.average = len(self.district_summary[self.district_summary['Category'] == 'Average'])
        self.needs_attention = len(self.district_summary[self.district_summary['Category'] == 'Needs Attention'])
        self.total_districts = len(self.district_summary)
    
    def generate_qr_code(self):
        """Generate QR code for Streamlit app"""
        qr = qrcode.QRCode(version=1, box_size=5, border=2)
        qr.add_data('https://ecoclubup.streamlit.app/')
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        img_buffer = BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        return img_buffer
    
    def generate_pdf(self, output_file='Comprehensive_Eco_Club_Report.pdf'):
        """Generate comprehensive PDF report"""
        
        doc = SimpleDocTemplate(
            output_file,
            pagesize=landscape(A4),
            rightMargin=25,
            leftMargin=25,
            topMargin=35,
            bottomMargin=30
        )
        
        elements = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=28,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=10,
            alignment=1
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2c5aa0'),
            spaceAfter=12,
            spaceBefore=12
        )
        
        # ==================== COVER PAGE ====================
        elements.append(Paragraph(
            "UP SECONDARY SCHOOLS<br/>ECO CLUB MONITORING REPORT",
            title_style
        ))
        
        elements.append(Paragraph(
            "Comprehensive Data Analysis with Insights & Action Plans",
            styles['Italic']
        ))
        
        elements.append(Spacer(1, 0.4*inch))
        
        # Report details
        current_time = datetime.now()
        elements.append(Paragraph(
            f"<b>Report Generated:</b> {current_time.strftime('%B %d, %Y at %I:%M %p')}",
            styles['Normal']
        ))
        
        elements.append(Spacer(1, 0.3*inch))
        
        # QR Code
        try:
            qr_img = self.generate_qr_code()
            img = Image(qr_img, width=1*inch, height=1*inch)
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
        
        # Key metrics
        total_schools = self.school_df.shape[0]
        notification_uploaded = len(self.school_df[self.school_df['Notification Uploaded'] == 'Yes'])
        notification_pct = (notification_uploaded / total_schools * 100)
        total_saplings = self.school_df['Trees Planted'].sum()
        
        summary_data = [
            ['Metric', 'Value', 'Status'],
            ['Total Districts', str(self.total_districts), '✓'],
            ['Total Schools', f"{total_schools:,}", '✓'],
            ['Notification Uploaded', f"{notification_uploaded:,} ({notification_pct:.1f}%)", 
             '✓' if notification_pct > 50 else '⚠️'],
            ['Excellent Districts (≥75%)', str(self.excellent), '🟢'],
            ['Good Districts (50-75%)', str(self.good), '🟡'],
            ['Average Districts (25-50%)', str(self.average), '🟠'],
            ['Needs Attention (<25%)', str(self.needs_attention), '🔴'],
            ['Total Saplings Planted', f"{total_saplings:,}", '✓'],
        ]
        
        summary_table = Table(summary_data, colWidths=[2.5*inch, 2*inch, 1.5*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        elements.append(summary_table)
        
        elements.append(Spacer(1, 0.3*inch))
        elements.append(PageBreak())
        
        # ==================== PERFORMANCE CATEGORIZATION ====================
        elements.append(Paragraph("PERFORMANCE CATEGORIZATION", heading_style))
        elements.append(Spacer(1, 0.2*inch))
        
        category_data = [['Category', 'Districts', 'Percentage', 'Status']]
        total = self.total_districts
        category_data.append(['🟢 Excellent (≥75%)', str(self.excellent), 
                            f"{self.excellent/total*100:.1f}%", 'Leaders'])
        category_data.append(['🟡 Good (50-75%)', str(self.good), 
                            f"{self.good/total*100:.1f}%", 'On Track'])
        category_data.append(['🟠 Average (25-50%)', str(self.average), 
                            f"{self.average/total*100:.1f}%", 'Developing'])
        category_data.append(['🔴 Needs Attention (<25%)', str(self.needs_attention), 
                            f"{self.needs_attention/total*100:.1f}%", 'Critical'])
        
        category_table = Table(category_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
        category_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        elements.append(category_table)
        
        elements.append(Spacer(1, 0.3*inch))
        elements.append(PageBreak())
        
        # ==================== KEY FINDINGS & INSIGHTS ====================
        elements.append(Paragraph("KEY FINDINGS & ACTIONABLE INSIGHTS", heading_style))
        elements.append(Spacer(1, 0.2*inch))
        
        # Identify critical districts
        critical = self.district_summary[self.district_summary['Notification %'] < 25].head(5)
        excellent = self.district_summary[self.district_summary['Notification %'] >= 75].head(5)
        
        insights_text = f"""
        <b>📊 KEY STATISTICS:</b><br/>
        • {100 - notification_pct:.1f}% districts still below target notification completion<br/>
        • {self.excellent} districts have achieved Excellent performance (≥75%)<br/>
        • {self.needs_attention} districts require immediate intervention (<25%)<br/>
        <br/>
        
        <b>🔴 CRITICAL ATTENTION REQUIRED:</b><br/>
        """
        
        for idx, row in critical.iterrows():
            insights_text += f"• {row['District']}: {row['Notification %']:.2f}% completion<br/>"
        
        insights_text += f"""
        <br/>
        <b>🟢 BEST PERFORMERS (MODEL DISTRICTS):</b><br/>
        """
        
        for idx, row in excellent.iterrows():
            insights_text += f"• {row['District']}: {row['Notification %']:.2f}% - Document best practices<br/>"
        
        if self.tree_df is not None and 'Tree Gap' in self.district_summary.columns:
            gap_issues = self.district_summary[self.district_summary['Tree Gap'] > 20].head(3)
            insights_text += f"""
            <br/>
            <b>🌳 TREE DATA INTEGRATION ISSUES:</b><br/>
            Notification done but tree data missing:<br/>
            """
            for idx, row in gap_issues.iterrows():
                insights_text += f"• {row['District']}: {row['Tree Gap']:.2f}% gap<br/>"
        
        elements.append(Paragraph(insights_text, styles['Normal']))
        
        elements.append(Spacer(1, 0.3*inch))
        elements.append(PageBreak())
        
        # ==================== TOP PERFORMERS ====================
        elements.append(Paragraph("TOP 10 BEST PERFORMING DISTRICTS", heading_style))
        elements.append(Spacer(1, 0.2*inch))
        
        top_10 = self.district_summary.head(10)
        top_data = [['Rank', 'District', 'Notification %', 'Schools', 'Notified', 'Category']]
        
        for idx, (_, row) in enumerate(top_10.iterrows(), 1):
            top_data.append([
                str(idx),
                row['District'],
                f"{row['Notification %']:.2f}%",
                str(int(row['Total Schools'])),
                str(int(row['Notification Uploaded'])),
                row['Category']
            ])
        
        top_table = Table(top_data, colWidths=[0.8*inch, 1.8*inch, 1.3*inch, 0.9*inch, 0.9*inch, 1.3*inch])
        top_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#27AE60')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        elements.append(top_table)
        
        elements.append(Spacer(1, 0.3*inch))
        elements.append(PageBreak())
        
        # ==================== CRITICAL DISTRICTS REQUIRING INTERVENTION ====================
        elements.append(Paragraph("BOTTOM 25 DISTRICTS - CRITICAL INTERVENTION REQUIRED", heading_style))
        elements.append(Spacer(1, 0.2*inch))
        
        bottom_25 = self.district_summary.tail(25)
        bottom_data = [['District', 'Notification %', 'Gap %', 'Schools', 'Notified', 'Priority']]
        
        for _, row in bottom_25.iterrows():
            gap = 100 - row['Notification %']
            if row['Notification %'] < 20:
                priority = '🔴 CRITICAL'
            elif row['Notification %'] < 30:
                priority = '🔴 HIGH'
            else:
                priority = '🟠 MEDIUM'
            
            bottom_data.append([
                row['District'],
                f"{row['Notification %']:.2f}%",
                f"{gap:.2f}%",
                str(int(row['Total Schools'])),
                str(int(row['Notification Uploaded'])),
                priority
            ])
        
        bottom_table = Table(bottom_data, colWidths=[1.8*inch, 1.3*inch, 1.2*inch, 0.9*inch, 0.9*inch, 1.3*inch])
        bottom_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8B0000')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        elements.append(bottom_table)
        
        elements.append(PageBreak())
        
        # ==================== ACTION PLAN ====================
        elements.append(Paragraph("STRATEGIC ACTION PLAN", heading_style))
        elements.append(Spacer(1, 0.2*inch))
        
        action_text = """
        <b>🎯 IMPLEMENTATION TIMELINE & ACCOUNTABILITY:</b><br/><br/>
        
        <b>🔴 CRITICAL (< 20% Completion) - IMMEDIATE ACTION:</b><br/>
        • Week 1: Mobilization of senior officials to district<br/>
        • Week 1-2: Root cause analysis and barrier identification<br/>
        • Week 2-3: Resource deployment and capacity building<br/>
        • Daily: Progress monitoring and reporting<br/>
        • Target: 50% completion by Week 4<br/>
        <br/>
        
        <b>🔴 HIGH PRIORITY (20-30% Completion):</b><br/>
        • Week 1: District coordination meeting<br/>
        • Week 1-2: Barrier removal and support<br/>
        • Bi-weekly: Progress tracking<br/>
        • Target: 70% completion by Week 8<br/>
        <br/>
        
        <b>🟠 MEDIUM PRIORITY (30-60% Completion):</b><br/>
        • Week 1: Support and guidance<br/>
        • Weekly: Progress monitoring<br/>
        • Monthly: Review and resource allocation<br/>
        • Target: 85% completion by Week 12<br/>
        <br/>
        
        <b>🟡 GOOD PERFORMERS (60-75%):</b><br/>
        • Bi-weekly: Support and guidance<br/>
        • Monthly: Performance review<br/>
        • Best practice documentation<br/>
        • Target: Achieve 85%+ by Month 3<br/>
        <br/>
        
        <b>🟢 EXCELLENT PERFORMERS (≥75%):</b><br/>
        • Monthly: Appreciation and recognition<br/>
        • Leadership role in mentoring other districts<br/>
        • Best practice sharing platform<br/>
        • Target: Maintain and sustain excellence<br/>
        <br/>
        
        <b>📋 ACCOUNTABILITY MATRIX:</b><br/>
        • District Education Officer: Weekly reporting<br/>
        • Block Coordinators: Bi-weekly field visits<br/>
        • State Level: Monthly review meetings<br/>
        • Data validation: Real-time dashboard access<br/>
        """
        
        elements.append(Paragraph(action_text, styles['Normal']))
        
        elements.append(PageBreak())
        
        # ==================== ALL DISTRICTS SUMMARY ====================
        elements.append(Paragraph("COMPLETE DISTRICT-WISE SUMMARY", heading_style))
        elements.append(Spacer(1, 0.15*inch))
        
        all_data = [['District', 'Schools', 'Notified', 'Notif %', 'Saplings', 'Tree Upload %', 'Category']]
        
        for _, row in self.district_summary.iterrows():
            all_data.append([
                row['District'][:20],  # Truncate long names
                str(int(row['Total Schools'])),
                str(int(row['Notification Uploaded'])),
                f"{row['Notification %']:.1f}%",
                str(int(row['Total Saplings'])),
                f"{row['Tree Upload %']:.1f}%",
                row['Category']
            ])
        
        all_table = Table(all_data, colWidths=[1.4*inch, 0.8*inch, 0.8*inch, 0.9*inch, 0.9*inch, 1.0*inch, 1.2*inch])
        all_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5aa0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        elements.append(all_table)
        
        elements.append(PageBreak())
        
        # ==================== FOOTER ====================
        elements.append(Spacer(1, 0.8*inch))
        
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#1f4788'),
            alignment=1,
        )
        
        footer_text = Paragraph(
            "<b>For live updates and detailed information, visit:</b><br/>"
            "<a href='https://ecoclubup.streamlit.app/' color='blue'>https://ecoclubup.streamlit.app/</a><br/>"
            f"Report Generated: {current_time.strftime('%d-%m-%Y %H:%M:%S')}",
            footer_style
        )
        elements.append(footer_text)
        
        # Build PDF
        print(f"Creating comprehensive PDF: {output_file}")
        doc.build(elements)
        print(f"[OK] Comprehensive PDF created: {output_file}")
        print(f"File size: {os.path.getsize(output_file) / 1024:.2f} KB")
        
        return output_file


if __name__ == "__main__":
    from data_service import DataService
    
    data_service = DataService(data_folder=".")
    df, success, error_msg = data_service.load_data()
    
    if success:
        # Try to load tree data if available
        tree_df = None
        try:
            tree_df = pd.read_csv('Tree_Data.csv')
            print(f"Tree data loaded: {len(tree_df)} records")
        except:
            print("Tree data not available - will generate report without tree integration")
        
        # Generate comprehensive report
        report = ComprehensiveEcoReport(df, tree_df)
        report.generate_pdf('Comprehensive_Eco_Club_Report.pdf')
    else:
        print(f"Error: {error_msg}")
