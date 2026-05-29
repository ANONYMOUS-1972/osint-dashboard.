import streamlit as st
import requests
import pandas as pd
import os

# Configurazione della pagina
st.set_page_config(page_title="Corporate OSINT Dashboard", page_icon="🕵️‍♂️", layout="wide")
st.title("🕵️‍♂️ OSINT Dashboard Aziendale")

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

# --- TAB 1: AIRBUS ---
with tab1:
    st.header("Intercettazione Voli (Tolosa)")
    if st.button("📡 Scansiona Spazio Aereo"):
        with st.spinner("Ricerca in corso..."):
            lamin, lamax, lomin, lomax = 43.5, 43.7, 1.3, 1.5
            url = f"https://opensky-network.org/api/states/all?lamin={lamin}&lomin={lomin}&lamax={lamax}&lomax={lomax}"
            try:
                opensky_user = os.environ.get("OPENSKY_USER", "")
                opensky_pw = os.environ.get("OPENSKY_PW", "")
                auth = (opensky_user, opensky_pw) if opensky_user else None
                res = requests.get(url, auth=auth, timeout=10).json()
                if res['states']:
                    st.success(f"Trovati {len(res['states'])} aerei!")
                    voli = [{'ICAO': a[0], 'Volo': str(a[1]).strip(), 'Nazione': a[2], 'Altitudine': a[7]} for a in res['states']]
                    df_voli = pd.DataFrame(voli)
                    st.dataframe(df_voli, use_container_width=True)

                    # Salviamo i dati in session_state per l'analisi A.I.
                    st.session_state['dati_airbus'] = df_voli.to_string(index=False)
                    st.session_state['airbus_trovati'] = True
                else:
                    st.warning("Nessun aereo rilevato in questo momento.")
                    st.session_state['airbus_trovati'] = False
            except Exception as e:
                st.error("Errore di connessione al radar.")
                st.session_state['airbus_trovati'] = False

    # Pulsante A.I. Predittiva (appare solo dopo la scansione)
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

                # Salviamo i dati in session_state per l'analisi A.I.
                st.session_state['dati_ferrari'] = testo_brevetti
                st.session_state['ferrari_trovati'] = True
            except Exception as e:
                st.error("Errore di connessione al database.")
                st.session_state['ferrari_trovati'] = False

    # Pulsante A.I. Predittiva (appare solo dopo la ricerca brevetti)
    if st.session_state.get('ferrari_trovati'):
        st.divider()
        if st.button("🤖 Analizza con A.I. Predittiva", key="ai_ferrari", type="primary"):
            with st.spinner("L'A.I. sta elaborando il briefing predittivo..."):
                briefing = analizza_con_ai("ferrari", st.session_state['dati_ferrari'])
            st.subheader("📊 Briefing Predittivo — Direzione Tecnologica Ferrari")
            st.markdown(briefing)
