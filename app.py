import streamlit as st
import requests
import pandas as pd

# Configurazione della pagina
st.set_page_config(page_title="Corporate OSINT Dashboard", page_icon="🕵️‍♂️", layout="wide")
st.title("🕵️‍♂️ OSINT Dashboard Aziendale")

# Creiamo due "Tab" (schede) per dividere i due strumenti
tab1, tab2 = st.tabs(["✈️ Radar Airbus (Live)", "🏎️ Brevetti Ferrari"])

# --- TAB 1: AIRBUS ---
with tab1:
    st.header("Intercettazione Voli (Tolosa)")
    if st.button("📡 Scansiona Spazio Aereo"):
        with st.spinner("Ricerca in corso..."):
            lamin, lamax, lomin, lomax = 43.5, 43.7, 1.3, 1.5
            url = f"https://opensky-network.org/api/states/all?lamin={lamin}&lomin={lomin}&lamax={lamax}&lomax={lomax}"
            try:
                res = requests.get(url, timeout=10 ).json()
                if res['states']:
                    st.success(f"Trovati {len(res['states'])} aerei!")
                    voli = [{'ICAO': a[0], 'Volo': str(a[1]).strip(), 'Nazione': a[2], 'Altitudine': a[7]} for a in res['states']]
                    st.dataframe(pd.DataFrame(voli), use_container_width=True)
                else:
                    st.warning("Nessun aereo rilevato in questo momento.")
            except Exception as e:
                st.error("Errore di connessione al radar.")

# --- TAB 2: FERRARI ---
with tab2:
    st.header("Monitoraggio Tecnologie (OpenAlex)")
    if st.button("📄 Cerca Ultimi Brevetti"):
        with st.spinner("Estrazione documenti..."):
            url = "https://api.openalex.org/works?search=ferrari&per-page=5&sort=publication_year:desc"
            try:
                res = requests.get(url ).json()
                risultati = res.get('results', [])
                for item in risultati:
                    st.info(f"**[{item.get('publication_year')}]** {item.get('title')}")
            except Exception as e:
                st.error("Errore di connessione al database.")
