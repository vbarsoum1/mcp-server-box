from src.lib.box_authentication import authorize_app


def test_box_authorize_app_tool():
    try:
        authorize_app()
    except Exception as e:
        assert str(e) == "Box application not authorized yet."
