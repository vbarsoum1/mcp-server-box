from src.lib.box_authentication import authorize_app, get_oauth_client
import pytest


@pytest.mark.skip
def test_box_authorize_app_tool():
    try:
        authorize_app()
    except Exception as e:
        assert str(e) == "Box application not authorized yet."


@pytest.mark.skip
def test_box_auth_client():
    try:
        client = get_oauth_client()
    except Exception as e:
        assert str(e) == "Box application not authorized yet."
