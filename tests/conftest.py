import pytest
import sys
import os
from pathlib import Path

# Add the parent directory to path so we can import from src
sys.path.insert(0, str(Path(__file__).parent.parent))

from box_sdk_gen import BoxClient
from src.lib.box_authentication import get_ccg_client, get_oauth_client


@pytest.fixture
def box_client() -> BoxClient:
    # return get_ccg_client()
    return get_oauth_client()
