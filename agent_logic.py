import os
import json
from groq import Groq
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from state import AgentState, MusicProfile, EventInfo
from tools import search_music_events

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.3-70b-versatile"

def parser_node(state):
    msg = state["messages"][-1]
    prompt = f"Estrai in JSON (genre, artists, location, budget) da: '{msg}'. Rispondi solo JSON."
    try:
        res = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model=MODEL, response_format={"type": "json_object"})
        data = json.loads(res.choices[0].message.content)
        if data.get("genre"): state["profile"].genre = data["genre"]
        if data.get("location"): state["profile"].location = data["location"]
        if data.get("budget"): state["profile"].budget = float(data["budget"])
    except: pass
    return state

def responder_node(state):
    p = state["profile"]
    context = "\n".join(state["results"])
    prompt = f"Sei un orientatore musicale. Basandoti su: {context}, consiglia all'utente ({p.genre} a {p.location}) cosa fare nel 2026. Sii specifico su nomi e date."
    res = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model=MODEL)
    state["final_response"] = res.choices[0].message.content
    return state

def reflection_node(state):
    res = client.chat.completions.create(messages=[{"role": "user", "content": f"Siamo nel 2026. Correggi date vecchie in: {state['final_response']}"}], model=MODEL)
    state["final_response"] = res.choices[0].message.content
    return state

def action_planner_node(state):
    prompt = f"Estrai UN evento da creare in calendario (JSON: title, date YYYY-MM-DD, location) da: {state['final_response']}. Se non ci sono eventi chiari, rispondi con JSON vuoto."
    try:
        res = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model=MODEL, response_format={"type": "json_object"})
        data = json.loads(res.choices[0].message.content)
        if data.get("title"):
            state["event_details"] = EventInfo(**data)
        else:
            state["event_details"] = None
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