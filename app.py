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
st.title("⚖️ Assistente MBAfesica")

# --- SIDEBAR DOCUMENTI ---
with st.sidebar:
    st.header("Documentazione")
    uploaded_files = st.file_uploader("Carica i PDF del Piano Sanitario", type="pdf", accept_multiple_files=True)
    if uploaded_files:
        testo = ""
        for f in uploaded_files:
            reader = PdfReader(f)
            for page in reader.pages:
                t = page.extract_text()
                if t: testo += f"--- DOC: {f.name} ---\n{t}\n"
        # Limite prudenziale per evitare Error 413 su Groq Free
        st.session_state.full_text = testo[:22000] 
        st.success("Documenti analizzati e pronti.")
    
    if st.button("Pulisci Conversazione"):
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
                # SYSTEM PROMPT MIRATO (MODALITÀ LIQUIDATORE)
                system_instruction = (
                    "Sei un Liquidatore Sinistri esperto della Mutua MBA. Il tuo obiettivo è fornire risposte "
                    "estremamente tecniche, precise e basate unicamente sui documenti forniti.\n\n"
                    "Segui rigorosamente questo schema di analisi per ogni domanda:\n"
                    "1. IDENTIFICAZIONE PRESTAZIONE: Capisci se si tratta di Ricovero, Alta Diagnostica, o Prevenzione.\n"
                    "2. VERIFICA NETWORK: Controlla se l'utente nomina una struttura. Se è San Camillo (o simile), "
                    "spiega la differenza tra strutture convenzionate (copertura 100%) e fuori rete (massimali ridotti).\n"
                    "3. RICERCA MASSIMALI: Cita il tetto massimo di spesa (es. €100.000 per ricoveri).\n"
                    "4. APPLICAZIONE FRANCHIGIE/SCOPERTI: Indica se ci sono quote a carico dell'associato (es. €30 per esame).\n"
                    "5. CONCLUSIONE: Se l'informazione specifica non c'è, indica esattamente quale capitolo del "
                    "regolamento dovrebbe consultare l'utente.\n\n"
                    "Usa grassetti per i valori monetari e tabelle se devi confrontare opzioni."
                )

                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": system_instruction},
                        {"role": "system", "content": f"CONTESTO DOCUMENTI:\n{st.session_state.full_text}"},
                        *st.session_state.messages[-3:]
                    ],
                    temperature=0.1, # Bassissima creatività, massima fedeltà al testo
                )
                
                answer = response.choices[0].message.content
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
                
            except Exception as e:
                st.error(f"Errore: {e}")
