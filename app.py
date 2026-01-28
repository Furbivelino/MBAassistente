import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import time

# 1. Recupero API KEY
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
except:
    st.error("Manca la API KEY nei Secrets!")
    st.stop()

# 2. Configurazione
genai.configure(api_key=API_KEY)

# Usiamo la versione LITE: meno probabile che dia errore 429 (quota)
model = genai.GenerativeModel('gemini-2.0-flash-lite')

st.set_page_config(page_title="Assistente MBA", page_icon="🏥")
st.title("🏥 Assistente Mutua MBA")

# --- CARICAMENTO PDF ---
st.warning("⚠️ Per evitare blocchi, prova a caricare UN SOLO PDF alla volta.")
uploaded_files = st.file_uploader("Carica i PDF", type="pdf", accept_multiple_files=True)

if uploaded_files:
    full_text = ""
    for pdf_file in uploaded_files:
        try:
            reader = PdfReader(pdf_file)
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    full_text += text + "\n"
        except:
            st.error(f"Errore nella lettura di {pdf_file.name}")
    
    if full_text:
        st.success("Documenti caricati!")
    
        # --- CHAT ---
        if prompt := st.chat_input("Fai una domanda (es: cosa copre il pacchetto odontoiatrico?)"):
            st.chat_message("user").write(prompt)
            
            with st.spinner("Sto consultando i documenti..."):
                # Trucco: prendiamo solo i primi 15.000 caratteri per non intasare la quota gratis
                testo_limitato = full_text[:15000] 
                
                try:
                    context = f"Testo dei regolamenti:\n{testo_limitato}\n\nDomanda: {prompt}\nRispondi in italiano."
                    response = model.generate_content(context)
                    st.chat_message("assistant").write(response.text)
                except Exception as e:
                    if "429" in str(e):
                        st.error("🚨 Google dice che stiamo chiedendo troppo velocemente. Aspetta 60 secondi e riprova con un file più piccolo.")
                    else:
                        st.error(f"Errore tecnico: {e}")
