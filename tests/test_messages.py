import os
import tempfile
from inventory import web


def setup_app(tmpdb):
    web.app.config['TESTING'] = True
    web.app.config['WTF_CSRF_ENABLED'] = False
    web.DB_PATH = tmpdb
    return web.app.test_client()


def test_users_pages():
    tmp = tempfile.NamedTemporaryFile(delete=False)
    tmp.close()
    try:
        client = setup_app(tmp.name)
        # list users page
        rv = client.get('/users')
        assert rv.status_code == 200
        # new user form page
        rv = client.get('/users/new')
        assert rv.status_code == 200
    finally:
        try:
            os.unlink(tmp.name)
        except Exception:
            pass
