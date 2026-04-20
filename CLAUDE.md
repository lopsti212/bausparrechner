# Bausparrechner — Bauansparprogramm

## Projektübersicht
Web-App zur Darstellung des Bauansparprogramm-Vorteils für Vertriebsberater in Finanzierungs-/Kundengesprächen. Vergleicht Direktfinanzierung mit der Kombination Bausparen + Finanzierung zur Ausnutzung des niedrigeren garantierten Bauspar-Darlehenszinses.

## Technologie-Stack
- **Framework**: Streamlit
- **Grafiken**: Plotly
- **PDF-Export**: ReportLab
- **Deployment**: Streamlit Cloud

## Starten
```bash
cd ~/bausparrechner
pip install -r requirements.txt
streamlit run app.py
```

## Kernlogik
- **Szenario A** (ohne Bausparen): volle Finanzierungssumme zum erwarteten Marktzins.
- **Szenario B** (mit Bausparen): Vorsparen bis zum Finanzierungsstart → Guthaben als Eigenkapital → Restsumme zum garantierten Bauspar-Darlehenszins.
- Ersparnis = Zinskosten(A) − Zinskosten(B).

## Features
1. **Kernvergleich** mit Ansparverlauf-Chart
2. **Start-Szenarien** (Verzögerung 0/2/5/10 Jahre)
3. **Cashflow-Ansicht** (Sparphase + Finanzierungsphase als Timeline)
4. **Zinsrisiko-Stresstest** (Marktzins 3/5/7/9 %)
5. **Zinshistorie** 2000-2025 (Bundesbank + EZB)
6. **Staatliche Förderung** (Wohnungsbauprämie + Arbeitnehmer-Sparzulage)
7. **PDF-Export** für Kundenberatungen

## Designsystem (wie beamtenrechner)
- Primärfarbe: `#2e7d32` (Grün)
- Akzentfarbe: `#c62828` (Rot, "Ohne Bausparen")
- Neutrale: `#66bb6a`, `#f57c00`, `#90a4ae`
- Layout wide, minimales CSS, Tabs-Navigation, Plotly mit transparentem Hintergrund

## Datenquellen
- Bundesbank MFI-Zinsstatistik (SUD118) — Baufinanzierung 5-10 J.
- EZB Key Interest Rates History — Leitzinsen
- Branchendurchschnitte Schwäbisch Hall / Wüstenrot / LBS — Bausparzinsen

## Förderungs-Rahmendaten (2026)
- **WoP**: 10 % auf bis zu 700 € (Single) / 1400 € (Paar), zvE-Grenze 35 T€ / 70 T€
- **AN-Sparzulage**: 9 % auf bis zu 470 €/Jahr VL, zvE-Grenze 40 T€ / 80 T€
