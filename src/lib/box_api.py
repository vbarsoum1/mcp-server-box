# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import json
import logging
import dotenv
import os
import tempfile
import base64
import mimetypes
from dataclasses import dataclass
from typing import Iterable, List, Union, Dict, Optional, Any, Tuple
from enum import Enum

import requests
from box_sdk_gen import (
    AiExtractResponse,
    AiItemBase,
    AiItemBaseTypeField,
    BoxCCGAuth,
    BoxClient,
    BoxSDKError,
    CCGConfig,
    CreateAiAskMode,
    CreateAiExtractStructuredFields,
    CreateAiExtractStructuredFieldsOptionsField,
    File,
    Folder,
    FolderMini,
    SearchForContentContentTypes,
    SearchForContentType,
    ByteStream,
    AiSingleAgentResponseFull,
    AiAgentAsk,
    AiAgentAskTypeField,
    AiAgentLongTextTool,
    AiAgentBasicTextTool,
    AiAgentExtract,
    AiAgentExtractTypeField,
    CreateFolderParent,
    UpdateFolderByIdParent,
    FolderFull,
    UploadFileAttributes,
    UploadFileAttributesParentField,
)


logger = logging.getLogger(__name__)


class DocumentFiles(Enum):
    """DocumentFiles(Enum).

    An enum containing all of the supported extensions for files
    Box considers Documents. These files should have text
    representations.
    """

    DOC = "doc"
    DOCX = "docx"
    GDOC = "gdoc"
    GSHEET = "gsheet"
    NUMBERS = "numbers"
    ODS = "ods"
    ODT = "odt"
    PAGES = "pages"
    PDF = "pdf"
    RTF = "rtf"
    WPD = "wpd"
    XLS = "xls"
    XLSM = "xlsm"
    XLSX = "xlsx"
    AS = "as"
    AS3 = "as3"
    ASM = "asm"
    BAT = "bat"
    C = "c"
    CC = "cc"
    CMAKE = "cmake"
    CPP = "cpp"
    CS = "cs"
    CSS = "css"
    CSV = "csv"
    CXX = "cxx"
    DIFF = "diff"
    ERB = "erb"
    GROOVY = "groovy"
    H = "h"
    HAML = "haml"
    HH = "hh"
    HTM = "htm"
    HTML = "html"
    JAVA = "java"
    JS = "js"
    JSON = "json"
    LESS = "less"
    LOG = "log"
    M = "m"
    MAKE = "make"
    MD = "md"
    ML = "ml"
    MM = "mm"
    MSG = "msg"
    PHP = "php"
    PL = "pl"
    PROPERTIES = "properties"
    PY = "py"
    RB = "rb"
    RST = "rst"
    SASS = "sass"
    SCALA = "scala"
    SCM = "scm"
    SCRIPT = "script"
    SH = "sh"
    SML = "sml"
    SQL = "sql"
    TXT = "txt"
    VI = "vi"
    VIM = "vim"
    WEBDOC = "webdoc"
    XHTML = "xhtml"
    XLSB = "xlsb"
    XML = "xml"
    XSD = "xsd"
    XSL = "xsl"
    YAML = "yaml"
    GSLLIDE = "gslide"
    GSLIDES = "gslides"
    KEY = "key"
    ODP = "odp"
    PPT = "ppt"
    PPTX = "pptx"
    BOXNOTE = "boxnote"


class ImageFiles(Enum):
    """ImageFiles(Enum).

    An enum containing all of the supported extensions for files
    Box considers images.
    """

    ARW = "arw"
    BMP = "bmp"
    CR2 = "cr2"
    DCM = "dcm"
    DICM = "dicm"
    DICOM = "dicom"
    DNG = "dng"
    EPS = "eps"
    EXR = "exr"
    GIF = "gif"
    HEIC = "heic"
    INDD = "indd"
    INDML = "indml"
    INDT = "indt"
    INX = "inx"
    JPEG = "jpeg"
    JPG = "jpg"
    NEF = "nef"
    PNG = "png"
    SVG = "svg"
    TIF = "tif"
    TIFF = "tiff"
    TGA = "tga"
    SVS = "svs"


