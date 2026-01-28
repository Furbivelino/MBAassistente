import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader

# 1. Recupero API KEY
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
except:
    st.error("Manca la API KEY nei Secrets!")
    st.stop()

# 2. Configurazione - Forziamo l'uso del modello corretto
genai.configure(api_key=API_KEY)

# Proviamo a usare 'gemini-1.5-flash' che è il più compatibile oggi
model = genai.GenerativeModel('gemini-1.5-flash')

st.set_page_config(page_title="Assistente MBA", page_icon="🏥")
st.title("🏥 Assistente Mutua MBA")

uploaded_files = st.file_uploader("Carica i PDF", type="pdf", accept_multiple_files=True)

if uploaded_files:
    full_text = ""
    for pdf_file in uploaded_files:
        reader = PdfReader(pdf_file)
        for page in reader.pages:
            full_text += page.extract_text() + "\n"
    
    st.success("Documenti pronti!")
    
    if prompt := st.chat_input("Chiedimi pure..."):
        st.chat_message("user").write(prompt)
        with st.spinner("Sto consultando i regolamenti..."):
            try:
                # Prompt ottimizzato per evitare errori di versione
                response = model.generate_content(f"Basandoti su questi testi: {full_text}\n\nDomanda: {prompt}")
                st.chat_message("assistant").write(response.text)
            except Exception as e:
                st.error(f"Si è verificato un errore: {e}")
