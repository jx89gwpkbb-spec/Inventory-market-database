"""
Simple SQLite-backed data layer for the inventory demo.
Provides: init_db, create_product, create_warehouse, add_stock, remove_stock, transfer_stock,
get_product_inventory, list_products

This is intentionally lightweight and synchronous to keep the demo dependency-free.
"""
import sqlite3
from typing import Optional, List, Dict, Any
from werkzeug.security import generate_password_hash, check_password_hash

SCHEMA_PATH = "./db/schema.sql"


def dict_factory(cursor, row):
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}


def get_conn(db_path: str = ":memory:") -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = dict_factory
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db(db_path: str = "inventory.db"):
    conn = get_conn(db_path)
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        sql = f.read()
    conn.executescript(sql)
    conn.commit()
    conn.close()


# Product / Warehouse CRUD

def create_product(sku: str, name: str, description: Optional[str] = None, unit: str = "each", db_path: str = "inventory.db") -> int:
    conn = get_conn(db_path)
    cur = conn.execute(
        "INSERT INTO products (sku, name, description, unit) VALUES (?, ?, ?, ?)",
        (sku, name, description, unit),
    )
    conn.commit()
    product_id = cur.lastrowid
    conn.close()
    return product_id


def create_warehouse(name: str, location: Optional[str] = None, db_path: str = "inventory.db") -> int:
    conn = get_conn(db_path)
    cur = conn.execute(
        "INSERT INTO warehouses (name, location) VALUES (?, ?)", (name, location)
    )
    conn.commit()
    wid = cur.lastrowid
    conn.close()
    return wid


def list_products(db_path: str = "inventory.db") -> List[Dict[str, Any]]:
    conn = get_conn(db_path)
    rows = conn.execute("SELECT * FROM products ORDER BY id").fetchall()
    conn.close()
    return rows


# User CRUD (simple)
def create_user(username: str, email: str, full_name: Optional[str] = None, password: Optional[str] = None, db_path: str = "inventory.db") -> int:
    """Create a user. If `password` is provided it will be hashed and stored in `password_hash`.

    Notes: for existing DBs without the `password_hash` column, re-run `init_db` to recreate schema.
    """
    conn = get_conn(db_path)
    password_hash = None
    if password:
        password_hash = generate_password_hash(password)
    cur = conn.execute(
        "INSERT INTO users (username, email, full_name, password_hash) VALUES (?, ?, ?, ?)",
        (username, email, full_name, password_hash),
    )
    conn.commit()
    uid = cur.lastrowid
    conn.close()
    return uid


def list_users(db_path: str = "inventory.db") -> List[Dict[str, Any]]:
    conn = get_conn(db_path)
    rows = conn.execute("SELECT * FROM users ORDER BY id").fetchall()
    conn.close()
    return rows


def get_user_by_id(user_id: int, db_path: str = "inventory.db") -> Optional[Dict[str, Any]]:
    conn = get_conn(db_path)
    row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return row


def delete_user(user_id: int, db_path: str = "inventory.db") -> None:
    conn = get_conn(db_path)
    try:
        conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
    finally:
        conn.close()


def authenticate_user(username_or_email: str, password: str, db_path: str = "inventory.db") -> Optional[Dict[str, Any]]:
    """Return user dict if authentication succeeds, otherwise None."""
    conn = get_conn(db_path)
    try:
        row = conn.execute(
            "SELECT * FROM users WHERE username = ? OR email = ? LIMIT 1",
            (username_or_email, username_or_email),
        ).fetchone()
        if not row:
            return None
        stored = row.get("password_hash")
        if not stored:
            return None
        if check_password_hash(stored, password):
            return row
        return None
    finally:
        conn.close()


# Inventory operations

def _ensure_inventory_row(conn: sqlite3.Connection, product_id: int, warehouse_id: int):
    cur = conn.execute(
        "SELECT id FROM inventory WHERE product_id = ? AND warehouse_id = ?",
        (product_id, warehouse_id),
    )
    if cur.fetchone() is None:
        conn.execute(
            "INSERT INTO inventory (product_id, warehouse_id, quantity) VALUES (?, ?, 0)",
            (product_id, warehouse_id),
        )


