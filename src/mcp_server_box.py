# from dataclasses import dataclass
import base64
import json
import logging

# from mcp.server import Server
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any, AsyncIterator, List, Union, cast  # , Optional, cast


from box_ai_agents_toolkit import (
    BoxClient,
    DocumentFiles,
    File,
    Folder,
    ImageFiles,
    SearchForContentContentTypes,
    box_claude_ai_agent_ask,
    box_claude_ai_agent_extract,
    box_create_folder,
    box_delete_folder,
    box_file_ai_ask,
    box_hubs_ai_ask,
    box_multi_file_ai_ask,
    box_file_ai_extract,
    box_file_download,
    box_file_text_extract,
    box_folder_list_content,
    box_locate_folder_by_name,
    box_search,
    box_update_folder,
    box_upload_file,
    authorize_app,
    get_oauth_client,
)

from mcp.server.fastmcp import Context, FastMCP

# # Disable all logging
logging.basicConfig(level=logging.CRITICAL)
for logger_name in logging.root.manager.loggerDict:
    logging.getLogger(logger_name).setLevel(logging.CRITICAL)

# Override the logging call that's visible in the original code
logger = logging.getLogger(__name__)
logger.setLevel(logging.CRITICAL)


@dataclass
class BoxContext:
    client: BoxClient = None


@asynccontextmanager
async def box_lifespan(server: FastMCP) -> AsyncIterator[BoxContext]:
    """Manage Box client lifecycle with OAuth handling"""
    try:
        client = get_oauth_client()
        yield BoxContext(client=client)
    # except Exception as e:
    #     pass
    #     # logger.error(f"Error: {e}")
    finally:
        # Cleanup (if needed)
        pass


# Initialize FastMCP server
mcp = FastMCP("Box MCP Server", lifespan=box_lifespan)
# mcp = Server("Box MCP Server", lifespan=box_lifespan)


@mcp.tool()
async def box_who_am_i(ctx: Context) -> str:
    """
    Get the current user's information.
    This is also useful to check the connection status.

    return:
        str: The current user's information.
    """
    # Get the Box client
    box_client: BoxClient = cast(
        BoxContext, ctx.request_context.lifespan_context
    ).client

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
    ctx: Context,
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
    box_client: BoxClient = cast(
        BoxContext, ctx.request_context.lifespan_context
    ).client

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
async def box_read_tool(ctx: Context, file_id: Any) -> str:
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
    box_client: BoxClient = cast(
        BoxContext, ctx.request_context.lifespan_context
    ).client

    response = box_file_text_extract(box_client, file_id)

    return response


@mcp.tool()
async def box_ask_ai_tool(ctx: Context, file_id: Any, prompt: str) -> str:
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
    box_client: BoxClient = cast(
        BoxContext, ctx.request_context.lifespan_context
    ).client
    ai_agent = box_claude_ai_agent_ask()
    response = box_file_ai_ask(box_client, file_id, prompt=prompt, ai_agent=ai_agent)

    return response


@mcp.tool()
async def box_ask_ai_tool_multi_file(
    ctx: Context, file_ids: List[str], prompt: str
) -> str:
    """
    Use Box AI to analyze and respond to a prompt based on the content of multiple files.

    This tool allows users to query Box AI with a specific prompt, leveraging the content
    of multiple files stored in Box. The AI processes the files and generates a response
    based on the provided prompt.

    Args:
        ctx (Context): The context object containing the request and lifespan context.
        file_ids (List[str]): A list of file IDs to be analyzed by the AI.
        prompt (str): The prompt or question to ask the AI.

    Returns:
        str: The AI-generated response based on the content of the specified files.

    Raises:
        Exception: If there is an issue with the Box client, AI agent, or file processing.
    """

    # Get the Box client
    box_client: BoxClient = cast(
        BoxContext, ctx.request_context.lifespan_context
    ).client
    ai_agent = box_claude_ai_agent_ask()
    response = box_multi_file_ai_ask(
        box_client, file_ids, prompt=prompt, ai_agent=ai_agent
    )

    return response

@mcp.tool()
async def box_hubs_ask_ai_tool(ctx: Context, hubs_id: Any, prompt: str) -> str:
    """
    Ask box ai about a hub in Box.

    Args:
        hubs_id (str): The ID of the hub to read.
        prompt (str): The prompt to ask the AI.
    return:
        str: The text content of the file.
    """
    # log parameters and its type
    logging.info(f"file_id: {hubs_id}, type: {type(hubs_id)}")

    # check if file id isn't a string and convert to a string
    if not isinstance(hubs_id, str):
        hubs_id = str(hubs_id)

    # Get the Box client
    box_client: BoxClient = cast(
        BoxContext, ctx.request_context.lifespan_context
    ).client
    ai_agent = box_claude_ai_agent_ask()
    response = box_hubs_ai_ask(box_client, hubs_id, prompt=prompt, ai_agent=ai_agent)

    return response


