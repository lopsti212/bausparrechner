"""
PDF-Export für Kundenberatungen.
ReportLab-basiert, mit Deckblatt, Eingaben, Ergebnistabellen und Chart-Bild.
"""

import io
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
)


PRIMARY_COLOR = colors.HexColor("#2e7d32")
SECONDARY_COLOR = colors.HexColor("#66bb6a")
ACCENT_COLOR = colors.HexColor("#c62828")


def _fmt_euro(betrag: float) -> str:
    s = f"{betrag:,.2f} €"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def erstelle_pdf(
    kunde_name: str,
    beratung_datum: str,
    eingaben: dict,
    ergebnis: dict,
    szenarien: list | None = None,
    stresstest: list | None = None,
    chart_bilder: list | None = None,
) -> bytes:
    """
    Erzeugt einen PDF-Report mit allen wichtigen Ergebnissen.
    chart_bilder: optional Liste von (title, png_bytes) für eingebettete Charts.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "Title", parent=styles["Title"],
        textColor=PRIMARY_COLOR, alignment=1, fontSize=22, spaceAfter=12,
    )
    h2_style = ParagraphStyle(
        "H2", parent=styles["Heading2"],
        textColor=PRIMARY_COLOR, fontSize=14, spaceBefore=16, spaceAfter=6,
    )
    normal = styles["Normal"]
    small = ParagraphStyle("Small", parent=normal, fontSize=9, textColor=colors.grey)

    story = []

    # Deckblatt
    story.append(Paragraph("Bauansparprogramm", title_style))
    story.append(Paragraph("Auswertung zur Kundenberatung", styles["Heading3"]))
    story.append(Spacer(1, 1 * cm))
    story.append(Paragraph(f"<b>Kunde:</b> {kunde_name or '—'}", normal))
    story.append(Paragraph(f"<b>Datum:</b> {beratung_datum}", normal))
    story.append(Spacer(1, 0.5 * cm))

    # Eingaben
    story.append(Paragraph("Ihre Eingaben", h2_style))
    eingabe_rows = [[k, v] for k, v in eingaben.items()]
    t_eingaben = Table(eingabe_rows, colWidths=[7 * cm, 9 * cm])
    t_eingaben.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f5f5f5")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t_eingaben)

    # Kern-Ergebnis
    story.append(Paragraph("Vergleich der Szenarien", h2_style))
    szen_a = ergebnis["szenario_a"]
    szen_b = ergebnis["szenario_b"]
    vergleich_data = [
        ["", "Ohne Bausparen", "Mit Bausparprogramm"],
        ["Darlehenshöhe", _fmt_euro(ergebnis["finanzierungssumme"]), _fmt_euro(ergebnis["restsumme_darlehen"])],
        ["Monatsrate", _fmt_euro(szen_a["monatsrate"]), _fmt_euro(szen_b["monatsrate"])],
        ["Zinskosten gesamt", _fmt_euro(szen_a["gesamt_zinsen"]), _fmt_euro(szen_b["gesamt_zinsen"])],
        ["Gesamtzahlung", _fmt_euro(szen_a["gesamt_zahlung"]), _fmt_euro(szen_b["gesamt_zahlung"])],
    ]
    t_vergleich = Table(vergleich_data, colWidths=[5 * cm, 5.5 * cm, 5.5 * cm])
    t_vergleich.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PRIMARY_COLOR),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t_vergleich)

    story.append(Spacer(1, 0.4 * cm))
    ersp = ergebnis["ersparnis_zinsen"]
    story.append(Paragraph(
        f"<b><font color='#2e7d32'>Ihre Zinsersparnis: {_fmt_euro(ersp)}</font></b>",
        styles["Heading3"]
    ))

    # Szenarien
    if szenarien:
        story.append(Paragraph("Auswirkung eines späteren Starts", h2_style))
        szen_rows = [["Start in Jahren", "Sparjahre", "Guthaben", "Monatsrate", "Verlust vs. sofort"]]
        for s in szenarien:
            szen_rows.append([
                f"+{s['start_in_jahren']} J.",
                f"{s['sparjahre']:.0f}",
                _fmt_euro(s["guthaben"]),
                _fmt_euro(s["monatsrate"]),
                _fmt_euro(s.get("verlust_vs_sofort", 0)),
            ])
        t_szen = Table(szen_rows, colWidths=[3 * cm, 2.5 * cm, 3.5 * cm, 3.5 * cm, 3.5 * cm])
        t_szen.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), PRIMARY_COLOR),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
            ("PADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(t_szen)

    # Stress-Test
    if stresstest:
        story.append(Paragraph("Zinsrisiko-Stresstest", h2_style))
        st_rows = [["Marktzins", "Rate ohne Bausparen", "Rate mit Bausparen", "Ersparnis"]]
        for s in stresstest:
            st_rows.append([
                f"{s['markt_zins']:.1f} %",
                _fmt_euro(s["rate_ohne_bausparen"]),
                _fmt_euro(s["rate_mit_bausparen"]),
                _fmt_euro(s["ersparnis"]),
            ])
        t_st = Table(st_rows, colWidths=[3 * cm, 4.5 * cm, 4.5 * cm, 4 * cm])
        t_st.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), ACCENT_COLOR),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
            ("PADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(t_st)

    # Charts
    if chart_bilder:
        story.append(PageBreak())
        story.append(Paragraph("Grafische Darstellung", h2_style))
        for titel, png in chart_bilder:
            story.append(Paragraph(f"<b>{titel}</b>", normal))
            img = Image(io.BytesIO(png), width=16 * cm, height=8 * cm)
            story.append(img)
            story.append(Spacer(1, 0.4 * cm))

    # Footer-Hinweise
    story.append(Spacer(1, 1 * cm))
    story.append(Paragraph(
        "Alle Berechnungen sind unverbindliche Modellrechnungen auf Basis Ihrer Eingaben. "
        "Die tatsächlichen Konditionen richten sich nach dem verbindlichen Angebot der Bausparkasse bzw. des Finanzierungspartners.",
        small
    ))
    story.append(Paragraph(
        f"Erstellt am {datetime.now().strftime('%d.%m.%Y %H:%M')} · © Jan Glänzer",
        small
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
