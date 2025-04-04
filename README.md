# MCP Server Box

## Description

MCP Server Box is a Python project that integrates with the Box API to perform various operations such as file search, text extraction, AI-based querying, and data extraction. It leverages the `box-sdk-gen` library and provides a set of tools to interact with Box files and folders.

The Model Context Protocol (MCP) is a framework designed to standardize the way models interact with various data sources and services. In this project, MCP is used to facilitate seamless integration with the Box API, enabling efficient and scalable operations on Box files and folders. The MCP Server Box project aims to provide a robust and flexible solution for managing and processing Box data using advanced AI and machine learning techniques.

## Tools implemented

## Box Tools

### `box_who_am_i`
Get your current user information and check connection status.

**Returns:** User information string

### `box_authorize_app_tool`
Start the Box application authorization process.

**Returns:** Authorization status message

### `box_search_tool`
Search for files in Box.

**Parameters:**
- `query` (str): Search query
- `file_extensions` (List[str], optional): File extensions to filter by
- `where_to_look_for_query` (List[str], optional): Where to search (NAME, DESCRIPTION, FILE_CONTENT, COMMENTS, TAG)
- `ancestor_folder_ids` (List[str], optional): Folder IDs to search within

**Returns:** Search results

### `box_read_tool`
Read the text content of a Box file.

**Parameters:**
- `file_id` (str): ID of the file to read

**Returns:** File content

### `box_ask_ai_tool`
Ask Box AI about a file.

**Parameters:**
- `file_id` (str): ID of the file
- `prompt` (str): Question for the AI

**Returns:** AI response

### `box_search_folder_by_name`
Locate a folder by name.

**Parameters:**
- `folder_name` (str): Name of the folder

**Returns:** Folder ID

### `box_ai_extract_data`
Extract data from a file using AI.

**Parameters:**
- `file_id` (str): ID of the file
- `fields` (str): Fields to extract

**Returns:** Extracted data in JSON format

### `box_list_folder_content_by_folder_id`
List folder contents.

**Parameters:**
- `folder_id` (str): ID of the folder
- `is_recursive` (bool): Whether to list recursively

**Returns:** Folder content in JSON format with id, name, type, and description

### `box_manage_folder_tool`
Create, update, or delete folders in Box.

**Parameters:**
- `action` (str): Action to perform: "create", "delete", or "update"
- `folder_id` (str, optional): ID of the folder (required for delete/update)
- `name` (str, optional): Folder name (required for create, optional for update)
- `parent_id` (str, optional): Parent folder ID (required for create, optional for update)
- `description` (str, optional): Folder description (optional for update)
- `recursive` (bool, optional): Whether to delete recursively (optional for delete)

**Returns:** Status message with folder details

### `box_upload_file_tool`
Upload content as a file to Box.

**Parameters:**
- `content` (str): The content to upload as a file
- `file_name` (str): The name to give the file in Box
- `folder_id` (Any, optional): The ID of the folder to upload to

**Returns:** Upload status with file ID and name

### `box_download_file_tool`
Download a file from Box and return its content.

**Parameters:**
- `file_id` (Any): The ID of the file to download
- `save_file` (bool, optional): Whether to save the file locally
- `save_path` (str, optional): Path where to save the file

**Returns:** File content as text, base64-encoded image, or save status message

## Requirements

- Python 3.13 or higher
- Box API credentials (Client ID, Client Secret, etc.)

## Installation

1. Clone the repository:

    ```sh
    git clone https://github.com/box-community/mcp-server-box.git
    cd mcp-server-box
    ```

2. Install `uv` if not installed yet:

    2.1 MacOS+Linux

    ```sh MacOS+Linux
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

    2.2 Windows

    ```powershell Windows
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    ```
    
3. Create and set up our project:

    3.1 MacOS+Linux

    ```sh
    # Create virtual environment and activate it
    uv venv
    source .venv/bin/activate

    # Lock the dependencies
    uv lock
    ```

    3.1 Windows

    ```sh
    # Create virtual environment and activate it
    uv venv
    .venv\Scripts\activate

    # Lock the dependencies
    uv lock
    ```


4. Create a `.env` file in the root directory and add your Box API credentials:

    ```.env
    BOX_CLIENT_ID=your_client_id
    BOX_CLIENT_SECRET=your_client_secret
    ```

## Usage

### Running the MCP Server

To start the MCP server, run the following command:

```sh
uv --directory /Users/anovotny/Desktop/mcp-server-box run src/mcp_server_box.py
```

### Using Claude as the client

1. Edit your `claude_desktop_config`.json

```sh
code ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

2. And add the following:
```json
{
    "mcpServers": {
        "mcp-server-box": {
            "command": "uv",
            "args": [
                "--directory",
                "/Users/anovotny/Desktop/mcp-server-box",
                "run",
                "src/mcp_server_box.py"
            ]
        }
    }
}
```

3. If CLaude is running restart it
```

## Running Tests

The project includes a suite of tests to verify Box API functionality. Before running the tests, you'll need to update the file and folder IDs in the test files to match files in your Box account.

### Setting Up Tests

1. **Update File and Folder IDs**: 
   - Each test file (in the `tests/` directory) contains hardcoded IDs for Box files and folders
   - You need to replace these IDs with IDs of files and folders in your Box account
   - Example: In `test_box_api_read.py`, replace `"1728677291168"` with the ID of a file in your Box account

2. **Test File ID References**:
   - `test_box_api_read.py`: Needs a valid document file ID (e.g., a Word document)
   - `test_box_api_search.py`: Update the search queries and file extensions to match your content
   - `test_box_api_ai.py`: Needs a file ID for testing AI extraction capabilities
   - Other test files may require specific folder IDs or file types

### Running Tests

Once you've updated the file IDs, you can run tests using pytest:

```bash
# Run all tests
pytest

# Run a specific test file
pytest tests/test_box_api_file_ops.py

# Run tests with detailed output
pytest -v

# Run tests and show print statements
pytest -v -s
```

### Available Tests

- `test_box_auth.py`: Tests authentication functionality
- `test_box_api_basic.py`: Basic Box API tests
- `test_box_api_read.py`: Tests file reading capabilities
- `test_box_api_search.py`: Tests search functionality
- `test_box_api_ai.py`: Tests AI-based features
- `test_box_api_file_ops.py`: Tests file upload and download operations

### Creating New Tests

When creating new tests:
1. Follow the pattern in existing test files
2. Use the `box_client` fixture for authenticated API access
3. Clean up any test files or folders created during tests
4. Add proper assertions to verify functionality

## Troubleshooting