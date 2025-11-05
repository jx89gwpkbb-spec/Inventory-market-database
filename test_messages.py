import os
import tempfile
import pytest
from inventory import web, models


@pytest.fixture
def client(tmp_path):
    db_file = tmp_path / "test.db"
    models.init_db(str(db_file))
    web.app.config['TESTING'] = True
    # disable CSRF for test client convenience
    web.app.config['WTF_CSRF_ENABLED'] = False
    web.DB_PATH = str(db_file)
    client = web.app.test_client()
    yield client


def test_create_user_shows_flash(client):
    resp = client.post('/users/new', data={
        'username': 'alice', 'email': 'a@example.com', 'password': 'secret'
    }, follow_redirects=True)
    assert b'User created' in resp.data


def test_auto_login_after_create(client):
    resp = client.post('/users/new', data={
        'username': 'carol', 'email': 'c@example.com', 'password': 'secret'
    }, follow_redirects=True)
    # after auto-login we should see the switchboard mentioning the signed-in username
    assert b'Signed in as' in resp.data
    assert b'carol' in resp.data


def test_failed_login_shows_error(client):
    resp = client.post('/login', data={'identifier': 'noone', 'password': 'x'}, follow_redirects=True)
    assert b'Invalid credentials' in resp.data


def test_delete_user_shows_info(client):
    # create a user then delete
    client.post('/users/new', data={'username': 'bob', 'email': 'b@example.com'})
    # find user id
    rows = models.list_users(db_path=web.DB_PATH)
    uid = rows[0]['id']
    resp = client.post(f'/users/{uid}/delete', follow_redirects=True)
    assert b'User deleted' in resp.data
