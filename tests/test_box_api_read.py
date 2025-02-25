from typing import List
from box_sdk_gen import BoxClient, File
from src.box_api import box_file_text_extract


def test_box_api_read_basic(box_client: BoxClient):
    # HAB-1-01.docx = 1728677291168. This file must exists
    resp = box_file_text_extract(box_client, "1728677291168")
    assert resp is not None
    assert len(resp) > 0
    assert "HAB-1-01" in resp
