"""Wiki-search tool wrappers for MCP integration with proper type hints."""
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from typing import List, Union, Tuple, Dict
from wiki_search import (
    search_wikipedia, get_wikipedia_content, clean_page_html,
    get_page_sections, get_section_content, get_multiple_sections_content
)

load_dotenv()

# Create a MCP server instance
mcp = FastMCP(
    name = "Wiki-Search-Server",	
    description = "A server for searching and retrieving Wikipedia articles and sections.",	
    host = "0.0.0.0",
    port = 8051,
)

@mcp.tool()
def search_wikipedia_tool(query: str) -> List[Dict[str, Union[str, int]]]:
    """Search Wikipedia for a query and return relevant article titles and snippets.
    
    Args:
        query: Search query string
    
    Returns:
        List of dictionaries with article info (title, pageid, snippet)
    """
    return search_wikipedia(query)

@mcp.tool()
def get_wikipedia_content_tool(page_id: int) -> str:
    """Retrieve the full content of a Wikipedia article by page ID.
    
    Args:
        page_id: Wikipedia page ID
    
    Returns:
        Article content as cleaned text
    """
    return get_wikipedia_content(page_id)

@mcp.tool()
def get_page_sections_tool(page_id: int) -> Tuple[List[str], Dict[str, str]]:
    """Get the list of section titles and their indices for a Wikipedia page.
    
    Args:
        page_id: Wikipedia page ID
    
    Returns:
        Tuple of (section titles list, section index dictionary)
    """
    return get_page_sections(page_id)

@mcp.tool()
def get_section_content_tool(page_id: int, section_index: str) -> str:
    """Get the content of a specific section from a Wikipedia page.
    
    Args:
        page_id: Wikipedia page ID
        section_index: Section index string
    
    Returns:
        Section content as cleaned text
    """
    return get_section_content(page_id, section_index)

@mcp.tool()
def clean_page_html_tool(html_content: str) -> str:
    """Clean Wikipedia HTML content to extract readable text.
    
    Args:
        html_content: HTML content to clean
    
    Returns:
        Cleaned text content
    """
    return clean_page_html(html_content)

@mcp.tool()
def get_multiple_sections_content_tool(page_id: int, section_indices: List[str]) -> Dict[str, str]:
    """Get content from multiple sections of a Wikipedia page in a single call.
    
    Args:
        page_id: Wikipedia page ID
        section_indices: List of section indices to retrieve
        
    Returns:
        Dictionary mapping section indices to their content
    """
    return get_multiple_sections_content(page_id, section_indices)

# to run the server --> mcp dev server_wiki_search.py 
if __name__ == "__main__":
    transport = "stdio"
    # stdio for basic input/output streams on the same machine
    if transport == "stdio":
        print("Running in stdio mode")
        mcp.run(transport= "stdio")
    # remote connection across networks
    elif transport == "sse":
        print("Running in sse mode")
        mcp.run(transport= "sse")
    else:
        raise ValueError("Invalid transport mode. Use 'stdio' or 'sse'.")