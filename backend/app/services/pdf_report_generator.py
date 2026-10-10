import io
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable

def generate_credit_assessment_pdf(analysis_data: dict, borrower_name: str, application_id: str) -> bytes:
    """
    Generates a professional PDF Credit Assessment & SHAP Explanation Report
    using ReportLab.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#102A43')
    )

    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#64748B')
    )

    h2_style = ParagraphStyle(
        'Heading2Custom',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#102A43'),
        spaceBefore=12,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        'BodyCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#1E293B')
    )

    story = []

    # Header
    story.append(Paragraph("CREDENCE AI — Alternative Credit Insights", title_style))
    story.append(Paragraph("Explainable Credit Assessment & SHAP Underwriting Report", subtitle_style))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0F766E'), spaceBefore=0, spaceAfter=12))

    # Meta Info Table
    pred = analysis_data.get("prediction", {})
    cashflow = analysis_data.get("cashflow", {})
    policy = analysis_data.get("loan_policy", {})
    data_meta = analysis_data.get("data", {})
    affordability = policy.get("affordability", {})

    meta_data = [
        [
            Paragraph("<b>Applicant Case:</b> " + borrower_name, body_style),
            Paragraph("<b>Application ID:</b> " + application_id, body_style)
        ],
        [
            Paragraph("<b>Assessment Date:</b> " + datetime.now().strftime("%Y-%m-%d %H:%M"), body_style),
            Paragraph("<b>Model Version:</b> " + analysis_data.get("model_version", "credence_gb_v1"), body_style)
        ]
    ]

    meta_table = Table(meta_data, colWidths=[270, 270])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#E2E8F0')),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 12))

    # Executive Score & Risk Summary
    story.append(Paragraph("1. Executive Credit Assessment", h2_style))
    score_val = pred.get("score", 600)
    default_prob = round(pred.get("default_probability", 0.0) * 100, 1)
    quality = data_meta.get("data_confidence", "Medium")

    summary_rows = [
        ["Alternative Credit Score", "Est. Default Probability", "Data Quality Rating", "Underwriting Recommendation"],
        [f"{score_val} / 900", f"{default_prob}%", quality, policy.get("recommendation_status", "Under Review")]
    ]
    summary_table = Table(summary_rows, colWidths=[135, 135, 135, 135])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#102A43')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#F1F5F9')),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 12))

    # Cash Flow & Affordability Analysis
    story.append(Paragraph("2. Cash Flow & Loan Affordability Metrics", h2_style))
    cash_rows = [
        ["Metric Description", "Value (INR ₹)", "Underwriting Significance"],
        ["Gross Monthly Business Inflow", f"₹{cashflow.get('gross_business_inflow_monthly', 0):,.2f}", "Total monthly revenue credits"],
        ["Estimated Monthly Outflow", f"₹{cashflow.get('estimated_business_outflow_monthly', 0):,.2f}", "Operating costs & recurring debits"],
        ["Stable Monthly Net Cash Flow", f"₹{cashflow.get('stable_monthly_cash_flow', 0):,.2f}", "Median net disposable cash flow"],
        ["Lean Month Cash Flow", f"₹{cashflow.get('lean_month_cash_flow', 0):,.2f}", "Conservative seasonal cash flow floor"],
        ["Requested Loan Amount", f"₹{policy.get('requested_amount', 0):,.2f}", "Applicant requested principal"],
        ["Recommended Loan Amount", f"₹{policy.get('recommended_amount', 0):,.2f}", "Capacity capped recommendation"],
        ["Estimated Monthly EMI (12m @ 14%)", f"₹{affordability.get('estimated_emi_monthly', 0):,.2f}", "Calculated monthly debt service"],
        ["Debt Service Coverage Ratio (DSCR)", f"{affordability.get('dscr', 0.0)}x", "Net cash flow to EMI ratio (>= 1.25x target)"]
    ]
    cash_table = Table(cash_rows, colWidths=[200, 140, 200])
    cash_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F766E')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8.5),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
    ]))
    story.append(cash_table)
    story.append(Spacer(1, 12))

    # SHAP Explanations
    story.append(Paragraph("3. SHAP TreeExplainer Contribution Waterfall", h2_style))
    explanations = analysis_data.get("explanations", [])
    exp_rows = [["Feature Name", "Value", "Score Contribution", "Explanation Direction", "Borrower Friendly Explanation"]]
    
    for exp in explanations:
        is_pos = exp.get("contribution", 0) >= 0
        contrib_str = f"+{exp.get('contribution', 0):.1f} pts" if is_pos else f"{exp.get('contribution', 0):.1f} pts"
        dir_str = "Supports Score" if is_pos else "Elevates Risk"
        exp_rows.append([
            exp.get("feature_name", "").replace("_", " ").title(),
            str(exp.get("feature_value", "")),
            contrib_str,
            dir_str,
            Paragraph(exp.get("borrower_text", ""), body_style)
        ])

    exp_table = Table(exp_rows, colWidths=[120, 60, 80, 80, 200])
    exp_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E3A5F')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
    ]))
    story.append(exp_table)
    story.append(Spacer(1, 12))

    # Fraud & Data Integrity Flags
    fraud_flags = analysis_data.get("fraud_flags", [])
    if fraud_flags:
        story.append(Paragraph("4. Data Integrity & Heuristic Flags", h2_style))
        flag_rows = [["Flag Type", "Severity Level", "Evidence Summary"]]
        for ff in fraud_flags:
            flag_rows.append([
                ff.get("flag_type", ""),
                ff.get("severity", ""),
                Paragraph(ff.get("evidence_summary", ""), body_style)
            ])
        flag_table = Table(flag_rows, colWidths=[150, 90, 300])
        flag_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#B45309')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('PADDING', (0, 0), (-1, -1), 5),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ]))
        story.append(flag_table)
        story.append(Spacer(1, 12))

    # Disclaimer Footer
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#CBD5E1'), spaceBefore=8, spaceAfter=8))
    story.append(Paragraph("<b>Notice:</b> Model trained on synthetic data for decision-support evaluation. All generated outputs require human underwriting review before final loan approval.", subtitle_style))

    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
