"""
Ansparphase des Bausparvertrages.
Berechnet das angesparte Guthaben inkl. Zinsen über eine definierte Laufzeit.
"""


def berechne_ansparung(
    monatliche_sparrate: float,
    zinssatz_guthaben_prozent: float,
    sparjahre: float,
    einmalzahlung: float = 0.0,
) -> dict:
    """
    Berechnet das Bauspar-Guthaben am Ende der Ansparphase.

    Verwendet eine Monats-Verzinsung (etwas genauer als jährliche Summe).

    Args:
        monatliche_sparrate: Monatliche Sparrate in €
        zinssatz_guthaben_prozent: Jährlicher Guthabenzins in %
        sparjahre: Ansparzeitraum in Jahren (kann dezimal sein)
        einmalzahlung: Optionaler Einmalbetrag zu Beginn

    Returns:
        dict mit eingezahlt, zinsertrag, guthaben_gesamt, verlauf (Liste je Jahr)
    """
    monatszins = zinssatz_guthaben_prozent / 100 / 12
    anzahl_monate = int(round(sparjahre * 12))

    guthaben = float(einmalzahlung)
    eingezahlt = float(einmalzahlung)
    verlauf = []

    for monat in range(1, anzahl_monate + 1):
        guthaben = guthaben * (1 + monatszins) + monatliche_sparrate
        eingezahlt += monatliche_sparrate
        if monat % 12 == 0:
            verlauf.append({
                "jahr": monat // 12,
                "eingezahlt": eingezahlt,
                "guthaben": guthaben,
                "zinsertrag": guthaben - eingezahlt,
            })

    return {
        "eingezahlt": eingezahlt,
        "zinsertrag": guthaben - eingezahlt,
        "guthaben_gesamt": guthaben,
        "verlauf": verlauf,
        "anzahl_monate": anzahl_monate,
    }
