from duckduckgo_search import DDGS

def search_music_events(state):
    p = state["profile"]
    genre_term = p.genre if p.genre else "musica"
    loc_term = f"a {p.location}" if p.location else ""
    
    # Integrazione Budget nella ricerca (Huyen, Pag. 287)
    budget_term = f"biglietti economici sotto {p.budget} euro" if p.budget else "prezzi biglietti"
    
    query = f"concerti {genre_term} {loc_term} 2026 {budget_term} date tour"
    
    print(f"--- RICERCA BUDGET: {query} ---")
    try:
        with DDGS() as ddgs:
            results = [r['body'] for r in ddgs.text(query, max_results=3)]
        state["results"] = results
    except:
        state["results"] = []
    return state