import streamlit as st
from groq import Groq
from pypdf import PdfReader

# --- MEMORIA E CONFIGURAZIONE ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "full_text" not in st.session_state:
    st.session_state.full_text = ""

try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Configura la API KEY nei Secrets.")
    st.stop()

st.set_page_config(page_title="MBA Expert Assistant", page_icon="⚖️")
st.title("⚖️ Analista MBAfesica")

# --- SIDEBAR DOCUMENTI ---
with st.sidebar:
    st.header("📂 Documentazione")
    uploaded_files = st.file_uploader("Carica i PDF", type="pdf", accept_multiple_files=True)
    if uploaded_files:
        testo = ""
        for f in uploaded_files:
            reader = PdfReader(f)
            for page in reader.pages:
                t = page.extract_text()
                if t: testo += f"--- DOC: {f.name} ---\n{t}\n"
        st.session_state.full_text = testo[:22000] 
        st.success("Documenti caricati.")
    
    if st.button("🗑️ Pulisci Chat"):
        st.session_state.messages = []
        st.rerun()

# --- INTERFACCIA CHAT ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Esempio: Intervento valvola mitrale al San Camillo"):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("Analisi tecnica in corso..."):
            try:
                # SYSTEM PROMPT AGGIORNATO: NESSUNA DELEGA ALL'UTENTE
                system_instruction = (
                    "Sei un Liquidatore Sinistri esperto della Mutua MBA. Il tuo compito è fornire risposte "
                    "COMPLETE e DEFINITIVE basandoti sui testi forniti. NON delegare la ricerca all'utente.\n\n"
                    "Segui rigorosamente questo schema senza eccezioni:\n\n"
                    "1. IDENTIFICAZIONE PRESTAZIONE: Definisci la categoria (es. Ricovero con intervento).\n\n"
                    "2. VERIFICA NETWORK: Se l'utente cita una struttura, spiega che DEVE verificare se è convenzionata. "
                    "POI, esponi chiaramente entrambi gli scenari:\n"
                    "   - SE CONVENZIONATA: riporta la copertura prevista (es. 100%).\n"
                    "   - SE NON CONVENZIONATA: riporta esattamente cosa prevede il regolamento per il fuori rete (es. massimali ridotti o rimborsi forfettari).\n\n"
                    "3. RICERCA MASSIMALI: Cerca nel testo i valori numerici e riportali (es. 100.000€, 8.000€, ecc.). "
                    "Se il testo parla di massimali, DEVI scriverli qui. NON dire 'consulta il manuale'.\n\n"
                    "4. FRANCHIGIE E SCOPERTI: Cerca e mostra i costi fissi a carico dell'associato (es. 30€ a evento o scoperti del 20%).\n\n"
                    "5. CONCLUSIONE: Riassumi la fattibilità della richiesta.\n\n"
                    "IMPORTANTE: Se le informazioni sono presenti nei documenti caricati, DEVI usarle. Sii sintetico ma esaustivo."
                )

                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": system_instruction},
                        {"role": "system", "content": f"CONTESTO DOCUMENTI CARICATI:\n{st.session_state.full_text}"},
                        *st.session_state.messages[-3:]
                    ],
                    temperature=0.1,
                )
                
                answer = response.choices[0].message.content
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
                
            except Exception as e:
                st.error(f"Errore: {e}")
