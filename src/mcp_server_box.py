from typing import List
from box_api import get_box_ccg_client, box_search
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("weather")


@mcp.tool()
async def box_search_tool(query: str) -> str:
    """
    Search for files in Box with the given query.

    Args:
        query (str): The query to search for.
    return:
        List[str]: The search results.
    """
    # Get the Box client
    box_client = get_box_ccg_client()

    # Search for files with the query
    search_results = box_search(box_client, query)

    # Return the "id", "name", "description" of the search results
    search_results = [
        f"{file.name} (id:{file.id})"
        + (f" {file.description}" if file.description else "")
        for file in search_results
    ]

    return "\n".join(search_results)


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport="stdio")
