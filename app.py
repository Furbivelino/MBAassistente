import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader

# 1. Recupero API KEY
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
except:
    st.error("Manca la API KEY nei Secrets!")
    st.stop()

# 2. Configurazione con il modello che abbiamo trovato nella tua lista
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

st.set_page_config(page_title="Assistente MBA", page_icon="🏥")
st.title("🏥 Assistente Mutua MBA")
st.markdown("Carica i regolamenti PDF e chiedimi cosa è coperto o come ottenere rimborsi.")

# --- CARICAMENTO E LETTURA PDF ---
uploaded_files = st.file_uploader("Trascina qui i PDF della Mutua", type="pdf", accept_multiple_files=True)

if uploaded_files:
    full_text = ""
    with st.spinner("Lettura documenti in corso..."):
        for pdf_file in uploaded_files:
            reader = PdfReader(pdf_file)
            for page in reader.pages:
                full_text += page.extract_text() + "\n"
    
    st.success(f"Ho letto {len(uploaded_files)} documenti. Sono pronto!")

    # --- CHAT ---
    if prompt := st.chat_input("Esempio: Cosa copre il pacchetto odontoiatrico?"):
        st.chat_message("user").write(prompt)
        
        with st.spinner("Sto consultando i regolamenti..."):
            try:
                # Chiediamo a Gemini di rispondere basandosi solo sul testo fornito
                context = f"Usa esclusivamente le seguenti informazioni per rispondere alla domanda dell'utente. Se non trovi la risposta, dillo chiaramente.\n\nCONTESTO:\n{full_text}\n\nDOMANDA:\n{prompt}"
                response = model.generate_content(context)
                st.chat_message("assistant").write(response.text)
            except Exception as e:
                st.error(f"C'è stato un piccolo intoppo: {e}")