@dataclass
class BoxFileExtended:
    file: File
    text_representation: str


def _do_request(box_client: BoxClient, url: str):
    """
    Performs a GET request to a Box API endpoint using the provided Box client.

    This is an internal helper function and should not be called directly.

    Args:
        box_client (BoxClient): An authenticated Box client object.
        url (str): The URL of the Box API endpoint to make the request to.

    Returns:
        bytes: The content of the response from the Box API.

    Raises:
        BoxSDKError: If an error occurs while retrieving the access token.
        requests.exceptions.RequestException: If the request fails (e.g., network error,
                                             4XX or 5XX status code).
    """
    try:
        access_token = box_client.auth.retrieve_token().access_token
    except BoxSDKError as e:
        raise e

    resp = requests.get(url, headers={"Authorization": f"Bearer {access_token}"})
    resp.raise_for_status()
    return resp.content


def box_file_get_by_id(client: BoxClient, file_id: str) -> File:
    return client.files.get_file_by_id(file_id=file_id)


def box_file_text_extract(client: BoxClient, file_id: str) -> str:
    # Request the file with the "extracted_text" representation hint
    file_text_representation = client.files.get_file_by_id(
        file_id,
        x_rep_hints="[extracted_text]",
        fields=["name", "representations"],
    )
    # Check if any representations exist
    if not file_text_representation.representations.entries:
        logger.debug(f"No representation for file {file_text_representation.id}")
        return ""

    # Find the "extracted_text" representation
    extracted_text_entry = next(
        (
            entry
            for entry in file_text_representation.representations.entries
            if entry.representation == "extracted_text"
        ),
        None,
    )
    if not extracted_text_entry:
        return ""

    # Handle cases where the extracted text needs generation
    if extracted_text_entry.status.state == "none":
        _do_request(extracted_text_entry.info.url)  # Trigger text generation

    # Construct the download URL and sanitize filename
    url = extracted_text_entry.content.url_template.replace("{+asset_path}", "")

    # Download and truncate the raw content
    raw_content = _do_request(client, url)

    # check to see if rawcontent is bytes
    if isinstance(raw_content, bytes):
        return raw_content.decode("utf-8")
    else:
        return raw_content


def box_file_ai_ask(
    client: BoxClient, file_id: str, prompt: str, ai_agent: AiAgentAsk = None
) -> str:
    mode = CreateAiAskMode.SINGLE_ITEM_QA
    ai_item = AiItemBase(id=file_id, type=AiItemBaseTypeField.FILE)
    response = client.ai.create_ai_ask(
        mode=mode, prompt=prompt, items=[ai_item], ai_agent=ai_agent
    )
    return response.answer


def box_file_ai_extract(
    client: BoxClient, file_id: str, prompt: str, ai_agent: AiAgentAsk = None
) -> dict:
    ai_item = AiItemBase(id=file_id, type=AiItemBaseTypeField.FILE)
    response = client.ai.create_ai_extract(
        prompt=prompt, items=[ai_item], ai_agent=ai_agent
    )

    # Return a dictionary from the json answer
    return json.loads(response.answer)


def box_file_ai_extract_structured(
    client: BoxClient, file_id: str, fields_json_str: str
) -> str:
    ai_item = AiItemBase(id=file_id, type=AiItemBaseTypeField.FILE)
    fields_list = json.loads(fields_json_str)
    ai_fields = []
    options = []
    for field in fields_list:
        field_options = field.get("options")
        if field_options is not None:
            for option in field.get("options"):
                options.append(
                    CreateAiExtractStructuredFieldsOptionsField(key=option.get("key"))
                )

        ai_fields.append(
            CreateAiExtractStructuredFields(
                key=field.get("key"),
                description=field.get("description"),
                display_name=field.get("display_name"),
                prompt=field.get("prompt"),
                type=field.get("type"),
                options=options if options is not None and len(options) > 0 else None,
            )
        )
    response: AiExtractResponse = client.ai.create_ai_extract_structured(
        items=[ai_item], fields=ai_fields
    )
    return json.dumps(response.to_dict(), indent=2)


