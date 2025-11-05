import os
import tempfile
from inventory import models

def test_init_and_basic_ops():
    tmp = tempfile.NamedTemporaryFile(delete=False)
    tmp.close()
    try:
        db_path = tmp.name
        models.init_db(db_path)
        p = models.create_product(db_path, 'Widget')
        w = models.create_warehouse(db_path, 'Main')
        models.add_stock(db_path, p, w, 10)
        inv = models.get_product_inventory(db_path, p)
        # inventory rows are returned as list-like; assert quantity found
        assert any(r.get('quantity', 0) >= 10 for r in inv)
    finally:
        try:
            os.unlink(tmp.name)
        except Exception:
            pass
