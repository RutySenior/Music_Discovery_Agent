import streamlit as st
from agent_logic import graph
from state import MusicProfile

st.set_page_config(page_title="Music Agent 2026", layout="centered")
st.title("Il tuo Orientatore Musicale")

if "profile" not in st.session_state:
    st.session_state.profile = MusicProfile()
if "chat" not in st.session_state:
    st.session_state.chat = []

with st.sidebar:
    st.header("Memoria Agente")
    st.json(st.session_state.profile.model_dump())

for m in st.session_state.chat:
    with st.chat_message(m["role"]): st.write(m["content"])

if prompt := st.chat_input("Di cosa vuoi parlare?"):
    st.session_state.chat.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.write(prompt)

    # Esecuzione Grafo
    inputs = {
        "messages": [prompt], 
        "profile": st.session_state.profile, 
        "results": [],
        "final_response": ""
    }
    output = graph.invoke(inputs)
    
    # Aggiorna lo stato
    st.session_state.profile = output["profile"]
    response = output["final_response"]
    
    if not response:
        response = "Mi mancano informazioni per darti un consiglio mirato. Dimmi un genere o una città!"

    with st.chat_message("assistant"): st.write(response)
    st.session_state.chat.append({"role": "assistant", "content": response})
    st.rerun()