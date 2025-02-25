import pytest
from box_sdk_gen import BoxClient
from src.lib.box_api import get_box_ccg_client


@pytest.fixture
def box_client() -> BoxClient:
    return get_box_ccg_client()
