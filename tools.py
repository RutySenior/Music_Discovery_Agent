from duckduckgo_search import DDGS

def search_music_events(state):
    p = state["profile"]
    # Creiamo una query flessibile (Huyen, Pag. 287)
    term = p.genre if p.genre else ""
    loc = f"a {p.location}" if p.location else ""
    query = f"concerti {term} {loc} 2026 tour date"
    
    print(f"Eseguo ricerca web per: {query}")
    try:
        with DDGS() as ddgs:
            results = [r['body'] for r in ddgs.text(query, max_results=3)]
        state["results"] = results
    except Exception as e:
        print(f"Errore ricerca: {e}")
        state["results"] = []
    return state