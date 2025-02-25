from box_sdk_gen import BoxClient
from src.lib.box_api import box_file_ai_ask, box_file_ai_extract


def test_box_api_ai_ask(box_client: BoxClient):
    # HAB-1-01.docx = 1728677291168. This file must exists
    resp = box_file_ai_ask(
        box_client, "1728677291168", "what are the key point of this file"
    )
    assert resp is not None
    assert len(resp) > 0
    assert "HAB-1-01" in resp


def test_box_api_ai_extract(box_client: BoxClient):
    resp: dict = box_file_ai_extract(
        box_client,
        "1728677291168",
        "contract date, start date, end date, lessee name, lessee email, rent, property id",
    )
    assert resp is not None
    assert len(resp) > 0
    assert resp.get("contract date") is not None
    assert resp.get("start date") is not None
