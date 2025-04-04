from box_ai_agents_toolkit import (
    BoxClient,
    box_file_text_extract,
    box_file_download,
)


def test_box_api_read_basic(box_client: BoxClient):
    # HAB-1-01.docx = 1728677291168. This file must exists
    resp = box_file_text_extract(box_client, "1728677291168")
    assert resp is not None
    assert len(resp) > 0
    assert "HAB-1-01" in resp


def test_box_api_file_download(box_client: BoxClient):
    # HAB-1-01.docx = 1728677291168. This file must exists
    saved_path, file_content, mime_type = box_file_download(box_client, "1728677291168")

    assert saved_path is None
    assert file_content is not None
    assert mime_type is not None
    assert len(file_content) > 0
