import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import os

# --- CONFIGURAZIONE ---
# Cerchiamo la chiave nel "Caveau" di Streamlit
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
except:
    st.error("Manca la API KEY! Impostala nei 'Secrets' di Streamlit.")
    st.stop()

genai.configure(api_key=API_KEY)
# Usiamo il modello Flash perché ha tanta memoria ed è veloce
model = genai.GenerativeModel('gemini-1.5-flash')

# --- INTERFACCIA WEB ---
st.set_page_config(page_title="Assistente MBA", page_icon="🏥")
st.title("🏥 Assistente Virtuale Mutua MBA")
st.markdown("Carica i documenti PDF (Regolamento, Guida, Strutture) e fai una domanda.")

# --- CARICAMENTO FILE ---
uploaded_files = st.file_uploader("Carica i tuoi PDF qui", type="pdf", accept_multiple_files=True)

full_text = ""

if uploaded_files:
    with st.status("Sto leggendo i documenti...", expanded=True) as status:
        for pdf_file in uploaded_files:
            try:
                reader = PdfReader(pdf_file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                full_text += f"\n--- DOCUMENTO: {pdf_file.name} ---\n{text}"
                st.write(f"✅ Letto: {pdf_file.name}")
            except Exception as e:
                st.error(f"Errore su {pdf_file.name}: {e}")
        status.update(label="Lettura completata!", state="complete", expanded=False)

    st.success(f"Ho memorizzato i documenti. Sono pronto!")

    # --- CHAT ---
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Fai una domanda sui documenti..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Consulto i documenti..."):
                try:
                    final_prompt = f"""
                    Sei un assistente esperto per la Mutua MBA.
                    Rispondi basandoti SOLO su questi documenti:
                    {full_text}
                    
                    Domanda: {prompt}
                    """
                    response = model.generate_content(final_prompt)
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                except Exception as e:
                    st.error(f"Errore: {e}")
