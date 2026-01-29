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
st.title("🏥 Assistente MBAfesica")

# --- 3. BARRA LATERALE PER I PDF ---
with st.sidebar:
    st.header("Documenti")
    uploaded_files = st.file_uploader("Carica i PDF (max 3-4 alla volta)", type="pdf", accept_multiple_files=True)
    
    if uploaded_files:
        testo_estratto = ""
        for uploaded_file in uploaded_files:
            reader = PdfReader(uploaded_file)
            for page in reader.pages:
                t = page.extract_text()
                if t: testo_estratto += t + "\n"
        # Salviamo il testo ed evitiamo che superi i 25.000 caratteri per sicurezza
        st.session_state.full_text = testo_estratto[:25000] 
        st.success("Documenti pronti!")
    
    if st.button("Svuota Chat"):
        st.session_state.messages = []
        st.rerun()

# --- 4. CHAT ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Chiedimi dei rimborsi o delle strutture..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("Ricerca in corso..."):
            try:
                # CAMBIO MODELLO: Usiamo 'llama-3.1-8b-instant' che ha limiti molto più alti
                response = client.chat.completions.create(
                    model="llama-3.1-8b-instant", 
                    messages=[
                        {"role": "system", "content": f"Sei l'assistente Mutua MBA. Rispondi usando questo testo: {st.session_state.full_text}"},
                        *st.session_state.messages[-5:] # Ricorda gli ultimi 5 messaggi
                    ],
                    temperature=0.1,
                )
                
                risposta = response.choices[0].message.content
                st.markdown(risposta)
                st.session_state.messages.append({"role": "assistant", "content": risposta})
                
            except Exception as e:
                st.error(f"Errore tecnico: {e}")
                st.info("Consiglio: Se l'errore persiste, prova a caricare un solo PDF alla volta.")
