import streamlit as st
from agent_logic import graph
from state import MusicProfile
from icalendar import Calendar, Event
from datetime import datetime
import io

st.set_page_config(page_title="Music Agent 2026", layout="centered", page_icon="📅")

# --- INIEZIONE CSS AGGIORNATO (Migliore Leggibilità) ---
st.markdown("""
    <style>
    /* Sfondo generale */
    .stApp {
        background: linear-gradient(135deg, #0f0f0f 0%, #1a1a2e 100%);
    }
    
    /* Titolo con contrasto elevato */
    .main-title {
        font-size: 3rem !important;
        font-weight: 800;
        background: -webkit-linear-gradient(#1DB954, #1ed760);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 20px;
    }

    /* FORZATURA COLORE TESTO (Leggibilità Massima) */
    /* Questo assicura che ogni paragrafo, lista o testo semplice sia bianco */
    .stApp p, .stApp li, .stApp span, .stApp div {
        color: #f0f0f0 !important;
        font-size: 1.05rem;
        line-height: 1.6;
    }

    /* Box dei messaggi Chat */
    [data-testid="stChatMessage"] {
        background-color: rgba(255, 255, 255, 0.08) !important;
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 15px;
        padding: 15px;
        margin-bottom: 15px;
    }

    /* Sidebar - Testo scuro su sfondo chiaro per contrasto */
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span {
        color: #ffffff !important;
    }

    /* Input Utente */
    .stChatInputContainer textarea {
        color: #ffffff !important;
    }
    
    /* Titoli delle sezioni nella chat */
    h1, h2, h3 {
        color: #1DB954 !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<p class="main-title">🎵 Music Agent Pro</p>', unsafe_allow_html=True)

if "profile" not in st.session_state: st.session_state.profile = MusicProfile()
if "chat" not in st.session_state: st.session_state.chat = []
if "last_event" not in st.session_state: st.session_state.last_event = None

# Visualizzazione Chat
for m in st.session_state.chat:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# Input Utente
if prompt := st.chat_input("Chiedimi di un concerto..."):
    st.session_state.chat.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    inputs = {"messages": [prompt], "profile": st.session_state.profile, "results": [], "final_response": "", "event_details": None}
    
    with st.spinner("L'agente sta lavorando..."):
        output = graph.invoke(inputs)
        st.session_state.profile = output["profile"]
        response = output["final_response"]
        # Salviamo l'evento nello stato della sessione per il download
        st.session_state.last_event = output.get("event_details")

    with st.chat_message("assistant"):
        st.markdown(response)
    
    st.session_state.chat.append({"role": "assistant", "content": response})
    st.rerun()

# --- SEZIONE DOWNLOAD (Fuori dal blocco input per stabilità) ---
if st.session_state.last_event and st.session_state.last_event.title:
    event = st.session_state.last_event
    st.sidebar.success(f"📅 Evento pronto: {event.title}")
    
    cal = Calendar()
    cal_event = Event()
    cal_event.add('summary', event.title)
    try:
        dt = datetime.strptime(event.date, '%Y-%m-%d')
        cal_event.add('dtstart', dt)
    except:
        cal_event.add('dtstart', datetime(2026, 6, 1))
    cal_event.add('location', event.location)
    cal.add_component(cal_event)
    
    st.sidebar.download_button(
        label="📥 Scarica Calendario",
        data=cal.to_ical(),
        file_name="concerto.ics",
        mime="text/calendar",
        key="download_btn"
    )