import streamlit as st
from groq import Groq
from pypdf import PdfReader

# 1. Configurazione Iniziale
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error("Errore: Manca la chiave GROQ nei Secrets!")
    st.stop()

st.set_page_config(page_title="Assistente MBA", page_icon="🏥")
st.title("🏥 Assistente MBAfesica")
st.markdown("Carica i tuoi PDF e chiedimi qualunque cosa sui rimborsi e le coperture.")

# --- CARICAMENTO PDF ---
uploaded_file = st.file_uploader("Trascina qui il file PDF (es. IntegraFesica.pdf)", type="pdf")

if uploaded_file:
    # Estrazione del testo
    with st.spinner("Lettura del documento in corso..."):
        reader = PdfReader(uploaded_file)
        full_text = ""
        for page in reader.pages:
            full_text += page.extract_text() + "\n"
    
    st.success("Documento pronto per l'analisi!")

    # --- CHAT ---
    if prompt := st.chat_input("Esempio: Cosa copre il pacchetto maternità?"):
        st.chat_message("user").write(prompt)
        
        with st.spinner("L'IA sta analizzando il regolamento..."):
            try:
                # Usiamo Llama 3.3 70B: è il modello più potente su Groq
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {
                            "role": "system", 
                            "content": "Sei un esperto di fondi sanitari integrativi. Rispondi in modo preciso e professionale usando esclusivamente il testo fornito. Se l'informazione non è presente, dillo chiaramente."
                        },
                        {
                            "role": "user", 
                            "content": f"Documento di riferimento:\n{full_text}\n\nDomanda dell'utente: {prompt}"
                        }
                    ],
                    temperature=0.2, # Teniamo l'IA "seria" e precisa
                )
                
                risposta_testo = response.choices[0].message.content
                st.chat_message("assistant").write(risposta_testo)
                
            except Exception as e:
                st.error(f"Errore nella generazione della risposta: {e}")
