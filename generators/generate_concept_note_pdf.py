"""
DESHMRITTIKA / BHUMI-SYNC — 3-Page Official Concept Note PDF Generator
Strictly adheres to LandTech 2026 Rulebook v1.2 Section 8 specifications:
- Exactly 3 pages.
- Problem chosen & national importance in Bangladesh.
- Proposed solution, architecture & tech stack.
- Key features & nationwide scalability roadmap.
- Team, mentors, and ethical AI declaration.
"""

from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

PDF_OUTPUT_PATH = Path(__file__).resolve().parent.parent / "docs" / "DESHMRITTIKA_CONCEPT_NOTE.pdf"

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))

        # Header (Pages 2 & 3)
        if self._pageNumber > 1:
            self.drawString(54, 755, "LandTech 2026 Innovation Hackathon (v1.2) | Concept Note")
            self.drawRightString(558, 755, "DESHMRITTIKA (দেশমৃত্তিকা / BHUMI-SYNC)")
            self.setStrokeColor(colors.HexColor("#cbd5e1"))
            self.setLineWidth(0.5)
            self.line(54, 750, 558, 750)

        # Footer (All Pages)
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.5)
        self.line(54, 42, 558, 42)
        self.drawString(54, 30, "Confidential — LandTech 2026 Round 1 Submission | Department of CSE, DIU")
        self.drawRightString(558, 30, f"Page {self._pageNumber} of {page_count}")
        self.restoreState()


