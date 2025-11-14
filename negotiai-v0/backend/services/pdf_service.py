# backend/services/pdf_service.py
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from datetime import datetime
import os

class PDFService:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#667eea'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))

        # Section header
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#764ba2'),
            spaceBefore=20,
            spaceAfter=12
        ))

        # Body text
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['BodyText'],
            fontSize=11,
            alignment=TA_JUSTIFY,
            spaceAfter=12
        ))

    async def generate_strategy_pdf(self, strategy, context, output_path: str) -> str:
        """Generate PDF report for negotiation strategy"""
        os.makedirs("exports", exist_ok=True)
        filepath = f"exports/{output_path}"

        doc = SimpleDocTemplate(filepath, pagesize=A4)
        story = []

        # Title
        title = Paragraph("🎯 Negotiation Strategy Report", self.styles['CustomTitle'])
        story.append(title)
        story.append(Spacer(1, 0.3*inch))

        # Date
        date = Paragraph(
            f"<i>Generated on {datetime.now().strftime('%B %d, %Y at %H:%M')}</i>",
            self.styles['Normal']
        )
        story.append(date)
        story.append(Spacer(1, 0.4*inch))

        # Context Summary
        story.append(Paragraph("📋 Negotiation Context", self.styles['SectionHeader']))
        story.append(Paragraph(f"<b>Objective:</b> {context.objective}", self.styles['CustomBody']))
        story.append(Paragraph(f"<b>Minimum Acceptable:</b> {context.minimum_acceptable}", self.styles['CustomBody']))
        if context.counterparty_name:
            story.append(Paragraph(f"<b>Counterparty:</b> {context.counterparty_name}", self.styles['CustomBody']))
        story.append(Spacer(1, 0.3*inch))

        # Strategy Summary
        story.append(Paragraph("📊 Strategy Summary", self.styles['SectionHeader']))
        story.append(Paragraph(strategy.summary, self.styles['CustomBody']))
        story.append(Spacer(1, 0.3*inch))

        # Opening Position
        story.append(Paragraph("🎬 Opening Position", self.styles['SectionHeader']))
        story.append(Paragraph(strategy.opening_position, self.styles['CustomBody']))
        story.append(Spacer(1, 0.3*inch))

        # Key Arguments
        story.append(Paragraph("💪 Key Arguments", self.styles['SectionHeader']))
        for i, arg in enumerate(strategy.key_arguments, 1):
            story.append(Paragraph(f"{i}. {arg}", self.styles['CustomBody']))
        story.append(Spacer(1, 0.3*inch))

        # Concession Plan
        story.append(Paragraph("🔄 Concession Plan", self.styles['SectionHeader']))
        for i, step in enumerate(strategy.concession_plan, 1):
            story.append(Paragraph(f"Step {i}: {step}", self.styles['CustomBody']))
        story.append(Spacer(1, 0.3*inch))

        # Red Lines
        story.append(Paragraph("🚫 Red Lines (DO NOT CROSS)", self.styles['SectionHeader']))
        for line in strategy.red_lines:
            story.append(Paragraph(f"• {line}", self.styles['CustomBody']))
        story.append(Spacer(1, 0.3*inch))

        # Expected Objections
        story.append(Paragraph("🛡️ Expected Objections & Counters", self.styles['SectionHeader']))
        for obj in strategy.expected_objections:
            story.append(Paragraph(
                f"<b>Objection:</b> \"{obj.objection}\"",
                self.styles['CustomBody']
            ))
            story.append(Paragraph(
                f"<b>Counter:</b> {obj.counter_argument}",
                self.styles['CustomBody']
            ))
            story.append(Paragraph(
                f"<i>Confidence: {int(obj.confidence * 100)}%</i>",
                self.styles['Normal']
            ))
            story.append(Spacer(1, 0.2*inch))

        # BATNA
        story.append(Paragraph("🏃 BATNA (Best Alternative)", self.styles['SectionHeader']))
        story.append(Paragraph(strategy.batna, self.styles['CustomBody']))

        # Build PDF
        doc.build(story)
        return filepath

    async def generate_analysis_pdf(self, analysis, strategy, output_path: str) -> str:
        """Generate PDF report for negotiation analysis"""
        os.makedirs("exports", exist_ok=True)
        filepath = f"exports/{output_path}"

        doc = SimpleDocTemplate(filepath, pagesize=A4)
        story = []

        # Title
        title = Paragraph("📊 Negotiation Performance Analysis", self.styles['CustomTitle'])
        story.append(title)
        story.append(Spacer(1, 0.3*inch))

        # Date
        date = Paragraph(
            f"<i>Generated on {datetime.now().strftime('%B %d, %Y at %H:%M')}</i>",
            self.styles['Normal']
        )
        story.append(date)
        story.append(Spacer(1, 0.4*inch))

        # Performance Scores
        story.append(Paragraph("🎯 Performance Scores", self.styles['SectionHeader']))

        scores_data = [
            ['Metric', 'Score'],
            ['Overall Performance', f"{analysis.performance.overall_score}/100"],
            ['Preparation', f"{analysis.performance.preparation_score}/100"],
            ['Tactics Execution', f"{analysis.performance.tactics_score}/100"],
            ['Outcome Achievement', f"{analysis.performance.outcome_score}/100"],
        ]

        scores_table = Table(scores_data, colWidths=[3*inch, 2*inch])
        scores_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(scores_table)
        story.append(Spacer(1, 0.4*inch))

        # Tactics Detected
        story.append(Paragraph("🎯 Tactics Detected", self.styles['SectionHeader']))
        for tactic in analysis.tactics_used:
            story.append(Paragraph(
                f"<b>{tactic.tactic_name}</b> ({tactic.tactic_type})",
                self.styles['CustomBody']
            ))
            story.append(Paragraph(
                f"<i>Quote: \"{tactic.quote}\"</i>",
                self.styles['Normal']
            ))
            story.append(Paragraph(
                f"Effectiveness: {tactic.effectiveness}",
                self.styles['Normal']
            ))
            story.append(Paragraph(
                f"{tactic.explanation}",
                self.styles['CustomBody']
            ))
            story.append(Spacer(1, 0.2*inch))

        # Strengths
        story.append(PageBreak())
        story.append(Paragraph("✅ Strengths", self.styles['SectionHeader']))
        for strength in analysis.strengths:
            story.append(Paragraph(f"• {strength}", self.styles['CustomBody']))
        story.append(Spacer(1, 0.3*inch))

        # Weaknesses
        story.append(Paragraph("⚠️ Areas for Improvement", self.styles['SectionHeader']))
        for weakness in analysis.weaknesses:
            story.append(Paragraph(f"• {weakness}", self.styles['CustomBody']))
        story.append(Spacer(1, 0.3*inch))

        # Recommendations
        story.append(Paragraph("💡 Key Recommendations", self.styles['SectionHeader']))
        for i, rec in enumerate(analysis.key_recommendations, 1):
            story.append(Paragraph(f"{i}. {rec}", self.styles['CustomBody']))

        # Build PDF
        doc.build(story)
        return filepath
