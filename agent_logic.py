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
    prompt = f"""
    Estrai in JSON (genre, artists, location, budget come numero) da: '{msg}'. 
    Se l'utente indica un budget, estrai solo il numero. Rispondi solo JSON.
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
    budget_info = f"Il budget dell'utente è di massimo {p.budget} Euro." if p.budget else "Non c'è limite di budget."
    
    prompt = f"""
    Sei un esperto orientatore musicale. 
    L'utente vuole {p.genre} a {p.location}. {budget_info}
    
    Basandoti su questi dati: {context}
    
    Pianifica la risposta:
    1. Se trovi prezzi, verifica che siano vicini al budget.
    2. Se non trovi prezzi esatti, avvisa l'utente ma dai comunque una stima.
    3. Sii molto chiaro su cosa può permettersi.
    """
    res = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model=MODEL)
    state["final_response"] = res.choices[0].message.content
    return state

def router(state):
    if state["profile"].genre or state["profile"].location:
        return "search"
    return "responder"

workflow = StateGraph(AgentState)
workflow.add_node("parser", parser_node)
workflow.add_node("search", search_music_events)
workflow.add_node("responder", responder_node)
workflow.set_entry_point("parser")
workflow.add_conditional_edges("parser", router, {"search": "search", "responder": "responder"})
workflow.add_edge("search", "responder")
workflow.add_edge("responder", END)
graph = workflow.compile()