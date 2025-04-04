import pytest


from box_ai_agents_toolkit import BoxClient, get_oauth_client


@pytest.fixture
def box_client() -> BoxClient:
    # return get_ccg_client()
    return get_oauth_client()
