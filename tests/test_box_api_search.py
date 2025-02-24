from typing import List
from box_sdk_gen import BoxClient, File
from src.box_api import box_search


def test_box_api_search_basic(box_client: BoxClient):
    search_results: List[File] = box_search(box_client, "HAB-1")

    assert len(search_results) > 0

    # Has HAB-1 in name
    assert any("HAB-1" in file.name for file in search_results)

    # Is a file
    assert all(file.type == "file" for file in search_results)
