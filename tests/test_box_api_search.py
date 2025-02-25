from typing import List
from box_sdk_gen import BoxClient, File
from src.lib.box_api import box_search, box_locate_folder_by_name


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
