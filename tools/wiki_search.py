import requests
import re
from bs4 import BeautifulSoup


WIKI_API_URL = "https://en.wikipedia.org/w/api.php"

def search_wikipedia(query, limit=5):
    """Step 1: Search Wikipedia for pages related to the query."""
    params = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "format": "json",
    }
    response = requests.get(WIKI_API_URL, params=params)
    data = response.json()

    results = data.get("query", {}).get("search", [])
    search_summaries = []

    for result in results[:limit]:
        clean_snippet = clean_html(result["snippet"])
        search_summaries.append({
            "title": result["title"],
            "pageid": result["pageid"],
            "snippet": clean_snippet,
        })

    return search_summaries

def clean_html(raw_html):
    """Remove all HTML tags like <span>, <b>, etc."""
    clean_text = re.sub(r"<.*?>", "", raw_html)
    return clean_text

def get_wikipedia_content(pageid):
    """Step 3-4: Fetch the full content of the selected Wikipedia page."""
    params = {
        "action": "parse",
        "pageid": pageid,
        "prop": "text",
        "format": "json"
    }
    response = requests.get(WIKI_API_URL, params=params)
    data = response.json()

    # Extract plain text from HTML (simplified for now)
    try:
        html_content = data["parse"]["text"]["*"]
        return html_content
    except KeyError:
        return "Content could not be retrieved."

def clean_page_html(html):
    soup = BeautifulSoup(html, "html.parser")

    # Remove scripts, styles, tables (infoboxes, navboxes), references
    for tag in soup(["script", "style", "table", "sup", "span"]):
        tag.decompose()

    # Optional: remove elements by class or id (e.g., navigation, references)
    for div in soup.find_all("div", {"class": ["reflist", "navbox", "infobox", "toc", "metadata"]}):
        div.decompose()

    # Keep only content from <p>, <h1-h6>, <li>
    content_tags = soup.find_all(["p", "h1", "h2", "h3", "h4", "h5", "h6", "li"])
    cleaned_text = "\n".join(tag.get_text(separator=" ", strip=True) for tag in content_tags if tag.get_text(strip=True))


    return cleaned_text

## Exmple usage:
# Uncomment the following lines to run the example usage
# if __name__ == "__main__":
#     query = "quantum entanglement"

#     # Step 1
#     search_results = search_wikipedia(query)
#     print("Search Results:")
#     for res in search_results:
#         print(f"- {res['title']} (pageid={res['pageid']})\n  → {res['snippet']}")

#    # Step 2: (Pretend agent picks one)
#     chosen_pageid = search_results[0]['pageid']
 
#     content_html = get_wikipedia_content(chosen_pageid)
#     clean_content_html = clean_page_html(content_html)
#     #print("\nRaw Wikipedia Page HTML:\n", content_html[:1000])
#     print("\nFull Wikipedia Page Content:\n", clean_content_html)
