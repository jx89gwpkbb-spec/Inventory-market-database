"""Simple CLI demo for the inventory data layer.

Commands:
  init                   Create the SQLite DB and tables
  add-product            Add a product (sku, name)
  add-warehouse          Add a warehouse (name)
  stock-in               Add stock
  stock-out              Remove stock
  transfer               Transfer between warehouses
  list-products          Show products
  show-inventory <sku>   Show inventory rows for a product

Example:
  python app.py init
  python app.py add-product --sku PROD1 --name "Widget"
  python app.py add-warehouse --name "Main"
  python app.py add-warehouse --name "Overflow"
  python app.py stock-in --sku PROD1 --warehouse 1 --qty 100
  python app.py transfer --sku PROD1 --from 1 --to 2 --qty 20

"""
import argparse
import sys
from inventory import models

DB_PATH = "inventory.db"


def cmd_init(args):
    models.init_db(DB_PATH)
    print(f"Initialized DB at {DB_PATH}")


def cmd_add_product(args):
    pid = models.create_product(args.sku, args.name, args.description, args.unit, db_path=DB_PATH)
    print(f"Created product id={pid}")


def cmd_add_warehouse(args):
    wid = models.create_warehouse(args.name, args.location, db_path=DB_PATH)
    print(f"Created warehouse id={wid}")


def cmd_stock_in(args):
    # resolve sku -> id
    rows = [p for p in models.list_products(db_path=DB_PATH) if p["sku"] == args.sku]
    if not rows:
        print("Product not found")
        return
    pid = rows[0]["id"]
    models.add_stock(pid, args.warehouse, args.qty, args.reason, db_path=DB_PATH)
    print("Stock added")


def cmd_stock_out(args):
    rows = [p for p in models.list_products(db_path=DB_PATH) if p["sku"] == args.sku]
    if not rows:
        print("Product not found")
        return
    pid = rows[0]["id"]
    try:
        models.remove_stock(pid, args.warehouse, args.qty, args.reason, db_path=DB_PATH)
        print("Stock removed")
    except Exception as e:
        print("Error:", e)


def cmd_transfer(args):
    rows = [p for p in models.list_products(db_path=DB_PATH) if p["sku"] == args.sku]
    if not rows:
        print("Product not found")
        return
    pid = rows[0]["id"]
    try:
        models.transfer_stock(pid, args.from_warehouse, args.to_warehouse, args.qty, args.reason, db_path=DB_PATH)
        print("Transfer complete")
    except Exception as e:
        print("Error:", e)


def cmd_list_products(args):
    for p in models.list_products(db_path=DB_PATH):
        print(f"{p['id']}: {p['sku']} - {p['name']}")


def cmd_show_inventory(args):
    rows = [p for p in models.list_products(db_path=DB_PATH) if p["sku"] == args.sku]
    if not rows:
        print("Product not found")
        return
    pid = rows[0]["id"]
    for r in models.get_product_inventory(pid, db_path=DB_PATH):
        print(f"Warehouse {r['warehouse_id']} ({r['warehouse_name']}): {r['quantity']}")


def main(argv=None):
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd")

    sub.add_parser("init").set_defaults(func=cmd_init)

    ap = sub.add_parser("add-product")
    ap.add_argument("--sku", required=True)
    ap.add_argument("--name", required=True)
    ap.add_argument("--description", default=None)
    ap.add_argument("--unit", default="each")
    ap.set_defaults(func=cmd_add_product)

    aw = sub.add_parser("add-warehouse")
    aw.add_argument("--name", required=True)
    aw.add_argument("--location", default=None)
    aw.set_defaults(func=cmd_add_warehouse)

    si = sub.add_parser("stock-in")
    si.add_argument("--sku", required=True)
    si.add_argument("--warehouse", type=int, required=True)
    si.add_argument("--qty", type=int, required=True)
    si.add_argument("--reason", default=None)
    si.set_defaults(func=cmd_stock_in)

    so = sub.add_parser("stock-out")
    so.add_argument("--sku", required=True)
    so.add_argument("--warehouse", type=int, required=True)
    so.add_argument("--qty", type=int, required=True)
    so.add_argument("--reason", default=None)
    so.set_defaults(func=cmd_stock_out)

    tr = sub.add_parser("transfer")
    tr.add_argument("--sku", required=True)
    tr.add_argument("--from", dest="from_warehouse", type=int, required=True)
    tr.add_argument("--to", dest="to_warehouse", type=int, required=True)
    tr.add_argument("--qty", type=int, required=True)
    tr.add_argument("--reason", default=None)
    tr.set_defaults(func=cmd_transfer)

    sub.add_parser("list-products").set_defaults(func=cmd_list_products)

    si = sub.add_parser("show-inventory")
    si.add_argument("--sku", required=True)
    si.set_defaults(func=cmd_show_inventory)

    args = p.parse_args(argv)
    if not hasattr(args, "func"):
        p.print_help()
        return 1
    args.func(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
