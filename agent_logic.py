import os
import json
from groq import Groq
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from state import AgentState, MusicProfile
from tools import search_music_events

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.3-70b-versatile"

def parser_node(state):
    msg = state["messages"][-1]
    prompt = f"Estrai in JSON (genre, artists, location) da: '{msg}'. Rispondi solo JSON."
    try:
        res = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=MODEL,
            response_format={"type": "json_object"}
        )
        data = json.loads(res.choices[0].message.content)
        if data.get("genre"): state["profile"].genre = data["genre"]
        if data.get("location"): state["profile"].location = data["location"]
    except: pass
    return state

# NUOVO NODO: GENERATOR (Huyen, Pag. 256)
def responder_node(state):
    p = state["profile"]
    context = "\n".join(state["results"])
    
    prompt = f"""
    Sei un esperto orientatore musicale. 
    L'utente ama il genere {p.genre} e si trova a {p.location}.
    Basandoti su questi risultati di ricerca (spesso frammentari):
    {context}
    
    Scrivi una risposta amichevole e sensata. Consiglia album o artisti e 
    cita i concerti trovati se sono pertinenti. Se i risultati sono confusi, 
    usa la tua conoscenza generale per dare comunque un buon consiglio.
    """
    
    res = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model=MODEL
    )
    state["final_response"] = res.choices[0].message.content
    return state

def router(state):
    if state["profile"].genre or state["profile"].location:
        return "search"
    return "responder"

workflow = StateGraph(AgentState)
workflow.add_node("parser", parser_node)
workflow.add_node("search", search_music_events)
workflow.add_node("responder", responder_node) # Aggiungiamo il generatore

workflow.set_entry_point("parser")
workflow.add_conditional_edges("parser", router, {"search": "search", "responder": "responder"})
workflow.add_edge("search", "responder") # Dopo la ricerca, elabora la risposta
workflow.add_edge("responder", END)
graph = workflow.compile()