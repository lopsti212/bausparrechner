"""
Staatliche Förderungen für Bausparverträge:
- Wohnungsbauprämie (WoP) nach §2 WoPG
- Arbeitnehmer-Sparzulage nach §13 VermBG (VL)
"""

# Wohnungsbauprämie (Stand 2026)
WOP_SATZ = 0.10          # 10% auf eingezahlte Sparleistung
WOP_MAX_EINZAHLUNG_SINGLE = 700.0
WOP_MAX_EINZAHLUNG_PAAR = 1400.0
WOP_MAX_EINKOMMEN_SINGLE = 35000.0   # zvE
WOP_MAX_EINKOMMEN_PAAR = 70000.0

# Arbeitnehmer-Sparzulage (VL-Bausparen)
AN_ZULAGE_SATZ = 0.09    # 9% auf vermögenswirksame Leistungen
AN_ZULAGE_MAX_EINZAHLUNG = 470.0     # max. 470€/Jahr VL bausparbegünstigt
AN_ZULAGE_MAX_EINKOMMEN_SINGLE = 40000.0
AN_ZULAGE_MAX_EINKOMMEN_PAAR = 80000.0


def berechne_wop(
    jahres_einzahlung: float,
    zve: float,
    verheiratet: bool,
) -> dict:
    """
    Wohnungsbauprämie pro Jahr.
    """
    max_einz = WOP_MAX_EINZAHLUNG_PAAR if verheiratet else WOP_MAX_EINZAHLUNG_SINGLE
    max_eink = WOP_MAX_EINKOMMEN_PAAR if verheiratet else WOP_MAX_EINKOMMEN_SINGLE

    foerderfaehig = min(jahres_einzahlung, max_einz)
    anspruch = zve <= max_eink
    wop = foerderfaehig * WOP_SATZ if anspruch else 0.0

    return {
        "prämie_pro_jahr": wop,
        "foerderfaehig": foerderfaehig,
        "anspruch": anspruch,
        "einkommensgrenze": max_eink,
    }


def berechne_an_sparzulage(
    jahres_vl: float,
    zve: float,
    verheiratet: bool,
) -> dict:
    """
    Arbeitnehmer-Sparzulage pro Jahr (nur für VL-geförderte Beträge).
    """
    max_eink = AN_ZULAGE_MAX_EINKOMMEN_PAAR if verheiratet else AN_ZULAGE_MAX_EINKOMMEN_SINGLE
    foerderfaehig = min(jahres_vl, AN_ZULAGE_MAX_EINZAHLUNG)
    anspruch = zve <= max_eink
    zulage = foerderfaehig * AN_ZULAGE_SATZ if anspruch else 0.0

    return {
        "zulage_pro_jahr": zulage,
        "foerderfaehig": foerderfaehig,
        "anspruch": anspruch,
        "einkommensgrenze": max_eink,
    }


def berechne_gesamt_foerderung(
    monatliche_sparrate: float,
    vl_anteil_monatlich: float,
    sparjahre: float,
    zve: float,
    verheiratet: bool,
) -> dict:
    """
    Summiert WoP + AN-Sparzulage über den gesamten Ansparzeitraum.
    """
    jahres_einzahlung = monatliche_sparrate * 12
    jahres_vl = vl_anteil_monatlich * 12

    wop = berechne_wop(jahres_einzahlung, zve, verheiratet)
    an_zul = berechne_an_sparzulage(jahres_vl, zve, verheiratet)

    wop_gesamt = wop["prämie_pro_jahr"] * sparjahre
    an_gesamt = an_zul["zulage_pro_jahr"] * sparjahre

    return {
        "wop_pro_jahr": wop["prämie_pro_jahr"],
        "wop_gesamt": wop_gesamt,
        "wop_anspruch": wop["anspruch"],
        "an_zulage_pro_jahr": an_zul["zulage_pro_jahr"],
        "an_zulage_gesamt": an_gesamt,
        "an_zulage_anspruch": an_zul["anspruch"],
        "foerderung_gesamt": wop_gesamt + an_gesamt,
        "foerderung_pro_jahr": wop["prämie_pro_jahr"] + an_zul["zulage_pro_jahr"],
    }
