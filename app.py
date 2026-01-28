import streamlit as st
import google.generativeai as genai

st.title("Diagnosi Assistente MBA")

try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=API_KEY)
    
    st.write("🔎 Controllo i modelli disponibili per la tua chiave...")
    
    available_models = [m.name for m in genai.list_models()]
    
    st.success("Chiave collegata! Ecco i modelli che puoi usare:")
    st.write(available_models)
    
    if 'models/gemini-1.5-flash' in available_models:
        st.balloons()
        st.write("✅ Il modello Flash è disponibile! Possiamo procedere.")
    else:
        st.warning("⚠️ Il modello Flash NON è nella lista. La tua chiave è limitata.")

except Exception as e:
    st.error(f"Errore di connessione: {e}")
    st.info("Se leggi 'API Key not found', la chiave è sbagliata. Se leggi 403, la chiave è bloccata.")
