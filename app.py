import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader

# 1. Recupero API KEY
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
except:
    st.error("Manca la API KEY nei Secrets!")
    st.stop()

# 2. Configurazione - Usiamo il modello 1.5 Flash (più leggero per la quota gratis)
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash-latest')

st.set_page_config(page_title="Assistente MBA", page_icon="🏥")
st.title("🏥 Assistente Mutua MBA")
st.info("Consiglio: se i documenti sono grandi, caricali uno alla volta per non esaurire la quota gratuita.")

# --- CARICAMENTO PDF ---
uploaded_files = st.file_uploader("Carica i PDF", type="pdf", accept_multiple_files=True)

if uploaded_files:
    full_text = ""
    for pdf_file in uploaded_files:
        reader = PdfReader(pdf_file)
        for page in reader.pages:
            text = page.extract_text()
            if text:
                full_text += text + "\n"
    
    if full_text:
        st.success("Documenti letti con successo!")
    
        # --- CHAT ---
        if prompt := st.chat_input("Chiedimi pure..."):
            st.chat_message("user").write(prompt)
            
            with st.spinner("Consulto i documenti..."):
                try:
                    # Accorciamo un po' il contesto se è troppo lungo per la versione free
                    context = f"Rispondi alla domanda usando questi documenti: {full_text[:30000]}" 
                    response = model.generate_content([context, prompt])
                    st.chat_message("assistant").write(response.text)
                except Exception as e:
                    if "429" in str(e):
                        st.error("⚠️ Limite gratuito raggiunto. Attendi 1 minuto e riprova con un file più piccolo.")
                    else:
                        st.error(f"Errore: {e}")
