from typing import List


from box_ai_agents_toolkit import (
    BoxClient,
    File,
    box_folder_list_content,
    box_locate_folder_by_name,
    box_search,
)


def test_box_api_search_basic(box_client: BoxClient):
    search_results: List[File] = box_search(box_client, "HAB-1")

    assert len(search_results) > 0

    # Has HAB-1 in name
    assert any("HAB-1" in file.name for file in search_results)

    # Is a file
    assert all(file.type == "file" for file in search_results)


def test_box_api_locate_folder_by_name(box_client: BoxClient):
    folders = box_locate_folder_by_name(box_client, "Airbyte-CI")

    assert len(folders) > 0
    assert all(folder.type == "folder" for folder in folders)
    assert all("Airbyte-CI" in folder.name for folder in folders)


def test_box_api_list_content_folders(box_client: BoxClient):
    # This folder only has folders
    items = box_folder_list_content(box_client, "298939523710")

    assert len(items) > 0
    assert all(item.type in ["file", "folder"] for item in items)


def test_box_api_list_conten_filest(box_client: BoxClient):
    # This filder only has files
    items = box_folder_list_content(box_client, "298939487242")

    assert len(items) > 0
    assert all(item.type in ["file", "folder"] for item in items)