def box_folder_text_representation(
    client: BoxClient,
    folder_id: str,
    is_recursive: bool = False,
    by_pass_text_extraction: bool = False,
) -> Iterable[BoxFileExtended]:
    # folder items iterator
    for item in client.folders.get_folder_items(folder_id).entries:
        if item.type == "file":
            file = box_file_get_by_id(client=client, file_id=item.id)
            if not by_pass_text_extraction:
                text_representation = box_file_text_extract(
                    client=client, file_id=item.id
                )
            else:
                text_representation = ""
            yield BoxFileExtended(file=file, text_representation=text_representation)
        elif item.type == "folder" and is_recursive:
            yield from box_folder_text_representation(
                client=client,
                folder_id=item.id,
                is_recursive=is_recursive,
                by_pass_text_extraction=by_pass_text_extraction,
            )


def box_folder_ai_ask(
    client: BoxClient,
    folder_id: str,
    prompt: str,
    is_recursive: bool = False,
    by_pass_text_extraction: bool = False,
) -> Iterable[BoxFileExtended]:
    # folder items iterator
    for item in client.folders.get_folder_items(folder_id).entries:
        if item.type == "file":
            file = box_file_get_by_id(client=client, file_id=item.id)
            if not by_pass_text_extraction:
                text_representation = box_file_ai_ask(
                    client=client, file_id=item.id, prompt=prompt
                )
            else:
                text_representation = ""
            yield BoxFileExtended(file=file, text_representation=text_representation)
        elif item.type == "folder" and is_recursive:
            yield from box_folder_ai_ask(
                client=client,
                folder_id=item.id,
                prompt=prompt,
                is_recursive=is_recursive,
                by_pass_text_extraction=by_pass_text_extraction,
            )


def box_folder_ai_extract(
    client: BoxClient,
    folder_id: str,
    prompt: str,
    is_recursive: bool = False,
    by_pass_text_extraction: bool = False,
) -> Iterable[BoxFileExtended]:
    # folder items iterator
    for item in client.folders.get_folder_items(folder_id).entries:
        if item.type == "file":
            file = box_file_get_by_id(client=client, file_id=item.id)
            if not by_pass_text_extraction:
                text_representation = box_file_ai_extract(
                    client=client, file_id=item.id, prompt=prompt
                )
            else:
                text_representation = ""
            yield BoxFileExtended(file=file, text_representation=text_representation)
        elif item.type == "folder" and is_recursive:
            yield from box_folder_ai_extract(
                client=client,
                folder_id=item.id,
                prompt=prompt,
                is_recursive=is_recursive,
                by_pass_text_extraction=by_pass_text_extraction,
            )


def box_folder_ai_extract_structured(
    client: BoxClient,
    folder_id: str,
    fields_json_str: str,
    is_recursive: bool = False,
    by_pass_text_extraction: bool = False,
) -> Iterable[BoxFileExtended]:
    # folder items iterator
    for item in client.folders.get_folder_items(folder_id).entries:
        if item.type == "file":
            file = box_file_get_by_id(client=client, file_id=item.id)
            if not by_pass_text_extraction:
                text_representation = box_file_ai_extract_structured(
                    client=client, file_id=item.id, fields_json_str=fields_json_str
                )
            else:
                text_representation = ""
            yield BoxFileExtended(file=file, text_representation=text_representation)
        elif item.type == "folder" and is_recursive:
            yield from box_folder_ai_extract_structured(
                client=client,
                folder_id=item.id,
                fields_json_str=fields_json_str,
                is_recursive=is_recursive,
                by_pass_text_extraction=by_pass_text_extraction,
            )


def box_search(
    client: BoxClient,
    query: str,
    file_extensions: List[str] | None = None,
    content_types: List[SearchForContentContentTypes] | None = None,
    ancestor_folder_ids: List[str] | None = None,
) -> List[File]:
    # content_types: List[SearchForContentContentTypes] = [
    #     SearchForContentContentTypes.NAME,
    #     SearchForContentContentTypes.DESCRIPTION,
    #     # SearchForContentContentTypes.FILE_CONTENT,
    #     SearchForContentContentTypes.COMMENTS,
    #     SearchForContentContentTypes.TAG,
    # ]
    type = [
        SearchForContentType.FILE,
    ]
    fields: List[str] = ["id", "name", "type", "size", "description"]

    search_results = client.search.search_for_content(
        query=query,
        file_extensions=file_extensions,
        ancestor_folder_ids=ancestor_folder_ids,
        content_types=content_types,
        type=type,
        fields=fields,
    )
    return search_results.entries


