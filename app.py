import streamlit as st
from groq import Groq
from pypdf import PdfReader

# 1. Configurazione Groq
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Manca la GROQ_API_KEY nei Secrets!")
    st.stop()

st.set_page_config(page_title="Assistente MBA", page_icon="🏥")
st.title("🏥 Assistente MBAfesica")

# Possibilità di caricare più file contemporaneamente
uploaded_files = st.file_uploader("Carica i PDF (Regolamenti, Guide, Integrazioni)", type="pdf", accept_multiple_files=True)

if uploaded_files:
    full_text = ""
    with st.spinner("Lettura dei documenti in corso..."):
        for uploaded_file in uploaded_files:
            reader = PdfReader(uploaded_file)
            for page in reader.pages:
                content = page.extract_text()
                if content:
                    full_text += content + "\n"
    
    st.success(f"Analisi completata! Ho letto tutto il materiale.")

    if prompt := st.chat_input("Chiedimi pure: 'Cosa copre la garanzia X?'"):
        st.chat_message("user").write(prompt)
        
        with st.spinner("Sto cercando nei regolamenti..."):
            try:
                # Abbiamo alzato il limite a 100.000 caratteri!
                context = full_text[:100000] 
                
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": "Sei l'assistente ufficiale della Mutua MBA. Rispondi in modo tecnico ma chiaro, citando se possibile le sezioni del testo. Se la risposta non è nel testo, consiglia di contattare la centrale salute."},
                        {"role": "user", "content": f"DOCUMENTI:\n{context}\n\nDOMANDA:\n{prompt}"}
                    ],
                    temperature=0.1, 
                )
                st.chat_message("assistant").write(response.choices[0].message.content)
            except Exception as e:
                st.error(f"Errore: {e}")
