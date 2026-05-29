import streamlit as st
import requests
import pandas as pd
import os
import base64
from pathlib import Path

# Configurazione della pagina
st.set_page_config(
    page_title="Gotham Project: Intelligence & Surveillance",
    page_icon="🦇",
    layout="wide"
)

# --- HEADER CON LOGO GOTHAM ---
def get_logo_base64():
    """Carica il logo come base64 per visualizzarlo inline."""
    logo_path = Path(__file__).parent / "gotham_logo.png"
    if logo_path.exists():
        with open(logo_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

logo_b64 = get_logo_base64()
if logo_b64:
    st.markdown(
        f"""
        <div style="display: flex; align-items: center; gap: 20px; margin-bottom: 10px;">
            <img src="data:image/png;base64,{logo_b64}" style="height: 80px; width: auto;">
            <div>
                <h1 style="margin: 0; padding: 0; font-size: 2.2rem; font-weight: 900; letter-spacing: 2px;">
                    Gotham Project: Intelligence & Surveillance
                </h1>
                <p style="margin: 0; color: #888; font-size: 0.9rem; letter-spacing: 1px;">
                    A.I. Predictive Intelligence Platform
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    st.title("🦇 Gotham Project: Intelligence & Surveillance")

st.divider()

# --- FUNZIONE: ANALISI PREDITTIVA CON A.I. ---
def analizza_con_ai(tipo, dati_testo):
    """Invia i dati raccolti a DeepSeek e restituisce un briefing predittivo."""
    api_key = os.environ.get("DEEPSEEK_API_KEY", "")
    if not api_key:
        return "⚠️ Chiave API non configurata. Aggiungi DEEPSEEK_API_KEY nei Secrets di Streamlit Cloud."

    if tipo == "airbus":
        prompt_sistema = (
            "Sei un analista di intelligence aeronautica e industriale. "
            "Ricevi dati sui voli rilevati sopra Tolosa (sede di Airbus). "
            "Analizza i dati e fornisci un briefing predittivo professionale: "
            "interpreta l'attività aerea, ipotizza cosa sta succedendo nello stabilimento "
            "e fai una previsione sull'attività produttiva di Airbus nelle prossime settimane. "
            "Rispondi in italiano, in modo conciso e strutturato con titoli e punti chiave."
        )
        prompt_utente = f"Ecco i dati dei voli rilevati sopra Tolosa in questo momento:\n\n{dati_testo}\n\nFornisci il tuo briefing predittivo."
    else:
        prompt_sistema = (
            "Sei un analista di intelligence tecnologica e brevettuale. "
            "Ricevi un elenco di pubblicazioni scientifiche e brevetti recenti di Ferrari. "
            "Analizza i titoli e le date, individua i pattern tecnologici ricorrenti "
            "e fai una previsione su quale direzione tecnologica sta prendendo Ferrari "
            "e quale potrebbe essere il prossimo prodotto o innovazione. "
            "Rispondi in italiano, in modo conciso e strutturato con titoli e punti chiave."
        )
        prompt_utente = f"Ecco i brevetti/pubblicazioni recenti di Ferrari:\n\n{dati_testo}\n\nFornisci il tuo briefing predittivo."

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": prompt_sistema},
            {"role": "user", "content": prompt_utente}
        ],
        "temperature": 0.7,
        "max_tokens": 800
    }
    try:
        risposta = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        risposta.raise_for_status()
        return risposta.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"❌ Errore nella chiamata all'A.I.: {str(e)}"


# Creiamo due "Tab" (schede) per dividere i due strumenti
tab1, tab2 = st.tabs(["✈️ Radar Airbus (Live)", "🏎️ Brevetti Ferrari"])

# --- TAB 1: AIRBUS (ADS-B Exchange - nessuna chiave richiesta) ---
with tab1:
    st.header("Intercettazione Voli (Tolosa)")
    st.caption("Fonte: ADS-B Exchange — dati in tempo reale, nessuna chiave API richiesta")

    if st.button("📡 Scansiona Spazio Aereo"):
        with st.spinner("Ricerca in corso..."):
            url = "https://api.adsb.lol/v2/lat/43.6/lon/1.4/dist/50"
            try:
                res = requests.get(url, timeout=30).json()
                aerei = res.get("ac", [])
                if aerei:
                    st.success(f"Trovati {len(aerei)} aerei nel raggio di 50km da Tolosa!")
                    voli = []
                    for a in aerei:
                        # Gestione valori misti (es. 'ground' invece di numero)
                        alt_raw = a.get('alt_baro', None)
                        try:
                            alt_val = int(alt_raw) if alt_raw not in (None, 'ground', '') else 0
                        except (ValueError, TypeError):
                            alt_val = 0
                        gs_raw = a.get('gs', None)
                        try:
                            gs_val = round(float(gs_raw), 1) if gs_raw not in (None, '') else 0.0
                        except (ValueError, TypeError):
                            gs_val = 0.0
                        voli.append({
                            'ICAO': a.get('hex', '').upper(),
                            'Volo': str(a.get('flight', '')).strip(),
                            'Tipo Aereo': str(a.get('t', 'N/D')),
                            'Matricola': str(a.get('r', 'N/D')),
                            'Altitudine (ft)': alt_val,
                            'Velocità (kt)': gs_val,
                            'Nazione': 'France' if str(a.get('hex', '')).startswith('3') else 'Internazionale'
                        })
                    df_voli = pd.DataFrame(voli)
                    st.dataframe(df_voli, use_container_width=True)
                    st.session_state['dati_airbus'] = df_voli.to_string(index=False)
                    st.session_state['airbus_trovati'] = True
                else:
                    st.warning("Nessun aereo rilevato in questo momento.")
                    st.session_state['airbus_trovati'] = False
            except Exception as e:
                st.error(f"Errore di connessione al radar: {str(e)}")
                st.session_state['airbus_trovati'] = False

    if st.session_state.get('airbus_trovati'):
        st.divider()
        if st.button("🤖 Analizza con A.I. Predittiva", key="ai_airbus", type="primary"):
            with st.spinner("L'A.I. sta elaborando il briefing predittivo..."):
                briefing = analizza_con_ai("airbus", st.session_state['dati_airbus'])
            st.subheader("📊 Briefing Predittivo — Attività Airbus")
            st.markdown(briefing)


# --- TAB 2: FERRARI ---
with tab2:
    st.header("Monitoraggio Tecnologie (OpenAlex)")
    if st.button("📄 Cerca Ultimi Brevetti"):
        with st.spinner("Estrazione documenti..."):
            url = "https://api.openalex.org/works?search=ferrari&per-page=5&sort=publication_year:desc"
            try:
                res = requests.get(url).json()
                risultati = res.get('results', [])
                testo_brevetti = ""
                for item in risultati:
                    anno = item.get('publication_year')
                    titolo = item.get('title')
                    st.info(f"**[{anno}]** {titolo}")
                    testo_brevetti += f"[{anno}] {titolo}\n"
                st.session_state['dati_ferrari'] = testo_brevetti
                st.session_state['ferrari_trovati'] = True
            except Exception as e:
                st.error("Errore di connessione al database.")
                st.session_state['ferrari_trovati'] = False

    if st.session_state.get('ferrari_trovati'):
        st.divider()
        if st.button("🤖 Analizza con A.I. Predittiva", key="ai_ferrari", type="primary"):
            with st.spinner("L'A.I. sta elaborando il briefing predittivo..."):
                briefing = analizza_con_ai("ferrari", st.session_state['dati_ferrari'])
            st.subheader("📊 Briefing Predittivo — Direzione Tecnologica Ferrari")
            st.markdown(briefing)