def add_stock(product_id: int, warehouse_id: int, quantity: int, reason: Optional[str] = None, db_path: str = "inventory.db") -> None:
    if quantity <= 0:
        raise ValueError("quantity must be positive for add_stock")
    conn = get_conn(db_path)
    try:
        _ensure_inventory_row(conn, product_id, warehouse_id)
        conn.execute(
            "UPDATE inventory SET quantity = quantity + ? WHERE product_id = ? AND warehouse_id = ?",
            (quantity, product_id, warehouse_id),
        )
        conn.execute(
            "INSERT INTO movements (product_id, from_warehouse, to_warehouse, quantity, reason) VALUES (?, NULL, ?, ?, ?)",
            (product_id, warehouse_id, quantity, reason),
        )
        conn.commit()
    finally:
        conn.close()


def remove_stock(product_id: int, warehouse_id: int, quantity: int, reason: Optional[str] = None, db_path: str = "inventory.db") -> None:
    if quantity <= 0:
        raise ValueError("quantity must be positive for remove_stock")
    conn = get_conn(db_path)
    try:
        _ensure_inventory_row(conn, product_id, warehouse_id)
        cur = conn.execute(
            "SELECT quantity FROM inventory WHERE product_id = ? AND warehouse_id = ?",
            (product_id, warehouse_id),
        )
        row = cur.fetchone()
        if row is None:
            raise ValueError("inventory row missing")
        if row["quantity"] < quantity:
            raise ValueError("insufficient stock")
        conn.execute(
            "UPDATE inventory SET quantity = quantity - ? WHERE product_id = ? AND warehouse_id = ?",
            (quantity, product_id, warehouse_id),
        )
        conn.execute(
            "INSERT INTO movements (product_id, from_warehouse, to_warehouse, quantity, reason) VALUES (?, ?, NULL, ?, ?)",
            (product_id, warehouse_id, quantity, reason),
        )
        conn.commit()
    finally:
        conn.close()


def transfer_stock(product_id: int, from_warehouse: int, to_warehouse: int, quantity: int, reason: Optional[str] = None, db_path: str = "inventory.db") -> None:
    if quantity <= 0:
        raise ValueError("quantity must be positive for transfer_stock")
    conn = get_conn(db_path)
    try:
        _ensure_inventory_row(conn, product_id, from_warehouse)
        _ensure_inventory_row(conn, product_id, to_warehouse)
        cur = conn.execute(
            "SELECT quantity FROM inventory WHERE product_id = ? AND warehouse_id = ?",
            (product_id, from_warehouse),
        )
        row = cur.fetchone()
        if row is None or row["quantity"] < quantity:
            raise ValueError("insufficient stock to transfer")
        conn.execute(
            "UPDATE inventory SET quantity = quantity - ? WHERE product_id = ? AND warehouse_id = ?",
            (quantity, product_id, from_warehouse),
        )
        conn.execute(
            "UPDATE inventory SET quantity = quantity + ? WHERE product_id = ? AND warehouse_id = ?",
            (quantity, product_id, to_warehouse),
        )
        conn.execute(
            "INSERT INTO movements (product_id, from_warehouse, to_warehouse, quantity, reason) VALUES (?, ?, ?, ?, ?)",
            (product_id, from_warehouse, to_warehouse, quantity, reason),
        )
        conn.commit()
    finally:
        conn.close()


def get_product_inventory(product_id: int, db_path: str = "inventory.db") -> List[Dict[str, Any]]:
    conn = get_conn(db_path)
    rows = conn.execute(
        "SELECT i.*, w.name AS warehouse_name FROM inventory i JOIN warehouses w ON i.warehouse_id = w.id WHERE i.product_id = ?",
        (product_id,),
    ).fetchall()
    conn.close()
    return rows


if __name__ == "__main__":
    print("This module provides the data layer functions. Use `app.py` to demo.")
