"""
Historische Zinssätze Deutschland 2000-2025
- baufinanzierung: Effektivzins Wohnungsbaukredite 5-10 J. Zinsbindung (Bundesbank SUD118)
- bauspar_guthaben: Branchendurchschnitt Bausparvertrag-Guthabenzins
- bauspar_darlehen: Branchendurchschnitt Bauspardarlehenszins
- leitzins: EZB-Hauptrefinanzierungssatz zum Jahresende
"""

ZINSEN_HISTORISCH = {
    2000: {"baufinanzierung": 6.21, "bauspar_guthaben": 3.00, "bauspar_darlehen": 4.75, "leitzins": 4.75},
    2001: {"baufinanzierung": 5.73, "bauspar_guthaben": 3.00, "bauspar_darlehen": 4.75, "leitzins": 3.25},
    2002: {"baufinanzierung": 5.65, "bauspar_guthaben": 3.00, "bauspar_darlehen": 4.75, "leitzins": 2.75},
    2003: {"baufinanzierung": 5.07, "bauspar_guthaben": 2.75, "bauspar_darlehen": 4.50, "leitzins": 2.00},
    2004: {"baufinanzierung": 4.79, "bauspar_guthaben": 2.50, "bauspar_darlehen": 4.25, "leitzins": 2.00},
    2005: {"baufinanzierung": 4.31, "bauspar_guthaben": 2.25, "bauspar_darlehen": 4.00, "leitzins": 2.25},
    2006: {"baufinanzierung": 4.56, "bauspar_guthaben": 2.25, "bauspar_darlehen": 4.00, "leitzins": 3.50},
    2007: {"baufinanzierung": 4.95, "bauspar_guthaben": 2.50, "bauspar_darlehen": 4.25, "leitzins": 4.00},
    2008: {"baufinanzierung": 5.08, "bauspar_guthaben": 2.50, "bauspar_darlehen": 4.25, "leitzins": 2.50},
    2009: {"baufinanzierung": 4.40, "bauspar_guthaben": 2.00, "bauspar_darlehen": 4.00, "leitzins": 1.00},
    2010: {"baufinanzierung": 3.88, "bauspar_guthaben": 1.75, "bauspar_darlehen": 3.75, "leitzins": 1.00},
    2011: {"baufinanzierung": 4.04, "bauspar_guthaben": 1.75, "bauspar_darlehen": 3.75, "leitzins": 1.00},
    2012: {"baufinanzierung": 3.30, "bauspar_guthaben": 1.50, "bauspar_darlehen": 3.50, "leitzins": 0.75},
    2013: {"baufinanzierung": 2.90, "bauspar_guthaben": 1.25, "bauspar_darlehen": 3.25, "leitzins": 0.25},
    2014: {"baufinanzierung": 2.60, "bauspar_guthaben": 1.00, "bauspar_darlehen": 3.00, "leitzins": 0.05},
    2015: {"baufinanzierung": 2.00, "bauspar_guthaben": 0.75, "bauspar_darlehen": 2.75, "leitzins": 0.05},
    2016: {"baufinanzierung": 1.80, "bauspar_guthaben": 0.50, "bauspar_darlehen": 2.50, "leitzins": 0.00},
    2017: {"baufinanzierung": 1.84, "bauspar_guthaben": 0.25, "bauspar_darlehen": 2.35, "leitzins": 0.00},
    2018: {"baufinanzierung": 1.88, "bauspar_guthaben": 0.25, "bauspar_darlehen": 2.25, "leitzins": 0.00},
    2019: {"baufinanzierung": 1.50, "bauspar_guthaben": 0.10, "bauspar_darlehen": 2.10, "leitzins": 0.00},
    2020: {"baufinanzierung": 1.29, "bauspar_guthaben": 0.10, "bauspar_darlehen": 2.00, "leitzins": 0.00},
    2021: {"baufinanzierung": 1.31, "bauspar_guthaben": 0.10, "bauspar_darlehen": 1.95, "leitzins": 0.00},
    2022: {"baufinanzierung": 2.85, "bauspar_guthaben": 0.25, "bauspar_darlehen": 2.10, "leitzins": 2.50},
    2023: {"baufinanzierung": 3.95, "bauspar_guthaben": 0.50, "bauspar_darlehen": 2.25, "leitzins": 4.50},
    2024: {"baufinanzierung": 3.60, "bauspar_guthaben": 0.75, "bauspar_darlehen": 2.35, "leitzins": 3.15},
    2025: {"baufinanzierung": 3.45, "bauspar_guthaben": 0.75, "bauspar_darlehen": 2.40, "leitzins": 2.40},
}

STAND_ZINSEN = "April 2026"
QUELLEN = (
    "Bundesbank MFI-Zinsstatistik (SUD118), EZB-Leitzinsarchiv, "
    "Geschäftsberichte Schwäbisch Hall/Wüstenrot/LBS, Interhyp-Zinsbarometer"
)


def get_jahr_range():
    return sorted(ZINSEN_HISTORISCH.keys())


def get_baufi_zinsen():
    return [(jahr, daten["baufinanzierung"]) for jahr, daten in sorted(ZINSEN_HISTORISCH.items())]


def get_zins_statistik():
    werte = [d["baufinanzierung"] for d in ZINSEN_HISTORISCH.values()]
    return {
        "min": min(werte),
        "max": max(werte),
        "durchschnitt": sum(werte) / len(werte),
    }
