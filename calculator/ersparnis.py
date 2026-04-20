"""
Kernberechnung: Bauansparprogramm-Vergleich.
Vergleicht zwei Szenarien:
  A) Direktfinanzierung zum Marktzins (ohne Vorsparen)
  B) Bausparen + Finanzierung mit Bauspar-Restsumme zu einem niedrigeren Zins

Ergebnis: konkrete Ersparnis in € über die Finanzierungslaufzeit.
"""

from calculator.sparphase import berechne_ansparung
from calculator.finanzierung import berechne_annuitaet


def berechne_bauansparprogramm(
    finanzierungssumme: float,
    monatliche_sparrate: float,
    sparjahre: float,
    zins_bauspar_guthaben: float,
    zins_bauspar_darlehen: float,
    zins_markt_heute: float,
    zins_markt_zukunft: float,
    finanzierungslaufzeit: int,
    einmalzahlung: float = 0.0,
    foerderung_gesamt: float = 0.0,
) -> dict:
    """
    Vergleicht Szenario A (Direktfinanzierung, ohne Vorsparen) mit
    Szenario B (Bauspar-Ansparung + anschließende Finanzierung der Restsumme).

    Szenario A:
        Volle Finanzierungssumme zum zukünftigen Marktzins über die Laufzeit.

    Szenario B:
        - Kunde spart in Ansparphase ein Guthaben auf (inkl. Förderung).
        - Guthaben wird als Eigenkapital eingesetzt.
        - Restsumme wird zum garantierten Bauspar-Darlehenszins finanziert.
        - Falls Guthaben die Finanzierungssumme übersteigt, entfällt Finanzierung.

    Returns dict mit beiden Szenarien, Ersparnis, angespartem Guthaben etc.
    """
    ansparung = berechne_ansparung(
        monatliche_sparrate=monatliche_sparrate,
        zinssatz_guthaben_prozent=zins_bauspar_guthaben,
        sparjahre=sparjahre,
        einmalzahlung=einmalzahlung,
    )

    guthaben_gesamt = ansparung["guthaben_gesamt"] + foerderung_gesamt
    restsumme = max(0.0, finanzierungssumme - guthaben_gesamt)

    # Szenario A: ohne Bausparen — volle Summe zum Zukunftszins
    szenario_a = berechne_annuitaet(
        darlehenssumme=finanzierungssumme,
        zinssatz_prozent=zins_markt_zukunft,
        laufzeit_jahre=finanzierungslaufzeit,
    )

    # Szenario B: mit Bausparen — Restsumme zum Bauspar-Darlehenszins
    szenario_b = berechne_annuitaet(
        darlehenssumme=restsumme,
        zinssatz_prozent=zins_bauspar_darlehen,
        laufzeit_jahre=finanzierungslaufzeit,
    )

    ersparnis_zinsen = szenario_a["gesamt_zinsen"] - szenario_b["gesamt_zinsen"]
    ersparnis_monatsrate = szenario_a["monatsrate"] - szenario_b["monatsrate"]

    return {
        "ansparung": ansparung,
        "guthaben_gesamt": guthaben_gesamt,
        "eigene_einzahlung": ansparung["eingezahlt"],
        "zinsertrag_ansparung": ansparung["zinsertrag"],
        "foerderung_gesamt": foerderung_gesamt,
        "finanzierungssumme": finanzierungssumme,
        "restsumme_darlehen": restsumme,
        "szenario_a": szenario_a,
        "szenario_b": szenario_b,
        "ersparnis_zinsen": ersparnis_zinsen,
        "ersparnis_monatsrate": ersparnis_monatsrate,
        "vollstaendig_gedeckt": restsumme == 0.0,
    }


