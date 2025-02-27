# from dataclasses import dataclass
from typing import Any, List, Union  # , Optional, cast
from lib.box_api import (
    box_search,
    box_file_text_extract,
    box_file_ai_ask,
    box_locate_folder_by_name,
    box_file_ai_extract,
    box_folder_list_content,
)
from lib.box_authentication import get_oauth_client, authorize_app
from mcp.server.fastmcp import FastMCP  # , Context
import logging
from box_sdk_gen import SearchForContentContentTypes, File, Folder
import json
# from contextlib import asynccontextmanager
# from dataclasses import dataclass


# Initialize FastMCP server
mcp = FastMCP("Box Server")

logger = logging.getLogger(__name__)
logger.info("Box MCP Server started")


# @dataclass
# class BoxContext:
#     client: Optional[BoxClient] = None
#     # auth: Optional[BoxOAuth] = None


# @asynccontextmanager
# async def box_lifespan(server: FastMCP):
#     """Manage Box client lifecycle with OAuth handling"""
#     try:
#         client = get_oauth_client()

#         # Test authentication (will auto-refresh if needed)
#         try:
#             current_user = client.users.get_user_me()
#             logger.info(f"Authenticated as: {current_user.name}")
#         except Exception as e:
#             logger.warning(f"Authentication failed: {str(e)}")
#             logger.info("You'll need to authenticate using the get_auth_url tool")

#         yield BoxContext(client=client)

#     finally:
#         # Cleanup (if needed)
#         pass


@mcp.tool()
async def box_who_am_i() -> str:
    """
    Get the current user's information.
    This is also useful to check the connection status.

    return:
        str: The current user's information.
    """
    # Get the Box client
    box_client = get_oauth_client()
    # Get the current user's information
    current_user = box_client.users.get_user_me()

    return f"Authenticated as: {current_user.name}"


@mcp.tool()
async def box_authorize_app_tool() -> str:
    """
    Authorize the Box application.
    Start the Box app authorization process

    return:
        str: Message
    """
    logger.info("Authorizing Box application")
    result = authorize_app()
    if result:
        return "Box application authorized successfully"
    else:
        return "Box application not authorized"


@mcp.tool()
async def box_search_tool(
    query: str,
    file_extensions: List[str] | None = None,
    where_to_look_for_query: List[str] | None = None,
    ancestor_folder_ids: List[str] | None = None,
) -> str:
    """
    Search for files in Box with the given query.

    Args:
        query (str): The query to search for.
        file_extensions (List[str]): The file extensions to search for, for example *.pdf
        content_types (List[SearchForContentContentTypes]): where to look for the information, possible values are:
            NAME
            DESCRIPTION,
            FILE_CONTENT,
            COMMENTS,
            TAG,
        ancestor_folder_ids (List[str]): The ancestor folder IDs to search in.
    return:
        str: The search results.
    """
    # Get the Box client
    box_client = get_oauth_client()

    # Convert the where to look for query to content types
    content_types: List[SearchForContentContentTypes] = []
    if where_to_look_for_query:
        for content_type in where_to_look_for_query:
            content_types.append(SearchForContentContentTypes[content_type])

    # Search for files with the query
    search_results = box_search(
        box_client, query, file_extensions, content_types, ancestor_folder_ids
    )

    # Return the "id", "name", "description" of the search results
    search_results = [
        f"{file.name} (id:{file.id})"
        + (f" {file.description}" if file.description else "")
        for file in search_results
    ]

    return "\n".join(search_results)


@mcp.tool()
async def box_read_tool(file_id: Any) -> str:
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
    box_client = get_oauth_client()

    response = box_file_text_extract(box_client, file_id)

    return response


@mcp.tool()
async def box_ask_ai_tool(file_id: Any, prompt: str) -> str:
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
    box_client = get_oauth_client()

    response = box_file_ai_ask(box_client, file_id, prompt=prompt)

    return response


@mcp.tool()
async def box_search_folder_by_name(folder_name: str) -> str:
    """
    Locate a folder in Box by its name.

    Args:
        folder_name (str): The name of the folder to locate.
    return:
        str: The folder ID.
    """

    # Get the Box client
    box_client = get_oauth_client()

    search_results = box_locate_folder_by_name(box_client, folder_name)

    # Return the "id", "name", "description" of the search results
    search_results = [f"{folder.name} (id:{folder.id})" for folder in search_results]

    return "\n".join(search_results)


@mcp.tool()
async def box_ai_extract_data(file_id: Any, fields: str) -> str:
    """ "
    Extract data from a file in Box using AI.

    Args:
        file_id (str): The ID of the file to read.
        fields (str): The fields to extract from the file.
    return:
        str: The extracted data in a json string format.
    """
    # Get the Box client
    box_client = get_oauth_client()

    # check if file id isn't a string and convert to a string
    if not isinstance(file_id, str):
        file_id = str(file_id)

    response = box_file_ai_extract(box_client, file_id, fields)

    return json.dumps(response)


@mcp.tool()
async def box_list_folder_content_by_folder_id(folder_id: Any, is_recursive) -> str:
    """
    List the content of a folder in Box by its ID.

    Args:
        folder_id (str): The ID of the folder to list the content of.
        is_recursive (bool): Whether to list the content recursively.

    return:
        str: The content of the folder in a json string format, including the "id", "name", "type", and "description".
    """
    # Get the Box client
    box_client = get_oauth_client()

    # check if file id isn't a string and convert to a string
    if not isinstance(folder_id, str):
        folder_id = str(folder_id)

    response: List[Union[File, Folder]] = box_folder_list_content(
        box_client, folder_id, is_recursive
    )

    # Convert the response to a json string

    response = [
        {
            "id": item.id,
            "name": item.name,
            "type": item.type,
            "description": item.description if hasattr(item, "description") else None,
        }
        for item in response
    ]
    return json.dumps(response)


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport="stdio")
