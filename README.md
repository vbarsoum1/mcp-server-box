# MCP Server Box

## Description

MCP Server Box is a Python project that integrates with the Box API to perform various operations such as file search, text extraction, AI-based querying, and data extraction. It leverages the `box-sdk-gen` library and provides a set of tools to interact with Box files and folders.

The Model Context Protocol (MCP) is a framework designed to standardize the way models interact with various data sources and services. In this project, MCP is used to facilitate seamless integration with the Box API, enabling efficient and scalable operations on Box files and folders. The MCP Server Box project aims to provide a robust and flexible solution for managing and processing Box data using advanced AI and machine learning techniques.

## Requirements

- Python 3.13 or higher
- Box API credentials (Client ID, Client Secret, etc.)

## Installation

1. Clone the repository:

    ```sh
    git clone https://github.com/yourusername/mcp-server-box.git
    cd mcp-server-box
    ```

2. Create a virtual environment and activate it:

    ```sh
    python -m venv .venv
    source .venv/bin/activate
    ```

3. Install the dependencies:

    ```sh
    pip install -r requirements.txt
    ```

4. Create a `.env` file in the root directory and add your Box API credentials:

    ```.env
    BOX_CLIENT_ID=your_client_id
    BOX_CLIENT_SECRET=your_client_secret
    BOX_SUBJECT_TYPE=your_subject_type
    BOX_SUBJECT_ID=your_subject_id
    ```

## Usage

### Running the MCP Server

To start the MCP server, run the following command:

```sh
uv --directory /path-to-the-project/mcp-server-box run src/mcp_server_box.py
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
                "/path-to-your-project/mcp-server-box",
                "run",
                "src/mcp_server_box.py"
            ]
        }
    }
}
```

3. If CLaude is running restart it