def box_locate_folder_by_name(
    client: BoxClient, folder_name: str, parent_folder_id: str = "0"
) -> List[Folder]:
    type = [
        SearchForContentType.FOLDER,
    ]
    fields: List[str] = ["id", "name", "type"]

    content_types: List[SearchForContentContentTypes] = [
        SearchForContentContentTypes.NAME,
    ]

    search_results = client.search.search_for_content(
        query=folder_name,
        # file_extensions=file_extensions,
        ancestor_folder_ids=parent_folder_id,
        content_types=content_types,
        type=type,
        fields=fields,
    )
    return search_results.entries


def box_folder_list_content(
    client: BoxClient, folder_id: str, is_recursive: bool = False
) -> List[Union[File, FolderMini]]:
    # fields = "id,name,type"
    result: List[Union[File, FolderMini]] = []

    for item in client.folders.get_folder_items(folder_id).entries:
        if item.type == "web_link":
            continue
        if item.type == "folder" and is_recursive:
            result.extend(box_folder_list_content(client, item.id, is_recursive))
        result.append(item)

    return result


def box_file_download(
    client: BoxClient, 
    file_id: Any, 
    save_file: bool = False, 
    save_path: Optional[str] = None
) -> Tuple[Optional[str], Optional[bytes], Optional[str]]:
    """
    Downloads a file from Box and optionally saves it locally.
    
    Args:
        client (BoxClient): An authenticated Box client
        file_id (Any): The ID of the file to download. Can be string or int.
        save_file (bool, optional): Whether to save the file locally. Defaults to False.
        save_path (str, optional): Path where to save the file. Defaults to None.
        
    Returns:
        Tuple containing:
            - path_saved (str or None): Path where file was saved if save_file=True
            - file_content (bytes): Raw file content
            - mime_type (str): Detected MIME type
            
    Raises:
        BoxSDKError: If an error occurs during file download
    """
    # Ensure file_id is a string
    file_id_str = str(file_id)
    
    # Get file info first to check file type
    file_info = client.files.get_file_by_id(file_id_str)
    file_name = file_info.name
    
    # Download the file
    download_stream = client.downloads.download_file(file_id_str)
    file_content = download_stream.read()
    
    # Get file extension and detect mime type
    file_extension = file_name.split('.')[-1].lower() if '.' in file_name else ''
    mime_type, _ = mimetypes.guess_type(file_name)
    
    # Save file locally if requested
    saved_path = None
    if save_file:
        # Determine where to save the file
        if save_path:
            # Use provided path
            full_save_path = save_path
            if os.path.isdir(save_path):
                # If it's a directory, append the filename
                full_save_path = os.path.join(save_path, file_name)
        else:
            # Use temp directory with the original filename
            temp_dir = tempfile.gettempdir()
            full_save_path = os.path.join(temp_dir, file_name)
        
        # Save the file
        with open(full_save_path, 'wb') as f:
            f.write(file_content)
        saved_path = full_save_path
    
    return saved_path, file_content, mime_type


def box_available_ai_agents(client: BoxClient) -> List[AiSingleAgentResponseFull]:
    return client.ai_studio.get_ai_agents().entries


def box_claude_ai_agent_ask() -> AiAgentAsk:
    return AiAgentAsk(
        type=AiAgentAskTypeField.AI_AGENT_ASK,
        long_text=AiAgentLongTextTool(
            model="aws__claude_3_7_sonnet",
        ),
        basic_text=AiAgentBasicTextTool(
            model="aws__claude_3_7_sonnet",
        ),
        long_text_multi=AiAgentLongTextTool(
            model="aws__claude_3_7_sonnet",
        ),
        basic_text_multi=AiAgentBasicTextTool(
            model="aws__claude_3_7_sonnet",
        ),
    )


