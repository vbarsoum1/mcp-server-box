from box_sdk_gen import BoxClient, ByteStream
from src.lib.box_api import box_file_text_extract, box_file_download
import base64


def test_box_api_read_basic(box_client: BoxClient):
    # HAB-1-01.docx = 1728677291168. This file must exists
    resp = box_file_text_extract(box_client, "1728677291168")
    assert resp is not None
    assert len(resp) > 0
    assert "HAB-1-01" in resp


def test_box_api_file_download(box_client: BoxClient):
    # HAB-1-01.docx = 1728677291168. This file must exists
    resp: ByteStream = box_file_download(box_client, "1728677291168")

    # read resp and convert to base64
    data = resp.read()

    b64_bytes = base64.b64encode(data)
    b64_unicode = b64_bytes.decode("utf-8")

    assert b64_unicode is not None
    assert len(b64_unicode) > 0
