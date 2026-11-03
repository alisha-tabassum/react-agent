from ddgs import DDGS

def search_web(query, max_results=3):
    results = []
    with DDGS() as ddgs:
        for r in ddgs.text(query, max_results=max_results):
            results.append({
                "title": r["title"],
                "snippet": r["body"],
                "link": r["href"]
            })
    return results

# Quick test
if __name__ == "__main__":
    query = "latest iPhone model 2026"
    print(f"Searching for: {query}\n")
    results = search_web(query)
    print(f"Got {len(results)} results\n")
    for i, r in enumerate(results, 1):
        print(f"{i}. {r['title']}")
        print(f"   {r['snippet'][:150]}...")
        print(f"   {r['link']}\n")

  
        