@mcp.tool()
async def box_search_folder_by_name(ctx: Context, folder_name: str) -> str:
    """
    Locate a folder in Box by its name.

    Args:
        folder_name (str): The name of the folder to locate.
    return:
        str: The folder ID.
    """

    # Get the Box client
    box_client: BoxClient = cast(
        BoxContext, ctx.request_context.lifespan_context
    ).client

    search_results = box_locate_folder_by_name(box_client, folder_name)

    # Return the "id", "name", "description" of the search results
    search_results = [f"{folder.name} (id:{folder.id})" for folder in search_results]

    return "\n".join(search_results)


@mcp.tool()
async def box_ai_extract_data(ctx: Context, file_id: Any, fields: str) -> str:
    """ "
    Extract data from a single file in Box using AI.

    Args:
        file_id (str): The ID of the file to read.
        fields (str): The fields to extract from the file.
    return:
        str: The extracted data in a json string format.
    """
    # Get the Box client
    box_client: BoxClient = cast(
        BoxContext, ctx.request_context.lifespan_context
    ).client

    # check if file id isn't a string and convert to a string
    if not isinstance(file_id, str):
        file_id = str(file_id)

    ai_agent = box_claude_ai_agent_extract()
    response = box_file_ai_extract(box_client, file_id, fields, ai_agent=ai_agent)

    return json.dumps(response)


@mcp.tool()
async def box_list_folder_content_by_folder_id(
    ctx: Context, folder_id: Any, is_recursive
) -> str:
    """
    List the content of a folder in Box by its ID.

    Args:
        folder_id (str): The ID of the folder to list the content of.
        is_recursive (bool): Whether to list the content recursively.

    return:
        str: The content of the folder in a json string format, including the "id", "name", "type", and "description".
    """
    # Get the Box client
    box_client: BoxClient = cast(
        BoxContext, ctx.request_context.lifespan_context
    ).client

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


@mcp.tool()
async def box_manage_folder_tool(
    ctx: Context,
    action: str,  # "create", "delete", or "update"
    folder_id: Any = None,  # Required for delete and update, not for create
    name: str = None,  # Required for create, optional for update
    parent_id: Any = None,  # Required for create, optional for update
    description: str = None,  # Optional for update
    recursive: bool = False,  # Optional for delete
) -> str:
    """
    Manage Box folders - create, delete, or update.

    Args:
        action (str): The action to perform: "create", "delete", or "update"
        folder_id (Any): The ID of the folder (required for delete and update)
        name (str): The name for the folder (required for create, optional for update)
        parent_id (Any): The ID of the parent folder (required for create, optional for update)
                       Root folder is "0" or 0.
        description (str): Description for the folder (optional for update)
        recursive (bool): Whether to delete recursively (optional for delete)

    return:
        str: Result of the operation
    """
    # Get the Box client
    box_client: BoxClient = cast(
        BoxContext, ctx.request_context.lifespan_context
    ).client

    # Validate and normalize inputs
    if action.lower() not in ["create", "delete", "update"]:
        return f"Invalid action: {action}. Must be one of: create, delete, update."

    action = action.lower()

    # Convert IDs to strings if needed
    if folder_id is not None and not isinstance(folder_id, str):
        folder_id = str(folder_id)

    if parent_id is not None and not isinstance(parent_id, str):
        parent_id = str(parent_id)

    # Handle create action
    if action == "create":
        if not name:
            return "Error: name is required for create action"

        try:
            # Default to root folder ("0") if parent_id is None
            parent_id_str = parent_id if parent_id is not None else "0"

            new_folder = box_create_folder(
                client=box_client, name=name, parent_id=parent_id_str
            )
            return f"Folder created successfully. Folder ID: {new_folder.id}, Name: {new_folder.name}"
        except Exception as e:
            return f"Error creating folder: {str(e)}"

    # Handle delete action
    elif action == "delete":
        if not folder_id:
            return "Error: folder_id is required for delete action"

        try:
            box_delete_folder(
                client=box_client, folder_id=folder_id, recursive=recursive
            )
            return f"Folder with ID {folder_id} deleted successfully"
        except Exception as e:
            return f"Error deleting folder: {str(e)}"

    # Handle update action
    elif action == "update":
        if not folder_id:
            return "Error: folder_id is required for update action"

        try:
            updated_folder = box_update_folder(
                client=box_client,
                folder_id=folder_id,
                name=name,
                description=description,
                parent_id=parent_id,
            )
            return f"Folder updated successfully. Folder ID: {updated_folder.id}, Name: {updated_folder.name}"
        except Exception as e:
            return f"Error updating folder: {str(e)}"


