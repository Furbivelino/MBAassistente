import streamlit as st
from groq import Groq
from pypdf import PdfReader

# --- 1. INIZIALIZZAZIONE SESSIONE (MEMORIA) ---
if "messages" not in st.session_state:
    st.session_state.messages = [] # Qui salviamo la cronologia della chat
if "full_text" not in st.session_state:
    st.session_state.full_text = "" # Qui salviamo il testo dei PDF per non rileggerli ogni volta

# --- 2. CONFIGURAZIONE GROQ ---
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Manca la chiave API nei Secrets!")
    st.stop()

st.set_page_config(page_title="Assistente MBA", page_icon="🏥")
st.title("🏥 Assistente MBAfesica")

# --- 3. GESTIONE DOCUMENTI ---
with st.sidebar:
    st.header("Documenti")
    uploaded_files = st.file_uploader("Carica i PDF", type="pdf", accept_multiple_files=True)
    
    if uploaded_files:
        testo_estratto = ""
        for uploaded_file in uploaded_files:
            reader = PdfReader(uploaded_file)
            for page in reader.pages:
                testo_estratto += page.extract_text() + "\n"
        st.session_state.full_text = testo_estratto
        st.success("Documenti pronti!")
    
    if st.button("Cancella Cronologia Chat"):
        st.session_state.messages = []
        st.rerun()

# --- 4. VISUALIZZAZIONE CHAT ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 5. LOGICA DI RISPOSTA ---
if prompt := st.chat_input("Chiedimi pure..."):
    # Mostra e salva il messaggio dell'utente
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("Analizzo i documenti e la nostra conversazione..."):
            try:
                # Prepariamo il contesto dai documenti (max 30k caratteri per stare nei limiti free)
                contesto_documenti = st.session_state.full_text[:30000]
                
                # Costruiamo i messaggi per l'IA includendo la cronologia
                history = [
                    {"role": "system", "content": f"Sei l'assistente Mutua MBA. Usa questo testo come riferimento: {contesto_documenti}. Rispondi in italiano in modo preciso."}
                ]
                # Aggiungiamo gli ultimi 4 messaggi per dare memoria
                for m in st.session_state.messages[-5:]:
                    history.append({"role": m["role"], "content": m["content"]})

                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=history,
                    temperature=0.2,
                )
                
                full_response = response.choices[0].message.content
                st.markdown(full_response)
                
                # Salva la risposta dell'IA nella memoria
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                
            except Exception as e:
                if "rate_limit" in str(e).lower():
                    st.error("⏳ Troppe domande ravvicinate! Aspetta 30 secondi e riprova.")
                else:
                    st.error(f"Errore: {e}")
