import streamlit as st
from agent_logic import graph
from state import MusicProfile
from icalendar import Calendar, Event
from datetime import datetime
import io

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Music Agent 2026", layout="wide", page_icon="🎵")

# --- CSS AD ALTO CONTRASTO (Slide 7: UX/UI Design) ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #0f0f0f 0%, #1a1a2e 100%); }
    .main-title { 
        font-size: 3rem !important; font-weight: 800; 
        color: #1DB954; text-align: center; margin-bottom: 20px; 
    }
    /* Forza testo bianco per leggibilità (Huyen, Pag. 288) */
    .stApp p, .stApp li, .stApp span, .stApp div, .stApp label {
        color: #ffffff !important;
        font-size: 1.05rem;
    }
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    /* Chat message contrast */
    [data-testid="stChatMessage"] {
        background-color: rgba(255, 255, 255, 0.08) !important;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- INIZIALIZZAZIONE MEMORIA (Pag. 301) ---
if "profile" not in st.session_state: st.session_state.profile = MusicProfile()
if "chat" not in st.session_state: st.session_state.chat = []
if "last_event" not in st.session_state: st.session_state.last_event = None

# --- SIDEBAR DI ISPEZIONE (Slide 7: Trasparenza) ---
with st.sidebar:
    st.markdown("## 🧠 Memoria Agente")
    st.write("Dati estratti dalle tue richieste:")
    
    # Visualizziamo il profilo strutturato (Integrità Strutturata)
    profile_data = st.session_state.profile.model_dump()
    st.json(profile_data)
    
    st.markdown("---")
    
    # --- SEZIONE DOWNLOAD CALENDARIO ---
    if st.session_state.last_event and st.session_state.last_event.title:
        ev = st.session_state.last_event
        st.success(f"📅 Evento: {ev.title}")
        
        cal = Calendar()
        cal_event = Event()
        cal_event.add('summary', ev.title)
        try:
            dt = datetime.strptime(ev.date, '%Y-%m-%d')
            cal_event.add('dtstart', dt)
        except:
            cal_event.add('dtstart', datetime(2026, 6, 1))
        cal_event.add('location', ev.location or "Da definire")
        cal.add_component(cal_event)
        
        st.download_button(
            label="📥 Scarica Calendario (.ics)",
            data=cal.to_ical(),
            file_name="evento_musicale.ics",
            mime="text/calendar",
            key="download_ics"
        )
    
    if st.button("Reset Conversazione"):
        st.session_state.chat = []
        st.session_state.profile = MusicProfile()
        st.session_state.last_event = None
        st.rerun()

# --- AREA PRINCIPALE ---
st.markdown('<p class="main-title">🎵 Music Orientator Pro</p>', unsafe_allow_html=True)

# Mostra i messaggi della chat
for m in st.session_state.chat:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# --- INPUT UTENTE E LOGICA AGENTE ---
if prompt := st.chat_input("Esempio: Vorrei andare a un concerto Techno a Milano"):
    st.session_state.chat.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Preparazione input per il grafo (Huyen Architecture)
    inputs = {
        "messages": [prompt], 
        "profile": st.session_state.profile, 
        "results": [], 
        "final_response": "",
        "event_details": None
    }
    
    with st.spinner("L'agente sta pianificando ed estraendo informazioni..."):
        # Esecuzione del Grafo LangGraph
        output = graph.invoke(inputs)
        
        # Aggiornamento dello Stato Persistente (Pag. 301)
        st.session_state.profile = output["profile"]
        st.session_state.last_event = output.get("event_details")
        response = output["final_response"]

    with st.chat_message("assistant"):
        st.markdown(response)
    
    st.session_state.chat.append({"role": "assistant", "content": response})
    st.rerun()