@mcp.tool()
async def box_upload_file_tool(
    ctx: Context, content: str, file_name: str, folder_id: Any | None = None
) -> str:
    """
    Upload content as a file to Box.

    Args:
        content (str): The content to upload as a file.
        file_name (str): The name to give the file in Box.
        folder_id (Any, optional): The ID of the folder to upload to. If not provided, uploads to root.

    return:
        str: The uploaded file's information including ID and name.
    """
    # Get the Box client
    box_client: BoxClient = cast(
        BoxContext, ctx.request_context.lifespan_context
    ).client

    try:
        # Convert folder_id to string if it's not None
        folder_id_str = str(folder_id) if folder_id is not None else None

        # Use the box_api function for uploading
        result = box_upload_file(
            client=box_client,
            content=content,
            file_name=file_name,
            folder_id=folder_id_str,
        )

        return f"File uploaded successfully. File ID: {result['id']}, Name: {result['name']}"
    except Exception as e:
        return f"Error uploading file: {str(e)}"


@mcp.tool()
async def box_download_file_tool(
    ctx: Context, file_id: Any, save_file: bool = False, save_path: str | None = None
) -> str:
    """
    Download a file from Box and return its content as a string.
    Supports text files (returns content directly) and images (returns base64-encoded).
    Other file types will return an error message.
    Optionally saves the file locally.

    Args:
        file_id (Any): The ID of the file to download.
        save_file (bool, optional): Whether to save the file locally. Defaults to False.
        save_path (str, optional): Path where to save the file. If not provided but save_file is True,
                                  uses a temporary directory. Defaults to None.

    return:
        str: For text files: content as string.
             For images: base64-encoded string with metadata.
             For unsupported files: error message.
             If save_file is True, includes the path where the file was saved.
    """
    # Get the Box client
    box_client: BoxClient = cast(
        BoxContext, ctx.request_context.lifespan_context
    ).client

    # Convert file_id to string if it's not already
    if not isinstance(file_id, str):
        file_id = str(file_id)

    try:
        # Use the box_api function for downloading
        saved_path, file_content, mime_type = box_file_download(
            client=box_client, file_id=file_id, save_file=save_file, save_path=save_path
        )

        # Get file info to include name in response
        file_info = box_client.files.get_file_by_id(file_id)
        file_name = file_info.name
        file_extension = file_name.split(".")[-1].lower() if "." in file_name else ""

        # Prepare response based on content type
        response = ""
        if saved_path:
            response += f"File saved to: {saved_path}\n\n"

        # Check if file is a document (text-based file)
        is_document = (
            mime_type
            and mime_type.startswith("text/")
            or file_extension in [e.value for e in DocumentFiles]
        )

        # Check if file is an image
        is_image = (
            mime_type
            and mime_type.startswith("image/")
            or file_extension in [e.value for e in ImageFiles]
        )

        if is_document:
            # Text file - return content directly
            try:
                content_text = file_content.decode("utf-8")
                response += (
                    f"File downloaded successfully: {file_name}\n\n{content_text}"
                )
            except UnicodeDecodeError:
                # Handle case where file can't be decoded as UTF-8 despite being a "document"
                response += f"File {file_name} is a document but couldn't be decoded as text. It may be in a binary format."

        elif is_image:
            # Image file - return base64 encoded
            base64_data = base64.b64encode(file_content).decode("utf-8")
            response += f"Image downloaded successfully: {file_name}\nMIME type: {mime_type}\nBase64 encoded data:\n{base64_data}"

        else:
            # Unsupported file type for content display (but still saved if requested)
            if not saved_path:
                response += f"File {file_name} has unsupported type ({mime_type or 'unknown'}). Only text and image files are supported for content display."
            else:
                response += f"File {file_name} has unsupported type ({mime_type or 'unknown'}) for content display, but was saved successfully."

        return response

    except Exception as e:
        return f"Error downloading file: {str(e)}"


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport="stdio")
