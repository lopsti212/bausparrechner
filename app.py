"""
Bausparrechner — Bauansparprogramm
"""

import datetime
import os
import sys

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from calculator.ersparnis import (
    berechne_bauansparprogramm,
    berechne_startzeitpunkt_szenarien,
    berechne_stresstest,
)
from calculator.finanzierung import berechne_annuitaet
from calculator.foerderung import berechne_gesamt_foerderung
from data.zinsen_historisch import (
    QUELLEN,
    STAND_ZINSEN,
    ZINSEN_HISTORISCH,
    get_zins_statistik,
)
from export.pdf_export import erstelle_pdf

FAVICON_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "favicon.png")
COPYRIGHT = "Jan Glänzer"

st.set_page_config(
    page_title="Bausparrechner",
    page_icon=FAVICON_PATH if os.path.exists(FAVICON_PATH) else "💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
    html, body, [class*="css"] { font-size: 13px; }
    h1 { font-size: 1.8rem !important; font-weight: 600 !important; padding-bottom: 10px; margin-bottom: 20px !important; }
    h2 { font-size: 1.2rem !important; font-weight: 500 !important; margin-top: 15px !important; margin-bottom: 10px !important; }
    h3 { font-size: 1rem !important; font-weight: 500 !important; }
    [data-testid="stMetricValue"] { font-size: 1.4rem !important; }
    [data-testid="stMetricLabel"] { font-size: 0.8rem !important; }
    .stTable { font-size: 0.85rem !important; }
    table { font-size: 0.85rem !important; }
    .stTabs [data-baseweb="tab"] { font-size: 1.1rem !important; font-weight: 500 !important; padding: 10px 20px !important; }
    .stTabs [data-baseweb="tab"][aria-selected="true"] { font-weight: 600 !important; border-bottom: 3px solid #2e7d32 !important; }
    input, select { font-size: 0.85rem !important; }
    [data-testid="stSidebar"] h2 { font-size: 0.9rem !important; padding-bottom: 5px; margin-top: 20px !important; }
    .stCaption { font-size: 0.75rem !important; }
</style>
""",
    unsafe_allow_html=True,
)


def fmt_euro(betrag: float) -> str:
    return f"{betrag:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")


st.title("Bausparrechner — Bauansparprogramm")
st.caption("Zinsersparnis durch frühzeitiges Bausparen vor der Finanzierung")

# =========================================================================
# SIDEBAR — EINGABEN
# =========================================================================
st.sidebar.markdown("### Eingabedaten")

st.sidebar.markdown("## Finanzierungsvorhaben")
heute_jahr = datetime.datetime.now().year

finanzierungssumme = st.sidebar.number_input(
    "Geplante Finanzierungssumme (€)",
    min_value=10000.0,
    max_value=2_000_000.0,
    value=300_000.0,
    step=10_000.0,
    help="Der Betrag, der voraussichtlich zur Immobilienfinanzierung benötigt wird.",
)

jahr_finanzierung = st.sidebar.number_input(
    "Geplanter Beginn der Finanzierung (Jahr)",
    min_value=heute_jahr,
    max_value=heute_jahr + 30,
    value=heute_jahr + 7,
    step=1,
)

finanzierungslaufzeit = st.sidebar.number_input(
    "Finanzierungslaufzeit (Jahre)",
    min_value=5,
    max_value=40,
    value=25,
    step=1,
    help="Gesamtlaufzeit bis zur vollständigen Tilgung.",
)

st.sidebar.markdown("## Sparphase (Bausparvertrag)")

monatliche_sparrate = st.sidebar.number_input(
    "Monatliche Sparrate (€)",
    min_value=0.0,
    max_value=2000.0,
    value=200.0,
    step=10.0,
)

einmalzahlung = st.sidebar.number_input(
    "Einmalzahlung zu Beginn (€)",
    min_value=0.0,
    max_value=200_000.0,
    value=0.0,
    step=500.0,
    help="Z. B. vorhandenes Eigenkapital, das direkt eingebracht wird.",
)

zins_bauspar_guthaben = st.sidebar.number_input(
    "Guthabenzins Bausparvertrag (% p. a.)",
    min_value=0.0,
    max_value=5.0,
    value=0.10,
    step=0.05,
    format="%.2f",
)

zins_bauspar_darlehen = st.sidebar.number_input(
    "Darlehenszins Bausparvertrag (% p. a.)",
    min_value=1.0,
    max_value=6.0,
    value=1.40,
    step=0.05,
    format="%.2f",
    help="Vertraglich festgelegter Zins des Bauspardarlehens.",
)

st.sidebar.markdown("## Marktzins-Annahmen")

zins_markt_heute = st.sidebar.number_input(
    "Aktueller Marktzins Baufi (% p. a.)",
    min_value=0.5,
    max_value=10.0,
    value=3.50,
    step=0.05,
    format="%.2f",
)

zins_markt_zukunft = st.sidebar.number_input(
    "Erwarteter Marktzins bei Finanzierung (% p. a.)",
    min_value=0.5,
    max_value=12.0,
    value=4.50,
    step=0.05,
    format="%.2f",
    help="Annahme zum Zinsniveau zum Zeitpunkt der Finanzierung.",
)

st.sidebar.markdown("## Staatliche Förderung")

verheiratet = st.sidebar.checkbox("Verheiratet", value=False)

zve = st.sidebar.number_input(
    "Zu versteuerndes Einkommen (€/Jahr)",
    min_value=0.0,
    max_value=200_000.0,
    value=35_000.0,
    step=1000.0,
    help="Relevant für WoP (max. 35.000 € Single / 70.000 € Paar) und AN-Sparzulage (40.000 / 80.000).",
)

vl_monatlich = st.sidebar.number_input(
    "Davon VL-Leistung des Arbeitgebers (€/Monat)",
    min_value=0.0,
    max_value=40.0,
    value=0.0,
    step=5.0,
    help="Vermögenswirksame Leistungen (max. 40 €/Monat bausparbegünstigt).",
)

# Abgeleitete Werte
sparjahre = max(0.0, jahr_finanzierung - heute_jahr)

# =========================================================================
# BERECHNUNGEN
# =========================================================================
foerderung = berechne_gesamt_foerderung(
    monatliche_sparrate=monatliche_sparrate,
    vl_anteil_monatlich=vl_monatlich,
    sparjahre=sparjahre,
    zve=zve,
    verheiratet=verheiratet,
)

ergebnis = berechne_bauansparprogramm(
    finanzierungssumme=finanzierungssumme,
    monatliche_sparrate=monatliche_sparrate,
    sparjahre=sparjahre,
    zins_bauspar_guthaben=zins_bauspar_guthaben,
    zins_bauspar_darlehen=zins_bauspar_darlehen,
    zins_markt_heute=zins_markt_heute,
    zins_markt_zukunft=zins_markt_zukunft,
    finanzierungslaufzeit=finanzierungslaufzeit,
    einmalzahlung=einmalzahlung,
    foerderung_gesamt=foerderung["foerderung_gesamt"],
)

# =========================================================================
# KEY METRICS
# =========================================================================
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Sparzeitraum",
        value=f"{sparjahre:.0f} Jahre",
    )
    st.caption(f"Bis {jahr_finanzierung} ({monatliche_sparrate:.0f} €/Mon.)")

with col2:
    st.metric(
        label="Angespartes Guthaben",
        value=fmt_euro(ergebnis["guthaben_gesamt"]),
    )
    st.caption(
        f"davon Förderung: {fmt_euro(foerderung['foerderung_gesamt'])}"
    )

with col3:
    st.metric(
        label="Monatsrate (mit Bausparen)",
        value=fmt_euro(ergebnis["szenario_b"]["monatsrate"]),
        delta=fmt_euro(-ergebnis["ersparnis_monatsrate"]) if ergebnis["ersparnis_monatsrate"] > 0 else None,
        delta_color="inverse",
    )
    st.caption(f"statt {fmt_euro(ergebnis['szenario_a']['monatsrate'])} ohne")

with col4:
    st.metric(
        label="Zinsersparnis gesamt",
        value=fmt_euro(ergebnis["ersparnis_zinsen"]),
    )
    st.caption(f"über {finanzierungslaufzeit} Jahre Finanzierung")

# style metric cards (inline, ohne streamlit_extras Abhängigkeit zur Laufzeit)
st.markdown(
    """
<style>
div[data-testid="stMetric"] {
    border-left: 4px solid #2e7d32;
    padding: 8px 12px;
    background: rgba(46, 125, 50, 0.03);
    border-radius: 4px;
}
</style>
""",
    unsafe_allow_html=True,
)

# =========================================================================
# NAVIGATION — TABS
# =========================================================================
tab_ersp, tab_szen, tab_cash, tab_stress, tab_hist, tab_export = st.tabs(
    ["Ersparnis", "Start-Szenarien", "Cashflow", "Zins-Stresstest", "Zinshistorie", "PDF-Export"]
)

# ---------- TAB: ERSPARNIS ----------
with tab_ersp:
    col_l, col_r = st.columns([3, 2])

    with col_l:
        st.markdown("### Vergleich Ihrer Szenarien")
        df_vergleich = pd.DataFrame({
            "": ["Darlehenshöhe", "Monatsrate", "Zinskosten gesamt", "Gesamtzahlung"],
            "Ohne Bausparen": [
                fmt_euro(ergebnis["finanzierungssumme"]),
                fmt_euro(ergebnis["szenario_a"]["monatsrate"]),
                fmt_euro(ergebnis["szenario_a"]["gesamt_zinsen"]),
                fmt_euro(ergebnis["szenario_a"]["gesamt_zahlung"]),
            ],
            "Mit Bauansparprogramm": [
                fmt_euro(ergebnis["restsumme_darlehen"]),
                fmt_euro(ergebnis["szenario_b"]["monatsrate"]),
                fmt_euro(ergebnis["szenario_b"]["gesamt_zinsen"]),
                fmt_euro(ergebnis["szenario_b"]["gesamt_zahlung"]),
            ],
        })
        st.dataframe(df_vergleich, use_container_width=True, hide_index=True)

        if ergebnis["vollstaendig_gedeckt"]:
            st.success(
                "Das angesparte Guthaben deckt die Finanzierungssumme komplett ab — "
                "es wird kein Darlehen mehr benötigt."
            )
        elif ergebnis["ersparnis_zinsen"] > 0:
            st.info(
                f"**Ergebnis:** Durch {sparjahre:.0f} Jahre Ansparen und den niedrigeren "
                f"Bauspar-Darlehenszins ({zins_bauspar_darlehen:.2f} % vs. {zins_markt_zukunft:.2f} % Marktzins) "
                f"ergibt sich eine rechnerische Zinsersparnis von **{fmt_euro(ergebnis['ersparnis_zinsen'])}**."
            )
        else:
            st.warning(
                "In diesem Szenario ergibt sich keine Zinsersparnis — "
                "der Bauspar-Darlehenszins liegt über dem erwarteten Marktzins."
            )

    with col_r:
        fig = go.Figure()
        fig.add_trace(go.Bar(
            name="Ohne Bausparen",
            x=["Darlehen", "Zinskosten", "Monatsrate"],
            y=[ergebnis["finanzierungssumme"], ergebnis["szenario_a"]["gesamt_zinsen"], ergebnis["szenario_a"]["monatsrate"]],
            marker_color="#c62828",
            text=[fmt_euro(ergebnis["finanzierungssumme"]), fmt_euro(ergebnis["szenario_a"]["gesamt_zinsen"]), fmt_euro(ergebnis["szenario_a"]["monatsrate"])],
            textposition="inside",
            textfont=dict(color="white", size=9),
        ))
        fig.add_trace(go.Bar(
            name="Mit Bauansparprogramm",
            x=["Darlehen", "Zinskosten", "Monatsrate"],
            y=[ergebnis["restsumme_darlehen"], ergebnis["szenario_b"]["gesamt_zinsen"], ergebnis["szenario_b"]["monatsrate"]],
            marker_color="#2e7d32",
            text=[fmt_euro(ergebnis["restsumme_darlehen"]), fmt_euro(ergebnis["szenario_b"]["gesamt_zinsen"]), fmt_euro(ergebnis["szenario_b"]["monatsrate"])],
            textposition="inside",
            textfont=dict(color="white", size=9),
        ))
        fig.update_layout(
            barmode="group",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=20, r=20, t=30, b=20),
            height=260,
            yaxis=dict(showgrid=True, gridwidth=1, type="log"),
            xaxis=dict(showgrid=False),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )
        st.plotly_chart(fig, use_container_width=True, theme="streamlit")
        st.caption("Logarithmische Skala, damit Monatsrate und Gesamtsummen vergleichbar bleiben.")

    st.markdown("---")
    st.markdown("### Aufbau des Guthabens während der Ansparphase")

    if ergebnis["ansparung"]["verlauf"]:
        verlauf = ergebnis["ansparung"]["verlauf"]
        jahre = [v["jahr"] for v in verlauf]
        eingezahlt = [v["eingezahlt"] for v in verlauf]
        guthaben = [v["guthaben"] for v in verlauf]

        fig_v = go.Figure()
        fig_v.add_trace(go.Scatter(
            x=jahre, y=eingezahlt, mode="lines", name="Eingezahlt",
            line=dict(color="#66bb6a", width=2),
            fill="tozeroy",
        ))
        fig_v.add_trace(go.Scatter(
            x=jahre, y=guthaben, mode="lines", name="Guthaben inkl. Zinsen",
            line=dict(color="#2e7d32", width=3),
        ))
        fig_v.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=20, r=20, t=20, b=30),
            height=240,
            yaxis=dict(title="€", showgrid=True, gridwidth=1),
            xaxis=dict(title="Jahre", showgrid=False),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )
        st.plotly_chart(fig_v, use_container_width=True, theme="streamlit")
    else:
        st.caption("Keine Ansparphase — Finanzierungsstart ist im aktuellen Jahr.")

    # Förderungs-Info
    if foerderung["foerderung_gesamt"] > 0:
        st.markdown("### Staatliche Förderung")
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            st.metric("Wohnungsbauprämie", fmt_euro(foerderung["wop_gesamt"]))
            st.caption(f"{fmt_euro(foerderung['wop_pro_jahr'])}/Jahr")
        with col_f2:
            st.metric("AN-Sparzulage", fmt_euro(foerderung["an_zulage_gesamt"]))
            st.caption(f"{fmt_euro(foerderung['an_zulage_pro_jahr'])}/Jahr")
        with col_f3:
            st.metric("Förderung gesamt", fmt_euro(foerderung["foerderung_gesamt"]))
            st.caption(f"über {sparjahre:.0f} Jahre")
    else:
        st.info(
            "Hinweis: Keine staatliche Förderung berücksichtigt — ggf. Einkommen zu hoch "
            "oder kein VL-Anteil. Grenzen: 35 T€ (Single) bzw. 70 T€ (Paar) für Wohnungsbauprämie."
        )

# ---------- TAB: START-SZENARIEN ----------
with tab_szen:
    st.markdown("### Was passiert bei späterem Start?")
    st.caption(
        "Vergleich eines sofortigen Starts mit einem Start in 2/5/10 Jahren. "
        "Je später gestartet wird, desto weniger Zeit bleibt zum Ansparen — "
        "die verbleibende Darlehenssumme steigt und die Ersparnis sinkt."
    )

    start_offsets = [0, 2, 5, 10]
    szenarien = berechne_startzeitpunkt_szenarien(
        finanzierungssumme=finanzierungssumme,
        monatliche_sparrate=monatliche_sparrate,
        max_sparjahre=sparjahre,
        zins_bauspar_guthaben=zins_bauspar_guthaben,
        zins_bauspar_darlehen=zins_bauspar_darlehen,
        zins_markt_zukunft=zins_markt_zukunft,
        finanzierungslaufzeit=finanzierungslaufzeit,
        foerderung_pro_jahr=foerderung["foerderung_pro_jahr"],
        start_offsets=start_offsets,
    )

    col_s1, col_s2 = st.columns([1, 2])

    with col_s1:
        df_szen = pd.DataFrame({
            "Start in": [f"+{s['start_in_jahren']} J." for s in szenarien],
            "Sparjahre": [f"{s['sparjahre']:.0f}" for s in szenarien],
            "Guthaben": [fmt_euro(s["guthaben"]) for s in szenarien],
            "Monatsrate": [fmt_euro(s["monatsrate"]) for s in szenarien],
            "Verlust": [fmt_euro(s.get("verlust_vs_sofort", 0)) for s in szenarien],
        })
        st.dataframe(df_szen, use_container_width=True, hide_index=True)
        st.caption("Verlust = Mehr-Zinskosten ggü. einem sofortigen Start.")

    with col_s2:
        fig_s = go.Figure()
        fig_s.add_trace(go.Bar(
            name="Zinskosten",
            x=[f"+{s['start_in_jahren']} J." for s in szenarien],
            y=[s["gesamt_zinsen"] for s in szenarien],
            marker_color=["#2e7d32", "#81c784", "#f57c00", "#c62828"],
            text=[fmt_euro(s["gesamt_zinsen"]) for s in szenarien],
            textposition="inside",
            textfont=dict(color="white", size=10),
        ))
        fig_s.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=20, r=20, t=20, b=30),
            height=260,
            yaxis=dict(showgrid=True, gridwidth=1, title="€ Zinskosten"),
            xaxis=dict(showgrid=False, title="Verzögerung des Sparbeginns"),
            showlegend=False,
        )
        st.plotly_chart(fig_s, use_container_width=True, theme="streamlit")

    if len(szenarien) >= 2 and szenarien[-1].get("verlust_vs_sofort", 0) > 1000:
        verlust_10j = szenarien[-1]["verlust_vs_sofort"]
        st.info(
            f"Ein um 10 Jahre verspäteter Start führt in diesem Beispiel zu "
            f"rund **{fmt_euro(verlust_10j)}** zusätzlichen Zinskosten."
        )

# ---------- TAB: CASHFLOW ----------
with tab_cash:
    st.markdown("### Monatliche Belastung & Cashflow")

    col_c1, col_c2 = st.columns(2)

    with col_c1:
        st.markdown("**Während der Sparphase**")
        st.metric("Monatliche Sparrate", fmt_euro(monatliche_sparrate))
        st.caption(f"über {sparjahre:.0f} Jahre")

        st.markdown("**Während der Finanzierung**")
        st.metric(
            "Monatsrate mit Bausparen",
            fmt_euro(ergebnis["szenario_b"]["monatsrate"]),
        )
        st.metric(
            "Monatsrate ohne Bausparen",
            fmt_euro(ergebnis["szenario_a"]["monatsrate"]),
        )
        diff = ergebnis["szenario_a"]["monatsrate"] - ergebnis["szenario_b"]["monatsrate"]
        if diff > 0:
            st.success(f"Monatliche Entlastung: {fmt_euro(diff)}")

    with col_c2:
        # Cashflow-Diagramm über Gesamtzeitraum
        gesamt_jahre = int(sparjahre) + finanzierungslaufzeit
        x = list(range(1, gesamt_jahre + 1))
        cashflow_mit = []
        cashflow_ohne = []
        for jahr in x:
            if jahr <= sparjahre:
                cashflow_mit.append(monatliche_sparrate * 12)
                cashflow_ohne.append(0.0)
            else:
                cashflow_mit.append(ergebnis["szenario_b"]["monatsrate"] * 12)
                cashflow_ohne.append(ergebnis["szenario_a"]["monatsrate"] * 12)

        fig_c = go.Figure()
        fig_c.add_trace(go.Scatter(
            x=x, y=cashflow_ohne, mode="lines",
            name="Ohne Bausparen (nur Finanzierung)",
            line=dict(color="#c62828", width=3),
            fill="tozeroy",
        ))
        fig_c.add_trace(go.Scatter(
            x=x, y=cashflow_mit, mode="lines",
            name="Mit Bauansparprogramm",
            line=dict(color="#2e7d32", width=3),
        ))
        fig_c.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=20, r=20, t=20, b=30),
            height=260,
            yaxis=dict(title="€/Jahr", showgrid=True, gridwidth=1),
            xaxis=dict(title="Jahr seit Beginn", showgrid=False),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )
        st.plotly_chart(fig_c, use_container_width=True, theme="streamlit")

    st.caption(
        "Mit Bausparen: konstante Belastung in beiden Phasen (Sparrate, dann niedrigere Monatsrate). "
        "Ohne Bausparen: keine Belastung vorab, aber höhere Monatsrate in der Finanzierung."
    )

# ---------- TAB: STRESS-TEST ----------
with tab_stress:
    st.markdown("### Zinsrisiko-Stresstest")
    st.caption(
        "Was passiert, wenn der Marktzins zur Finanzierung stark steigt? "
        "Der Bauspardarlehen-Zins ist vertraglich garantiert — unabhängig vom Marktzins."
    )

    stress_zinsen = [3.0, 5.0, 7.0, 9.0]
    stress = berechne_stresstest(
        finanzierungssumme=finanzierungssumme,
        monatliche_sparrate=monatliche_sparrate,
        sparjahre=sparjahre,
        zins_bauspar_guthaben=zins_bauspar_guthaben,
        zins_bauspar_darlehen=zins_bauspar_darlehen,
        finanzierungslaufzeit=finanzierungslaufzeit,
        foerderung_gesamt=foerderung["foerderung_gesamt"],
        stress_zinsen=stress_zinsen,
    )

    col_st1, col_st2 = st.columns([1, 2])

    with col_st1:
        df_st = pd.DataFrame({
            "Marktzins": [f"{s['markt_zins']:.1f} %" for s in stress],
            "Rate ohne": [fmt_euro(s["rate_ohne_bausparen"]) for s in stress],
            "Rate mit": [fmt_euro(s["rate_mit_bausparen"]) for s in stress],
            "Ersparnis": [fmt_euro(s["ersparnis"]) for s in stress],
        })
        st.dataframe(df_st, use_container_width=True, hide_index=True)

    with col_st2:
        fig_st = go.Figure()
        fig_st.add_trace(go.Bar(
            name="Ohne Bausparen",
            x=[f"{s['markt_zins']:.1f}%" for s in stress],
            y=[s["rate_ohne_bausparen"] for s in stress],
            marker_color="#c62828",
            text=[fmt_euro(s["rate_ohne_bausparen"]) for s in stress],
            textposition="inside",
            textfont=dict(color="white", size=9),
        ))
        fig_st.add_trace(go.Bar(
            name="Mit Bauansparprogramm",
            x=[f"{s['markt_zins']:.1f}%" for s in stress],
            y=[s["rate_mit_bausparen"] for s in stress],
            marker_color="#2e7d32",
            text=[fmt_euro(s["rate_mit_bausparen"]) for s in stress],
            textposition="inside",
            textfont=dict(color="white", size=9),
        ))
        fig_st.update_layout(
            barmode="group",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=20, r=20, t=20, b=30),
            height=260,
            yaxis=dict(title="€ Monatsrate", showgrid=True, gridwidth=1),
            xaxis=dict(showgrid=False, title="Marktzins-Szenario"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )
        st.plotly_chart(fig_st, use_container_width=True, theme="streamlit")

    max_ersp = max((s["ersparnis"] for s in stress), default=0)
    if max_ersp > 0:
        st.info(
            f"Bei einem Marktzins von 9 % ergibt sich in diesem Beispiel eine "
            f"rechnerische Zinsersparnis von bis zu **{fmt_euro(max_ersp)}**."
        )

# ---------- TAB: ZINSHISTORIE ----------
with tab_hist:
    st.markdown("### Historische Baufinanzierungszinsen 2000–2025")
    st.caption(
        "Orientierung für realistische Zins-Annahmen. "
        f"Quellen: {QUELLEN}. Stand: {STAND_ZINSEN}."
    )

    stats = get_zins_statistik()
    col_h1, col_h2, col_h3 = st.columns(3)
    with col_h1:
        st.metric("Minimum", f"{stats['min']:.2f} %")
    with col_h2:
        st.metric("Durchschnitt", f"{stats['durchschnitt']:.2f} %")
    with col_h3:
        st.metric("Maximum", f"{stats['max']:.2f} %")

    jahre = sorted(ZINSEN_HISTORISCH.keys())
    baufi = [ZINSEN_HISTORISCH[j]["baufinanzierung"] for j in jahre]
    guthaben = [ZINSEN_HISTORISCH[j]["bauspar_guthaben"] for j in jahre]
    darlehen = [ZINSEN_HISTORISCH[j]["bauspar_darlehen"] for j in jahre]
    leitzins = [ZINSEN_HISTORISCH[j]["leitzins"] for j in jahre]

    fig_h = go.Figure()
    fig_h.add_trace(go.Scatter(
        x=jahre, y=baufi, mode="lines+markers", name="Baufinanzierung (10 J.)",
        line=dict(color="#c62828", width=3),
    ))
    fig_h.add_trace(go.Scatter(
        x=jahre, y=darlehen, mode="lines+markers", name="Bauspar-Darlehen",
        line=dict(color="#f57c00", width=2, dash="dash"),
    ))
    fig_h.add_trace(go.Scatter(
        x=jahre, y=guthaben, mode="lines+markers", name="Bauspar-Guthaben",
        line=dict(color="#2e7d32", width=2),
    ))
    fig_h.add_trace(go.Scatter(
        x=jahre, y=leitzins, mode="lines", name="EZB-Leitzins",
        line=dict(color="#90a4ae", width=1, dash="dot"),
    ))
    fig_h.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=20, b=30),
        height=340,
        yaxis=dict(title="% p. a.", showgrid=True, gridwidth=1),
        xaxis=dict(title="Jahr", showgrid=False),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    st.plotly_chart(fig_h, use_container_width=True, theme="streamlit")

    df_h = pd.DataFrame({
        "Jahr": jahre,
        "Baufinanzierung (%)": baufi,
        "Bauspar-Darlehen (%)": darlehen,
        "Bauspar-Guthaben (%)": guthaben,
        "EZB-Leitzins (%)": leitzins,
    })
    with st.expander("Rohdaten anzeigen"):
        st.dataframe(df_h, use_container_width=True, hide_index=True)

    st.info(
        f"**Einordnung:** In den letzten 25 Jahren schwankte der Baufinanzierungszins zwischen "
        f"{stats['min']:.2f} % (Niedrigzinsphase 2020/2021) und {stats['max']:.2f} % (Anfang 2000er). "
        f"Der Durchschnitt liegt bei **{stats['durchschnitt']:.2f} %** — ein realistischer "
        f"Langfrist-Erwartungswert für konservative Finanzierungsplanung."
    )

# ---------- TAB: PDF EXPORT ----------
with tab_export:
    st.markdown("### PDF-Report")

    col_e1, col_e2 = st.columns(2)
    with col_e1:
        kunde_name = st.text_input("Name (optional)", value="")
    with col_e2:
        beratung_datum = st.date_input("Datum", value=datetime.date.today()).strftime("%d.%m.%Y")

    if st.button("PDF erzeugen", type="primary"):
        eingaben = {
            "Finanzierungssumme": fmt_euro(finanzierungssumme),
            "Geplanter Finanzierungsstart": str(jahr_finanzierung),
            "Sparzeitraum": f"{sparjahre:.0f} Jahre",
            "Monatliche Sparrate": fmt_euro(monatliche_sparrate),
            "Einmalzahlung": fmt_euro(einmalzahlung),
            "Zins Bausparvertrag (Guthaben / Darlehen)": f"{zins_bauspar_guthaben:.2f} % / {zins_bauspar_darlehen:.2f} %",
            "Marktzins (heute / erwartet)": f"{zins_markt_heute:.2f} % / {zins_markt_zukunft:.2f} %",
            "Finanzierungslaufzeit": f"{finanzierungslaufzeit} Jahre",
            "Zu versteuerndes Einkommen": fmt_euro(zve),
            "Verheiratet": "Ja" if verheiratet else "Nein",
        }

        try:
            pdf_bytes = erstelle_pdf(
                kunde_name=kunde_name,
                beratung_datum=beratung_datum,
                eingaben=eingaben,
                ergebnis=ergebnis,
                szenarien=szenarien,
                stresstest=stress,
            )
            st.download_button(
                label="Report herunterladen",
                data=pdf_bytes,
                file_name=f"bausparrechner_{kunde_name or 'kunde'}_{datetime.date.today().isoformat()}.pdf",
                mime="application/pdf",
            )
            st.success("PDF erfolgreich erstellt.")
        except Exception as e:
            st.error(f"Fehler beim PDF-Erstellen: {e}")

# =========================================================================
# FOOTER
# =========================================================================
st.markdown("---")
st.caption(
    f"Zinsdaten Stand: {STAND_ZINSEN} · Alle Berechnungen sind unverbindliche Modellrechnungen · "
    f"© {COPYRIGHT}"
)
