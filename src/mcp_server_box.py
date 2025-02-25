from box_api import (
    get_box_ccg_client,
    box_search,
    box_file_text_extract,
    box_file_ai_ask,
)
from mcp.server.fastmcp import FastMCP
import logging

# Initialize FastMCP server
mcp = FastMCP("Box Server")

# Set the logging level to INFO and sve it on a file
logging.basicConfig(
    level=logging.INFO,
    filename="/Users/rbarbosa/Documents/code/python/box/mcp-server-box/mcp_server.log",
)

logging.info("Box Server started")


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


@mcp.tool()
async def box_read_tool(file_id: any) -> str:
    """
    Read the text content of a file in Box.

    Args:
        file_id (str): The ID of the file to read.
    return:
        str: The text content of the file.
    """
    # log parameters and its type
    logging.info(f"file_id: {file_id}, type: {type(file_id)}")

    # check if file id isn't a string and convert to a string
    if not isinstance(file_id, str):
        file_id = str(file_id)

    # Get the Box client
    box_client = get_box_ccg_client()

    response = box_file_text_extract(box_client, file_id)

    return response


@mcp.tool()
async def box_ask_ai_tool(file_id: any, prompt: str) -> str:
    """
    Ask box ai about a file in Box.

    Args:
        file_id (str): The ID of the file to read.
        prompt (str): The prompt to ask the AI.
    return:
        str: The text content of the file.
    """
    # log parameters and its type
    logging.info(f"file_id: {file_id}, type: {type(file_id)}")

    # check if file id isn't a string and convert to a string
    if not isinstance(file_id, str):
        file_id = str(file_id)

    # Get the Box client
    box_client = get_box_ccg_client()

    response = box_file_ai_ask(box_client, file_id, prompt=prompt)

    return response


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport="stdio")
