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
        clean_snippet = clean_page_html(result["snippet"])
        search_summaries.append({
            "title": result["title"],
            "pageid": result["pageid"],
            "snippet": clean_snippet,
        })

    return search_summaries

def get_page_sections(pageid):
    """Fetch the sections of a Wikipedia page."""
    params = {
        "action": "parse",
        "pageid": pageid,
        "prop": "sections",
        "format": "json"
    }
    response = requests.get(WIKI_API_URL, params=params)
    data = response.json()

    sections = data.get("parse", {}).get("sections", [])
    section_titles = [section["line"] for section in sections]
    section_index = {section["line"]: section["index"] for section in sections}
    return section_titles, section_index

def get_section_content(pageid, section_index):
    """Fetch a specific section of a Wikipedia page."""
    params = {
        "action": "parse",
        "pageid": pageid,
        "section": section_index,
        "prop": "text",
        "format": "json"
    }
    response = requests.get(WIKI_API_URL, params=params)
    data = response.json()

    # Extract content from HTML and clean it
    try:
        html_content = data["parse"]["text"]["*"]
        # Clean the HTML to extract readable text
        cleaned_content = clean_page_html(html_content)
        return cleaned_content
    except KeyError:
        return "Content could not be retrieved."

def get_wikipedia_content(pageid):
    """Fetch the full content of the selected Wikipedia page and return it as cleaned text."""
    params = {
        "action": "parse",
        "pageid": pageid,
        "prop": "text",
        "format": "json"
    }
    response = requests.get(WIKI_API_URL, params=params)
    data = response.json()

    # Extract content from HTML and clean it
    try:
        html_content = data["parse"]["text"]["*"]
        # Clean the HTML to extract readable text
        cleaned_content = clean_page_html(html_content)
        return cleaned_content
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

def get_multiple_sections_content(pageid, section_indices):
    """Fetch multiple sections of a Wikipedia page in one batch to reduce API calls.
    
    Args:
        pageid (int): The Wikipedia page ID
        section_indices (list[str]): List of section indices to retrieve as strings
    
    Returns:
        dict: Dictionary mapping section indices to their cleaned content
    """
    sections_content = {}
    
    if not section_indices:
        return {"error": "No section indices provided"}
        
    # Convert pageid to integer if it's not already
    try:
        pageid = int(pageid)
    except (ValueError, TypeError):
        return {"error": f"Invalid page ID: {pageid}. Must be an integer."}
    
    for section_index in section_indices:
        # We still need to make multiple API calls, but we're batching them
        # in a single function call from the agent's perspective
        params = {
            "action": "parse",
            "pageid": pageid,
            "section": section_index,
            "prop": "text",
            "format": "json"
        }
        response = requests.get(WIKI_API_URL, params=params)
        data = response.json()
        
        try:
            html_content = data["parse"]["text"]["*"]
            cleaned_content = clean_page_html(html_content)
            sections_content[section_index] = cleaned_content
        except KeyError:
            sections_content[section_index] = f"Content could not be retrieved for section {section_index}."
    
    return sections_content

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
