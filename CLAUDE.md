# Bausparrechner

## Zusammenfassung der Entstehung

Die App wurde als neutraler Bausparrechner von Grund auf neu entwickelt. Design und Struktur orientieren sich am Schwesterprojekt `beamtenrechner` (gleiches Farbschema, gleicher Seitenaufbau, gleicher Tech-Stack). Die Berechnungsmodule, Daten und UI-Logik wurden spezifisch für das Thema Bausparen/Finanzierung geschrieben.

### Was wurde gemacht

1. **Projektgerüst angelegt** — Verzeichnisstruktur, Streamlit-Config, requirements, Favicon (aus beamtenrechner übernommen), .gitignore.
2. **Zinsdaten recherchiert** — Jahresdurchschnitte 2000–2025 für Baufinanzierungszinsen (5–10 J. Zinsbindung), Bauspar-Guthabenzinsen, Bauspar-Darlehenszinsen und EZB-Leitzinsen, fest im Modul `data/zinsen_historisch.py` hinterlegt.
3. **Berechnungs-Module geschrieben** — vier getrennte Module für Ansparphase, Annuitätendarlehen, staatliche Förderung und den Szenarien-Vergleich.
4. **Streamlit-App gebaut** — Sidebar-Eingaben, vier Key-Metriken und sechs Tabs (Ersparnis, Start-Szenarien, Cashflow, Zins-Stresstest, Zinshistorie, PDF-Export).
5. **PDF-Export implementiert** — ReportLab-basiert, mit Deckblatt, Eingaben- und Ergebnis-Tabellen, Förderungs-Informationen.
6. **Sicherheits-Hardening** — Streamlit bindet ausschließlich auf `127.0.0.1:8501`, Telemetrie (`gatherUsageStats`) deaktiviert, Error-Details auf Stacktrace beschränkt, Toolbar minimal.
7. **GitHub-Repository** — `lopsti212/bausparrechner` mit initialer Codebasis und Hardening-Commit.
8. **Cloudflare-Tunnel** — `cloudflared` installiert, Tunnel `bausparrechner` angelegt, DNS-Route für `bausparrechner.lopsticles.com` gesetzt, TLS endet an der Cloudflare-Edge.
9. **Systemd-Services** — `bausparrechner.service` (Streamlit) und `cloudflared.service` (Tunnel) laufen reboot-fest.

## Features

### Eingaben (Sidebar)
- **Finanzierungsvorhaben** — geplante Finanzierungssumme, Jahr des Finanzierungsstarts, Laufzeit
- **Sparphase (Bausparvertrag)** — monatliche Sparrate, Einmalzahlung, Guthabenzins (Default 0,10 %), Darlehenszins (Default 1,40 %)
- **Marktzins-Annahmen** — aktueller und erwarteter zukünftiger Baufinanzierungszins
- **Staatliche Förderung** — Familienstand, zu versteuerndes Einkommen, VL-Anteil des Arbeitgebers

### Key-Metriken (direkt unter dem Titel)
- Sparzeitraum
- Angespartes Guthaben (inkl. staatlicher Förderung)
- Monatsrate mit Bausparen (mit Delta zur Direktfinanzierung)
- Zinsersparnis gesamt über die Finanzierungslaufzeit

### Tabs
1. **Ersparnis** — Tabelle und Balkendiagramm (Direktfinanzierung vs. Bausparen), Ansparverlauf, Förderungs-Kacheln
2. **Start-Szenarien** — Auswirkung eines späteren Sparbeginns (heute vs. +2/+5/+10 Jahre)
3. **Cashflow** — monatliche Belastung über Spar- und Finanzierungsphase als Timeline
4. **Zins-Stresstest** — Marktzins 3/5/7/9 %, Vergleich der Monatsrate mit/ohne Bausparvertrag
5. **Zinshistorie** — Liniendiagramm 2000–2025 mit Baufinanzierung, Bauspar-Darlehen, Bauspar-Guthaben, EZB-Leitzins + Min/Max/Durchschnitt
6. **PDF-Report** — Download eines PDFs mit allen Eingaben, Ergebnissen, Szenarien und Stresstest-Tabelle

### Berechnungslogik
- **Szenario A** (ohne Bausparen): volle Finanzierungssumme zum zukünftigen Marktzins über die Laufzeit (Annuitätendarlehen).
- **Szenario B** (mit Bausparen): Guthaben aus Ansparphase + staatliche Förderung → Restsumme zum Bauspar-Darlehenszins über die Laufzeit.
- **Ersparnis** = Zinskosten(A) − Zinskosten(B).
- **Förderung** = Wohnungsbauprämie (10 % auf bis zu 700 €/Jahr Single, 1.400 €/Jahr Paar, zvE-Grenze 35.000/70.000 €) + Arbeitnehmer-Sparzulage (9 % auf bis zu 470 €/Jahr VL, zvE-Grenze 40.000/80.000 €).

## Tech-Stack
- **Framework**: Streamlit
- **Grafiken**: Plotly (transparente Hintergründe, Streamlit-Theme)
- **PDF**: ReportLab
- **Daten**: fest hinterlegt in Python-Modul (offlinefähig)

## Design
- Primärfarbe Grün `#2e7d32`, Akzentfarbe Rot `#c62828`, Sekundärfarben `#66bb6a`, `#f57c00`, `#90a4ae`
- Basis-Schriftgröße 13 px, minimales CSS, Tabs-Navigation mit grünem Underline
- Layout wide, Sidebar expanded

## Deployment
- **Repository**: https://github.com/lopsti212/bausparrechner
- **Öffentliche URL**: https://bausparrechner.lopsticles.com
- **Server-Binding**: `127.0.0.1:8501` (nur über Cloudflare-Tunnel erreichbar)
- **Systemd-Services**:
  - `bausparrechner.service` — Streamlit-App
  - `cloudflared.service` — Cloudflare-Tunnel

### Verwaltungs-Befehle
```bash
# App-Status
systemctl status bausparrechner
systemctl status cloudflared

# Nach Code-Änderung (git pull) App neu starten
systemctl restart bausparrechner

# Live-Logs
journalctl -u bausparrechner -f
journalctl -u cloudflared -f

# Lokale Entwicklung
cd /root/bausparrechner && streamlit run app.py
```

### Updates aus GitHub
```bash
cd /root/bausparrechner
git pull
systemctl restart bausparrechner
```

## Datenquellen
- Bundesbank MFI-Zinsstatistik (Baufinanzierungszinsen 5–10 J. Zinsbindung)
- EZB-Leitzinsarchiv (Hauptrefinanzierungssatz)
- Branchendurchschnitte der Bausparkassen (Guthaben- und Darlehenszinsen)

Die App ist vollständig unternehmens­neutral gehalten — es werden keine Anbieter, Tarife oder Marken genannt.
