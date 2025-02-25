from box_sdk_gen import BoxClient
from src.lib.box_api import box_file_ai_ask


def test_box_api_ai_ask(box_client: BoxClient):
    # HAB-1-01.docx = 1728677291168. This file must exists
    resp = box_file_ai_ask(
        box_client, "1728677291168", "what are the key point of this file"
    )
    assert resp is not None
    assert len(resp) > 0
    assert "HAB-1-01" in resp