def box_claude_ai_agent_extract() -> AiAgentExtract:
    return AiAgentExtract(
        type=AiAgentExtractTypeField.AI_AGENT_EXTRACT,
        long_text=AiAgentLongTextTool(
            model="aws__claude_3_7_sonnet",
        ),
        basic_text=AiAgentBasicTextTool(
            model="aws__claude_3_7_sonnet",
        ),
    )


# Folder Management Functions

def box_create_folder(client: BoxClient, name: str, parent_id: Any = "0") -> FolderFull:
    """
    Creates a new folder in Box.
    
    Args:
        client (BoxClient): An authenticated Box client
        name (str): Name for the new folder
        parent_id (Any, optional): ID of the parent folder. Can be string or int.
                                  Defaults to "0" (root folder).
        
    Returns:
        FolderFull: The created folder object
        
    Raises:
        BoxSDKError: If an error occurs during folder creation
    """
    # Ensure parent_id is a string
    parent_id_str = str(parent_id) if parent_id is not None else "0"
    
    return client.folders.create_folder(
        name=name,
        parent=CreateFolderParent(id=parent_id_str)
    )


def box_update_folder(
    client: BoxClient, 
    folder_id: Any, 
    name: Optional[str] = None, 
    description: Optional[str] = None,
    parent_id: Optional[Any] = None
) -> FolderFull:
    """
    Updates a folder's properties in Box.
    
    Args:
        client (BoxClient): An authenticated Box client
        folder_id (Any): ID of the folder to update. Can be string or int.
        name (str, optional): New name for the folder
        description (str, optional): New description for the folder
        parent_id (Any, optional): ID of the new parent folder (for moving). Can be string or int.
        
    Returns:
        FolderFull: The updated folder object
        
    Raises:
        BoxSDKError: If an error occurs during folder update
    """
    # Ensure folder_id is a string
    folder_id_str = str(folder_id)
    
    update_params = {}
    if name:
        update_params["name"] = name
    if description:
        update_params["description"] = description
    if parent_id is not None:
        # Ensure parent_id is a string
        parent_id_str = str(parent_id)
        update_params["parent"] = UpdateFolderByIdParent(id=parent_id_str)
        
    return client.folders.update_folder_by_id(
        folder_id=folder_id_str,
        **update_params
    )


def box_delete_folder(client: BoxClient, folder_id: Any, recursive: bool = False) -> None:
    """
    Deletes a folder from Box.
    
    Args:
        client (BoxClient): An authenticated Box client
        folder_id (Any): ID of the folder to delete. Can be string or int.
        recursive (bool, optional): Whether to delete recursively. Defaults to False.
        
    Raises:
        BoxSDKError: If an error occurs during folder deletion
    """
    # Ensure folder_id is a string
    folder_id_str = str(folder_id)
    
    client.folders.delete_folder_by_id(
        folder_id=folder_id_str,
        recursive=recursive
    )
    return None


# File Upload and Download Functions

def box_upload_file(
    client: BoxClient, 
    content: str, 
    file_name: str, 
    folder_id: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Uploads content as a file to Box.
    
    Args:
        client (BoxClient): An authenticated Box client
        content (str): The content to upload as a file
        file_name (str): The name to give the file in Box
        folder_id (Any, optional): The ID of the folder to upload to. Can be string or int.
                                  Defaults to "0" (root).
        
    Returns:
        Dict containing information about the uploaded file including id and name
        
    Raises:
        BoxSDKError: If an error occurs during file upload
    """
    # Create a temporary file
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
        temp_file.write(content)
        temp_file_path = temp_file.name

    try:
        # Upload the file
        with open(temp_file_path, 'rb') as file:
            # Use root folder if folder_id is not provided
            parent_id = "0"
            if folder_id is not None:
                parent_id = str(folder_id)
                
            uploaded_file = client.uploads.upload_file(
                UploadFileAttributes(
                    name=file_name,
                    parent=UploadFileAttributesParentField(id=parent_id)
                ),
                file
            )
            
            # Return the first entry which contains file info
            return {
                "id": uploaded_file.entries[0].id,
                "name": uploaded_file.entries[0].name,
                "type": uploaded_file.entries[0].type
            }
    finally:
        # Clean up the temporary file
        os.unlink(temp_file_path)
