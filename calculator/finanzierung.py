"""
Finanzierungs-Berechnung (Annuitätendarlehen).
"""


def berechne_annuitaet(
    darlehenssumme: float,
    zinssatz_prozent: float,
    laufzeit_jahre: int,
) -> dict:
    """
    Klassisches Annuitätendarlehen: gleichbleibende Monatsrate über die Laufzeit,
    volle Tilgung am Laufzeitende.

    Args:
        darlehenssumme: Darlehenshöhe in €
        zinssatz_prozent: Nomineller Jahreszins in %
        laufzeit_jahre: Gesamtlaufzeit in Jahren

    Returns:
        dict mit monatsrate, gesamt_zinsen, gesamt_zahlung, verlauf (je Jahr)
    """
    if darlehenssumme <= 0:
        return {
            "monatsrate": 0.0,
            "gesamt_zinsen": 0.0,
            "gesamt_zahlung": 0.0,
            "verlauf": [],
            "darlehenssumme": 0.0,
        }

    monatszins = zinssatz_prozent / 100 / 12
    anzahl_monate = laufzeit_jahre * 12

    if monatszins == 0:
        monatsrate = darlehenssumme / anzahl_monate
    else:
        q = 1 + monatszins
        monatsrate = darlehenssumme * (monatszins * q**anzahl_monate) / (q**anzahl_monate - 1)

    restschuld = darlehenssumme
    gesamt_zinsen = 0.0
    verlauf = []
    jahr_zinsen = 0.0
    jahr_tilgung = 0.0

    for monat in range(1, anzahl_monate + 1):
        zins_anteil = restschuld * monatszins
        tilg_anteil = monatsrate - zins_anteil
        restschuld -= tilg_anteil
        gesamt_zinsen += zins_anteil
        jahr_zinsen += zins_anteil
        jahr_tilgung += tilg_anteil

        if monat % 12 == 0:
            verlauf.append({
                "jahr": monat // 12,
                "restschuld": max(0.0, restschuld),
                "zinsen_jahr": jahr_zinsen,
                "tilgung_jahr": jahr_tilgung,
            })
            jahr_zinsen = 0.0
            jahr_tilgung = 0.0

    return {
        "monatsrate": monatsrate,
        "gesamt_zinsen": gesamt_zinsen,
        "gesamt_zahlung": monatsrate * anzahl_monate,
        "verlauf": verlauf,
        "darlehenssumme": darlehenssumme,
    }
