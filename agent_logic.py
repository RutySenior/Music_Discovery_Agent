import os
import json
from groq import Groq
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from state import AgentState, MusicProfile, EventInfo
from tools import search_music_events

load_dotenv(override=True) # override=True forza il ricaricamento dal file .env
api_key = os.getenv("GROQ_API_KEY")

if not api_key or not api_key.startswith("gsk_"):
    raise ValueError("ERRORE: Chiave API Groq non trovata o formato non valido nel file .env")

client = Groq(api_key=api_key)
MODEL = "llama-3.3-70b-versatile"

def parser_node(state):
    msg = state["messages"][-1]
    # Prompt migliorato per definire l'utente come FAN (Pag. 270: Query Rewriting)
    prompt = f"""
    L'utente è un FAN/ASCOLTATORE di musica. 
    Analizza il suo messaggio: "{msg}"
    Estrai in JSON: genre, artists, location, budget.
    Ignora qualsiasi riferimento a 'fare musica' o 'promuoversi', interpreta tutto come preferenze di ascolto.
    """
    try:
        res = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}], 
            model=MODEL, 
            response_format={"type": "json_object"}
        )
        data = json.loads(res.choices[0].message.content)
        if data.get("genre"): state["profile"].genre = data["genre"]
        if data.get("location"): state["profile"].location = data["location"]
        if data.get("budget"): state["profile"].budget = float(data["budget"])
    except: pass
    return state

def responder_node(state):
    p = state["profile"]
    context = "\n".join(state["results"])
    
    # Definizione Persona (Pag. 286): L'agente è un ORIENTATORE per FAN.
    system_persona = """
    Sei un ORIENTATORE MUSICALE per FAN e ASCOLTATORI. 
    Il tuo compito è consigliare CONCERTI, ALBUM e ARTISTI da scoprire.
    NON dare mai consigli su come pubblicizzare musica, come distribuirla o come fare marketing.
    L'utente vuole solo sapere cosa ascoltare e dove andare a ballare o sentire musica dal vivo.
    """
    
    prompt = f"""
    {system_persona}
    Dati i risultati della ricerca: {context}
    Consiglia all'utente (Fan di {p.genre} a {p.location}) cosa ascoltare o quali eventi vedere nel 2026.
    """
    res = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model=MODEL)
    state["final_response"] = res.choices[0].message.content
    return state

def reflection_node(state):
    # Nodo di controllo (Pag. 292): Verifica che non ci siano consigli di marketing
    prompt = f"""
    Analizza questa risposta: '{state['final_response']}'
    Se contiene consigli su 'come pubblicizzarsi', 'caricare musica' o 'carriera musicale', 
    riscrivila completamente focalizzandoti solo su consigli di ASCOLTO e CONCERTI nel 2026.
    """
    res = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model=MODEL)
    state["final_response"] = res.choices[0].message.content
    return state

def action_planner_node(state):
    prompt = f"Estrai UN evento (title, date, location) in JSON da: {state['final_response']}"
    try:
        res = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model=MODEL, response_format={"type": "json_object"})
        data = json.loads(res.choices[0].message.content)
        if data.get("title"): state["event_details"] = EventInfo(**data)
    except: state["event_details"] = None
    return state

def router(state):
    if state["profile"].genre or state["profile"].location: return "search"
    return "responder"

workflow = StateGraph(AgentState)
workflow.add_node("parser", parser_node)
workflow.add_node("search", search_music_events)
workflow.add_node("responder", responder_node)
workflow.add_node("reflection", reflection_node)
workflow.add_node("action_planner", action_planner_node)
workflow.set_entry_point("parser")
workflow.add_conditional_edges("parser", router, {"search": "search", "responder": "responder"})
workflow.add_edge("search", "responder")
workflow.add_edge("responder", "reflection")
workflow.add_edge("reflection", "action_planner")
workflow.add_edge("action_planner", END)
graph = workflow.compile()
