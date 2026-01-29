import streamlit as st
from groq import Groq
from pypdf import PdfReader

# --- 1. MEMORIA DI SESSIONE ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "full_text" not in st.session_state:
    st.session_state.full_text = ""

# --- 2. CONFIGURAZIONE ---
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Manca la chiave API nei Secrets!")
    st.stop()

st.set_page_config(page_title="Assistente MBA", page_icon="🏥")
st.title("🏥 Assistente MBA (Versione Ottimizzata)")

# --- 3. BARRA LATERALE ---
with st.sidebar:
    st.header("📂 Documenti")
    st.info("⚠️ Carica solo i file necessari (es. Regolamento + Integrazione). Escludi le Strutture se cerchi rimborsi.")
    uploaded_files = st.file_uploader("Carica PDF", type="pdf", accept_multiple_files=True)
    
    if uploaded_files:
        testo_estratto = ""
        for uploaded_file in uploaded_files:
            reader = PdfReader(uploaded_file)
            for page in reader.pages:
                t = page.extract_text()
                if t: testo_estratto += t + "\n"
        
        # LIMITE DI SICUREZZA: 18.000 caratteri (~6000 token)
        # Lasciamo spazio per la chat history e la risposta dell'IA
        st.session_state.full_text = testo_estratto[:18000] 
        st.success(f"Documenti pronti ({len(uploaded_files)} file)")
    
    if st.button("🗑️ Svuota Chat"):
        st.session_state.messages = []
        st.rerun()

# --- 4. VISUALIZZAZIONE CHAT ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 5. LOGICA DI RISPOSTA ---
if prompt := st.chat_input("Chiedimi dei rimborsi o delle valvole mitrali..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("Consulto i regolamenti..."):
            try:
                # Torniamo al 70B che ha il limite Token più alto (12k)
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile", 
                    messages=[
                        {
                            "role": "system", 
                            "content": f"Sei l'assistente MBA. Usa questo testo: {st.session_state.full_text}. Rispondi in modo sintetico."
                        },
                        # Inviamo solo gli ULTIMI 2 messaggi per risparmiare spazio prezioso
                        *st.session_state.messages[-3:] 
                    ],
                    temperature=0.1,
                )
                
                risposta = response.choices[0].message.content
                st.markdown(risposta)
                st.session_state.messages.append({"role": "assistant", "content": risposta})
                
            except Exception as e:
                if "rate_limit_exceeded" in str(e):
                    st.error("🚨 Troppi dati! Prova a caricare un solo file o cancella la chat.")
                else:
                    st.error(f"Errore: {e}")