def berechne_startzeitpunkt_szenarien(
    finanzierungssumme: float,
    monatliche_sparrate: float,
    max_sparjahre: float,
    zins_bauspar_guthaben: float,
    zins_bauspar_darlehen: float,
    zins_markt_zukunft: float,
    finanzierungslaufzeit: int,
    foerderung_pro_jahr: float,
    start_offsets: list,
) -> list:
    """
    Berechnet die Ersparnis in Abhängigkeit vom Startzeitpunkt.
    start_offsets = [0, 2, 5, 10] Jahre Verzögerung.
    Bei Verzögerung um X Jahre bleiben (max_sparjahre - X) Jahre zum Sparen.
    """
    szenarien = []
    for offset in start_offsets:
        verbleibende_sparjahre = max(0.0, max_sparjahre - offset)
        foerderung_gesamt = foerderung_pro_jahr * verbleibende_sparjahre

        if verbleibende_sparjahre <= 0:
            # Kein Sparen möglich → volle Direktfinanzierung
            szenarien.append({
                "start_in_jahren": offset,
                "sparjahre": 0.0,
                "guthaben": 0.0,
                "restsumme": finanzierungssumme,
                "monatsrate": berechne_annuitaet(
                    finanzierungssumme, zins_markt_zukunft, finanzierungslaufzeit
                )["monatsrate"],
                "gesamt_zinsen": berechne_annuitaet(
                    finanzierungssumme, zins_markt_zukunft, finanzierungslaufzeit
                )["gesamt_zinsen"],
                "ersparnis_vs_sofort": None,
            })
            continue

        ergebnis = berechne_bauansparprogramm(
            finanzierungssumme=finanzierungssumme,
            monatliche_sparrate=monatliche_sparrate,
            sparjahre=verbleibende_sparjahre,
            zins_bauspar_guthaben=zins_bauspar_guthaben,
            zins_bauspar_darlehen=zins_bauspar_darlehen,
            zins_markt_heute=zins_markt_zukunft,
            zins_markt_zukunft=zins_markt_zukunft,
            finanzierungslaufzeit=finanzierungslaufzeit,
            foerderung_gesamt=foerderung_gesamt,
        )
        szenarien.append({
            "start_in_jahren": offset,
            "sparjahre": verbleibende_sparjahre,
            "guthaben": ergebnis["guthaben_gesamt"],
            "restsumme": ergebnis["restsumme_darlehen"],
            "monatsrate": ergebnis["szenario_b"]["monatsrate"],
            "gesamt_zinsen": ergebnis["szenario_b"]["gesamt_zinsen"],
            "ersparnis_vs_sofort": ergebnis["ersparnis_zinsen"],
        })

    # Relative Ersparnis gegenüber sofortigem Start berechnen
    if szenarien and szenarien[0]["ersparnis_vs_sofort"] is not None:
        basis_ersparnis = szenarien[0]["ersparnis_vs_sofort"]
        for s in szenarien:
            if s["ersparnis_vs_sofort"] is not None:
                s["verlust_vs_sofort"] = basis_ersparnis - s["ersparnis_vs_sofort"]
            else:
                s["verlust_vs_sofort"] = basis_ersparnis

    return szenarien


def berechne_stresstest(
    finanzierungssumme: float,
    monatliche_sparrate: float,
    sparjahre: float,
    zins_bauspar_guthaben: float,
    zins_bauspar_darlehen: float,
    finanzierungslaufzeit: int,
    foerderung_gesamt: float,
    stress_zinsen: list,
) -> list:
    """
    Zinsrisiko-Stresstest: was wäre wenn der Marktzins zur Finanzierung
    auf 4%, 6%, 8%, 10% steigt?
    Vergleicht jeweils Direktfinanzierung vs. Bauspar-Variante.
    """
    ergebnisse = []
    for markt_zins in stress_zinsen:
        ergebnis = berechne_bauansparprogramm(
            finanzierungssumme=finanzierungssumme,
            monatliche_sparrate=monatliche_sparrate,
            sparjahre=sparjahre,
            zins_bauspar_guthaben=zins_bauspar_guthaben,
            zins_bauspar_darlehen=zins_bauspar_darlehen,
            zins_markt_heute=markt_zins,
            zins_markt_zukunft=markt_zins,
            finanzierungslaufzeit=finanzierungslaufzeit,
            foerderung_gesamt=foerderung_gesamt,
        )
        ergebnisse.append({
            "markt_zins": markt_zins,
            "rate_ohne_bausparen": ergebnis["szenario_a"]["monatsrate"],
            "rate_mit_bausparen": ergebnis["szenario_b"]["monatsrate"],
            "zinsen_ohne": ergebnis["szenario_a"]["gesamt_zinsen"],
            "zinsen_mit": ergebnis["szenario_b"]["gesamt_zinsen"],
            "ersparnis": ergebnis["ersparnis_zinsen"],
        })
    return ergebnisse
