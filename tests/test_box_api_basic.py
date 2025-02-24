def test_box_api_basic_connection(box_client):
    user = box_client.users.get_user_me()
    assert user.id is not None
    assert user.name is not None
    assert user.login is not None
