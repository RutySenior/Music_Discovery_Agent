import streamlit as st
from agent_logic import graph
from state import MusicProfile

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Music Agent 2026", layout="centered", page_icon="🎵")

# --- INIEZIONE CSS (Slide 7: UX/UI Design) ---
st.markdown("""
    <style>
    /* Sfondo e font generale */
    .stApp {
        background: linear-gradient(135deg, #121212 0%, #1e1e2e 100%);
        color: #ffffff;
    }
    
    /* Header personalizzato */
    .main-title {
        font-size: 3rem !important;
        font-weight: 800;
        background: -webkit-linear-gradient(#1DB954, #1ed760);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
    }

    /* Sidebar - Agent Memory (Huyen, Pag. 301) */
    [data-testid="stSidebar"] {
        background-color: rgba(255, 255, 255, 0.05);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Box della Memoria */
    .stJson {
        background-color: #000000 !important;
        border-radius: 10px;
        padding: 10px;
    }

    /* Messaggi Chat */
    .stChatMessage {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border-radius: 15px !important;
        margin-bottom: 10px !important;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Bottone Input */
    .stChatInputContainer {
        border-radius: 30px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- TITOLO ---
st.markdown('<p class="main-title">🎵 Music Orientator</p>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #b3b3b3;">L\'Agente Intelligente per i tuoi concerti e album del 2026</p>', unsafe_allow_html=True)

# --- LOGICA (Invariata) ---
if "profile" not in st.session_state:
    st.session_state.profile = MusicProfile()
if "chat" not in st.session_state:
    st.session_state.chat = []

with st.sidebar:
    st.markdown("### 🧠 Agent Memory")
    st.write("Stato interno estratto via NLP:")
    st.json(st.session_state.profile.model_dump())
    if st.button("Reset Sessione"):
        st.session_state.chat = []
        st.session_state.profile = MusicProfile()
        st.rerun()

# Visualizzazione Chat
for m in st.session_state.chat:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# Gestione Input (Huyen Architecture)
if prompt := st.chat_input("Di che musica o città vuoi parlare?"):
    st.session_state.chat.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Execution (Identica alla precedente)
    inputs = {
        "messages": [prompt], 
        "profile": st.session_state.profile, 
        "results": [],
        "final_response": ""
    }
    
    with st.spinner("L'agente sta consultando il web e pianificando..."):
        output = graph.invoke(inputs)
        st.session_state.profile = output["profile"]
        response = output["final_response"]
        
        if not response:
            response = "Scusami, ho avuto un problema nel processare la tua richiesta musicale."

    with st.chat_message("assistant"):
        st.markdown(response)
    
    st.session_state.chat.append({"role": "assistant", "content": response})
    st.rerun()
