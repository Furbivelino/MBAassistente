import streamlit as st
from groq import Groq
from pypdf import PdfReader

# --- CONFIGURAZIONE GROQ ---
try:
    # Recupera la chiave dai Secrets di Streamlit
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error("Manca la GROQ_API_KEY nei Secrets di Streamlit!")
    st.stop()

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Assistente Mutua MBA", page_icon="🏥", layout="centered")
st.title("🏥 Assistente MBAfesica")
st.markdown("""
Carica i regolamenti e le integrazioni (PDF). 
**Consiglio:** Escludi il file delle Strutture Convenzionate per evitare di superare i limiti di memoria dell'IA.
""")

# --- CARICAMENTO E LETTURA PDF ---
uploaded_files = st.file_uploader(
    "Carica i documenti della Mutua", 
    type="pdf", 
    accept_multiple_files=True
)

if uploaded_files:
    full_text = ""
    with st.spinner("Lettura dei file in corso..."):
        for uploaded_file in uploaded_files:
            try:
                reader = PdfReader(uploaded_file)
                for page in reader.pages:
                    content = page.extract_text()
                    if content:
                        full_text += content + "\n"
            except Exception as e:
                st.warning(f"Impossibile leggere il file {uploaded_file.name}: {e}")
    
    if full_text:
        st.success(f"Analisi completata! Ho letto {len(uploaded_files)} file.")
        
        # --- CHAT INTERFACE ---
        if prompt := st.chat_input("Chiedimi, ad esempio: 'Quanto è il massimale per i ricoveri?'"):
            st.chat_message("user").write(prompt)
            
            with st.spinner("Consulto i regolamenti..."):
                try:
                    # LIMITE TOKEN: Tagliamo il testo a 30.000 caratteri 
                    # per stare abbondantemente sotto i 12.000 token di Groq Free.
                    context_limitato = full_text[:30000]
                    
                    response = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[
                            {
                                "role": "system", 
                                "content": (
                                    "Sei un assistente esperto della Mutua MBA. Rispondi in modo professionale "
                                    "usando esclusivamente le informazioni fornite nei documenti. "
                                    "Se l'informazione non è presente, dillo chiaramente."
                                )
                            },
                            {
                                "role": "user", 
                                "content": f"DOCUMENTI:\n{context_limitato}\n\nDOMANDA:\n{prompt}"
                            }
                        ],
                        temperature=0.1, # Risposte precise e non inventate
                    )
                    
                    risposta = response.choices[0].message.content
                    st.chat_message("assistant").write(risposta)
                    
                except Exception as e:
                    if "rate_limit_exceeded" in str(e):
                        st.error("🚨 Limite di traffico raggiunto. Riprova tra 60 secondi o carica meno documenti.")
                    else:
                        st.error(f"Errore tecnico: {e}")
    else:
        st.error("Non è stato possibile estrarre testo dai PDF. Verifica che non siano solo immagini.")