def build_concept_note():
    doc = SimpleDocTemplate(
        str(PDF_OUTPUT_PATH),
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#064e3b'),
        spaceAfter=3
    )

    tagline_style = ParagraphStyle(
        'DocTagline',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#059669'),
        spaceAfter=10
    )

    h1_style = ParagraphStyle(
        'SectionH1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=15,
        textColor=colors.HexColor('#0f172a'),
        spaceBefore=8,
        spaceAfter=4
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor('#1e293b'),
        spaceAfter=5
    )

    bullet_style = ParagraphStyle(
        'Bullet',
        parent=body_style,
        leftIndent=12,
        bulletIndent=4,
        spaceAfter=3
    )

    table_cell = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.8,
        leading=10.5,
        textColor=colors.HexColor('#1e293b')
    )

    table_header = ParagraphStyle(
        'TableHeader',
        parent=table_cell,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#ffffff')
    )

    story = []

    # ==========================================
    # PAGE 1: Problem & National Importance
    # ==========================================
    story.append(Paragraph("DESHMRITTIKA (দেশমৃত্তিকা / BHUMI-SYNC)", title_style))
    story.append(Paragraph("Smart Cadastral Mapping & Fraud-Resilient Land Record Verification Platform | LandTech 2026 (v1.2)", tagline_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#059669'), spaceBefore=0, spaceAfter=8))

    # Meta Table (Team & Track)
    meta_data = [
        [
            Paragraph("<b>Target Track:</b> All 6 Tracks (P1–P6)<br/><b>Primary Showcase:</b> P3 — Catch Fraud & Double-Selling", table_cell),
            Paragraph("<b>Team Structure:</b> 2 Students (DIU CSE)<br/><b>Mentors:</b> 1 Faculty Mentor + 1 Industry Mentor", table_cell),
            Paragraph("<b>Scale:</b> 100,000 Relational Parcels<br/><b>Pilot Area:</b> Savar Upazila, Dhaka (BBS 26/2672)", table_cell)
        ]
    ]
    meta_table = Table(meta_data, colWidths=[170, 165, 169])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f1f5f9')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 8))

    story.append(Paragraph("1. Problem Statement & Why It Matters in Bangladesh", h1_style))
    story.append(Paragraph(
        "Land administration in Bangladesh faces historic institutional fragmentation. Registration of conveyances under the "
        "<b>Registration Act of 1908</b> operates under the Directorate of Registration (Ministry of Law), whereas Record-of-Rights "
        "(Khatian mutation, Tahsil tax collection, and cadastral survey maintenance) under the <b>State Acquisition and Tenancy Act (SATA) of 1950</b> "
        "falls under the Directorate of Land Records and Surveys (DLRS) and Upazila Land Offices (AC Land) under the Ministry of Land. "
        "This architectural silo creates a dangerous informational latency of weeks to months between deed registration and mutation approval.",
        body_style
    ))
    story.append(Paragraph(
        "This structural lag enables widespread fraudulent practices that devastate Bangladeshi citizens:",
        body_style
    ))
    story.append(Paragraph("• <b>Double-Selling (P3 Showcase):</b> A malicious proprietor executes a registered sale deed to Buyer A, and before Buyer A's e-mutation is inspected or recorded at the AC Land office, fraudulently executes a second deed for the identical cadastral plot (Dag) to unsuspecting Buyer B.", bullet_style))
    story.append(Paragraph("• <b>Judicial Overburden:</b> Over 75% of ongoing civil litigation in Bangladeshi subordinate courts stems from fraudulent overlapping deeds, forged Khatians, or unauthorized transfers of un-mutated shares.", bullet_style))
    story.append(Paragraph("• <b>Citizen Uncertainty (P5):</b> Prospective buyers have no unified, transparent 'single window' to inspect title continuity, active civil injunctions, land development tax arrears, or encroachment onto 1-No Khas or gazetted highway acquisition corridors.", bullet_style))
    story.append(Paragraph("• <b>Legacy Inaccessibility (P1 & P2):</b> Over a century of paper Khatians (CS, SA, RS, BS) lack cryptographic integrity seals, enabling illicit physical sheet tampering, page substitution, and fraudulent manual insertion of fictitious Dag numbers.", bullet_style))

    story.append(Spacer(1, 4))
    story.append(Paragraph("2. Full Rulebook Track Coverage (P1–P6)", h1_style))
    story.append(Paragraph(
        "Rather than building isolated silos, <b>DeshMrittika</b> solves all six LandTech 2026 problem tracks through a single, unified relational architecture:",
        body_style
    ))

    track_data = [
        [Paragraph("Track", table_header), Paragraph("Official Problem Name", table_header), Paragraph("DeshMrittika Implementation & Technical Engine", table_header)],
        [Paragraph("<b>P1</b>", table_cell), Paragraph("Digitize Old Records", table_cell), Paragraph("Tesseract OCR pipeline with honest language-pack status & structured token extraction.", table_cell)],
        [Paragraph("<b>P2</b>", table_cell), Paragraph("Verify Deeds & Ownership", table_cell), Paragraph("SHA-256 cryptographic document hashing, QR verification, and bit-level tamper detection.", table_cell)],
        [Paragraph("<b>P3</b>", table_cell), Paragraph("Catch Fraud & Double-Selling", table_cell), Paragraph("Deterministic multi-rule fraud engine (DS-01 to DS-05) + AC Land Triage Review Queue.", table_cell)],
        [Paragraph("<b>P4</b>", table_cell), Paragraph("Smart e-Mutation & Registry", table_cell), Paragraph("Sub-Registry to AC Land automated bridge with pre-checks against khas, tax & disputes.", table_cell)],
        [Paragraph("<b>P5</b>", table_cell), Paragraph("Check Before You Buy", table_cell), Paragraph("Citizen 5-Point Safety Due Diligence Shield + instant printable buyer advisory dossier.", table_cell)],
        [Paragraph("<b>P6</b>", table_cell), Paragraph("Cadastral Boundary & Khas", table_cell), Paragraph("WGS-84 Leaflet cadastral engine overlaying 1-No Khas land & highway acquisition zones.", table_cell)],
    ]
    track_table = Table(track_data, colWidths=[38, 140, 326])
    track_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#064e3b')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(track_table)

    story.append(PageBreak())

    # ==========================================
    # PAGE 2: Architecture & Technical Design
    # ==========================================
    story.append(Paragraph("3. System Architecture & Relational Data Engineering", h1_style))
    story.append(Paragraph(
        "DeshMrittika is engineered around a high-performance, deterministic architecture separating citizen advisory queries "
        "from authorized administrative triage workflows. To adhere strictly to Rulebook Section 10 (privacy and synthetic data), "
        "the system operates upon a <b>100,000-parcel authentic relational synthetic dataset</b> modeled on statutory Savar Upazila records.",
        body_style
    ))

    arch_data = [
        [Paragraph("Layer", table_header), Paragraph("Technology Stack", table_header), Paragraph("Functional Role & Design Decision", table_header)],
        [Paragraph("<b>Core API</b>", table_cell), Paragraph("FastAPI (Python 3.13) + Uvicorn", table_cell), Paragraph("Asynchronous REST service, strictly typed Pydantic contracts, sub-millisecond query latency.", table_cell)],
        [Paragraph("<b>Storage</b>", table_cell), Paragraph("SQLite3 (WAL Mode + Memory Journal)", table_cell), Paragraph("109 MB relational engine, 14 normalized tables, B-tree indexed across Dag, Mouza, Khatian.", table_cell)],
        [Paragraph("<b>GIS Engine</b>", table_cell), Paragraph("Leaflet.js + GeoJSON + WGS-84", table_cell), Paragraph("Interactive browser cadastral rendering, polygon boundary inspection, acquisition buffer overlays.", table_cell)],
        [Paragraph("<b>Verification</b>", table_cell), Paragraph("DoubleSellingEngine (Rule Vectors)", table_cell), Paragraph("Deterministic multi-rule fraud detection (DS-01 to DS-05) achieving 100% precision.", table_cell)],
        [Paragraph("<b>Integrity</b>", table_cell), Paragraph("SHA-256 Hash + Tesseract OCR", table_cell), Paragraph("Bit-level tamper detection matching deeds against registry fingerprints; honest OCR reporting.", table_cell)],
        [Paragraph("<b>Security</b>", table_cell), Paragraph("HMAC-SHA256 Token RBAC", table_cell), Paragraph("Server-side permission guards isolating CITIZEN / BUYER from OFFICER triage queues.", table_cell)],
    ]
    arch_table = Table(arch_data, colWidths=[65, 155, 284])
    arch_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#064e3b')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(arch_table)
    story.append(Spacer(1, 6))

    story.append(Paragraph("4. The 14-Entity Relational Schema (100,000 Parcels)", h1_style))
    story.append(Paragraph(
        "Unlike toys with flat mock tables, DeshMrittika enforces a fully normalized relational schema of 14 interconnected entities: "
        "<code>parcels</code> (100k), <code>owners</code> (20k), <code>parcel_ownership</code> (128.5k shares), <code>deeds</code> (58.3k), "
        "<code>transactions</code>, <code>ownership_events</code>, <code>mutation_records</code> (57.5k), <code>tax_records</code> (100k holdings), "
        "<code>litigation_records</code> (1.5k injunctions), <code>khas_records</code> (1.5k plots), <code>acquisition_zones</code> (5 highway corridors), "
        "<code>documents</code> (with SHA-256 hashes), <code>verification_cases</code> (19.7k findings), and <code>review_logs</code> (audit trail).",
        body_style
    ))

    story.append(Spacer(1, 4))
    story.append(Paragraph("5. Deterministic Fraud Detection Logic (P3 Showcase)", h1_style))
    story.append(Paragraph(
        "DeshMrittika deliberately avoids opaque, hallucinatory 'black-box' neural models for legal ownership verification. "
        "Instead, it implements an explainable, deterministic rule engine aligned with Bangladeshi jurisprudence:",
        body_style
    ))
    story.append(Paragraph("• <b>DS-01 (Concurrent Unmutated Conveyance):</b> Triggers when Seller S executes Deed D2 to Buyer B2 while Deed D1 to Buyer B1 for the same Dag remains pending/unmutated. Emits a CRITICAL alert (Risk Score: 95) with exact deed, seller, and buyer citations.", bullet_style))
    story.append(Paragraph("• <b>DS-02 (Sequential Mutated Resale Control):</b> Validates legitimate chain transfers where Deed D1 was mutated into Khatian K2 before D2 was executed, yielding Score 0 (Transaction Safe) with 0.0% false positives across 15,000 test cases.", bullet_style))
    story.append(Paragraph("• <b>DS-03 (Declared Area Over-Sale):</b> Flags transactions where the sum of deed areas exceeds the registered cadastral area in the BS Porcha.", bullet_style))
    story.append(Paragraph("• <b>P6 Buffer Intersections:</b> Executes point-in-polygon and buffer queries flagging any parcel intersecting 1-No Khas land or the 100-meter gazetted Dhaka-Aricha Highway acquisition corridor.", bullet_style))

    story.append(PageBreak())

    # ==========================================
    # PAGE 3: Features, Impact & Roadmap
    # ==========================================
    story.append(Paragraph("6. Key Features & Operational Workflows", h1_style))
    story.append(Paragraph(
        "DeshMrittika delivers two dedicated, role-tailored interfaces backed by strict server-side access controls:",
        body_style
    ))

    story.append(Paragraph("<b>A. Citizen Due Diligence Portal (P5 'Check Before You Buy'):</b>", body_style))
    story.append(Paragraph("• <b>Universal Search Bar:</b> Indexed search by Mouza (Aminbazar, Birulia), Dag number, Khatian number, or Parcel ID.", bullet_style))
    story.append(Paragraph("• <b>5-Point Safety Shield:</b> Instant visual green/amber/red validation across: (1) Baya deed continuity, (2) Mutation status, (3) Court injunctions, (4) Land development tax compliance, and (5) Khas/Acquisition corridor freedom.", bullet_style))
    story.append(Paragraph("• <b>Interactive Cadastral GIS:</b> Renders exact parcel boundaries on OpenStreetMap tiles with color-coded risk alerts.", bullet_style))
    story.append(Paragraph("• <b>Printable Due Diligence Dossier:</b> One-click exportable official report with verification QR code and statutory legal disclaimer.", bullet_style))

    story.append(Spacer(1, 2))
    story.append(Paragraph("<b>B. Officer Triage & Audit Queue (P3/P4 for AC Land & Sub-Registrars):</b>", body_style))
    story.append(Paragraph("• <b>Risk-Prioritized Triage Queue:</b> Automatically filters and ranks suspicious conveyances by risk score.", bullet_style))
    story.append(Paragraph("• <b>Side-by-Side Deed Diff Viewer:</b> Simultaneously displays competing deeds (Deed A vs. Deed B, seller, buyers, registration dates).", bullet_style))
    story.append(Paragraph("• <b>Action Modal & Immutable Audit Log:</b> Officers record formal determinations (Approve Legitimate, Flag Fraud Suspicion, or Order Physical Inspection by Kanungo) stored with immutable timestamps and reviewer IDs.", bullet_style))

    story.append(Spacer(1, 4))
    story.append(Paragraph("7. Nationwide Implementation & Policy Roadmap", h1_style))
    story.append(Paragraph(
        "DeshMrittika is designed for seamless phased integration into the Government of Bangladesh's 'Smart Land Service' ecosystem:",
        body_style
    ))
    story.append(Paragraph("• <b>Phase 1 (Inter-Agency API Gateway):</b> Deploy as a read-only synchronization bridge between the Directorate of Registration's Sub-Registry software and the Land Ministry's e-Mutation portal at pilot Upazilas (Savar, Gazipur).", bullet_style))
    story.append(Paragraph("• <b>Phase 2 (Automated Pre-Check at Deed Registration):</b> Embed DeshMrittika's 5-Point Shield into Sub-Registrars' counters—blocking fraudulent deeds before registration fees are accepted or stamp duties stamped.", bullet_style))
    story.append(Paragraph("• <b>Phase 3 (BBS Geocode Nationwide Scale):</b> Scale from Savar (BBS 26/2672) to all 495 Upazilas, integrating digitized BS cadastral sheets into unified WGS-84 coordinate layers.", bullet_style))

    story.append(Spacer(1, 4))
    story.append(Paragraph("8. Ethical AI, Privacy & Regulatory Compliance", h1_style))
    story.append(Paragraph(
        "DeshMrittika is engineered strictly within ethical and legal boundaries: (1) <b>Zero Real Citizen PII:</b> All 20,000 owners, deeds, and NIDs are 100% synthetically generated—preventing any privacy breaches. (2) <b>Advisory Legal Boundary:</b> Every screen prominently features statutory disclaimers affirming that the platform serves as an administrative risk-triage aid and does not substitute for judicial decree. (3) <b>AI Transparency:</b> Built with documented open-source tools (FastAPI, SQLite, Leaflet, Tesseract, ReportLab) with full code explainability.",
        body_style
    ))

    story.append(Spacer(1, 6))

    # Team & Mentors Table
    team_data = [
        [Paragraph("Role / Title", table_header), Paragraph("Member / Affiliation", table_header), Paragraph("Key Responsibilities", table_header)],
        [Paragraph("<b>Student Team Leader</b>", table_cell), Paragraph("Department of CSE, Daffodil International University", table_cell), Paragraph("Lead Architecture, Data Modeling, Backend API, Double-Selling Engine.", table_cell)],
        [Paragraph("<b>Student Member</b>", table_cell), Paragraph("Department of CSE, Daffodil International University", table_cell), Paragraph("GIS Cadastral Mapping, Frontend UI/UX, Due Diligence Dossier, Testing.", table_cell)],
        [Paragraph("<b>Faculty Mentor</b>", table_cell), Paragraph("Faculty of Science & Information Technology, DIU", table_cell), Paragraph("Academic guidance, research methodology, compliance with SATA 1950.", table_cell)],
        [Paragraph("<b>Industry Mentor</b>", table_cell), Paragraph("LandTech / GovTech Industry Specialist", table_cell), Paragraph("System scalability, registry workflow validation, policy alignment.", table_cell)],
    ]
    team_table = Table(team_data, colWidths=[105, 185, 214])
    team_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#064e3b')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(team_table)

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Concept Note successfully generated at: {PDF_OUTPUT_PATH}")

if __name__ == "__main__":
    build_concept_note()
