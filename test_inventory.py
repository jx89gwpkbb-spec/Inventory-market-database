import os
import tempfile
from inventory import models


def test_init_and_basic_flow():
    fd, path = tempfile.mkstemp(prefix="inv_test_", suffix=".db")
    os.close(fd)
    try:
        # use a fresh DB file
        models.init_db(path)
        pid = models.create_product("SKU1", "Test Prod", "desc", db_path=path)
        wid1 = models.create_warehouse("W1", "loc1", db_path=path)
        wid2 = models.create_warehouse("W2", "loc2", db_path=path)
        models.add_stock(pid, wid1, 50, "initial", db_path=path)
        models.transfer_stock(pid, wid1, wid2, 20, "move", db_path=path)
        inv = models.get_product_inventory(pid, db_path=path)
        # inventory rows should exist for both warehouses
        assert any(r["warehouse_id"] == wid1 and r["quantity"] == 30 for r in inv)
        assert any(r["warehouse_id"] == wid2 and r["quantity"] == 20 for r in inv)
    finally:
        os.remove(path)
