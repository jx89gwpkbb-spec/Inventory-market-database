"""Small Flask web app to add users for the inventory demo.

Run: python -m inventory.web

Routes:
- GET  /users/new  -> HTML form
- POST /users/new  -> create user and show a simple success message
- GET  /users      -> list users
"""
import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_wtf import CSRFProtect
from inventory import models

app = Flask(__name__)
DB_PATH = "inventory.db"
# prefer environment-provided secret; fallback is only for local/dev convenience
app.secret_key = os.environ.get("FLASK_SECRET", "dev-secret-for-demo")
csrf = CSRFProtect(app)


@app.route("/users")
def users_list():
    # optional search/filter parameter `q` filters username or email (case-insensitive)
    q = request.args.get("q", "")
    if q:
        q_like = f"%{q}%"
        # simple SQL filter performed in the models layer via raw query
        conn = None
        try:
            conn = models.get_conn(DB_PATH)
            users = conn.execute(
                "SELECT * FROM users WHERE username LIKE ? OR email LIKE ? ORDER BY id",
                (q_like, q_like),
            ).fetchall()
        finally:
            if conn:
                conn.close()
    else:
        users = models.list_users(db_path=DB_PATH)
    return render_template("users_list.html", users=users, q=q)


@app.route("/")
def switchboard():
    """Central landing / switchboard with quick links and an inline add-user form.

    The inline form posts to `/users/new` so it reuses the same create logic.
    """
    user = None
    uid = session.get("user_id")
    if uid:
        user = models.get_user_by_id(uid, db_path=DB_PATH)
    return render_template("switchboard.html", current_user=user)


@app.route("/login", methods=["GET"])
def login_form():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login():
    identifier = request.form.get("identifier")
    password = request.form.get("password")
    if not identifier or not password:
        flash("Identifier and password are required", "error")
        return render_template("login.html", identifier=identifier), 400
    user = models.authenticate_user(identifier, password, db_path=DB_PATH)
    if not user:
        flash("Invalid credentials", "error")
        return render_template("login.html", identifier=identifier), 401
    session["user_id"] = user["id"]
    flash(f"Signed in as {user['username']}", "success")
    return redirect(url_for("switchboard"))


@app.route("/logout", methods=["POST"])
def logout():
    session.pop("user_id", None)
    flash("Signed out", "info")
    return redirect(url_for("switchboard"))


@app.route("/users/new", methods=["GET"])
def new_user_form():
    return render_template("new_user.html")


@app.route("/users/new", methods=["POST"])
def create_user():
    username = request.form.get("username")
    email = request.form.get("email")
    full_name = request.form.get("full_name")
    password = request.form.get("password")
    if not username or not email:
        flash("Username and email are required", "error")
        return render_template("new_user.html"), 400
    try:
        uid = models.create_user(username, email, full_name, password=password, db_path=DB_PATH)
    except Exception as e:
        flash(f"Error creating user: {e}", "error")
        return render_template("new_user.html"), 400
    # auto-login the newly created user for a smoother demo experience
    session["user_id"] = uid
    flash(f"User created and signed in as {username}", "success")
    return redirect(url_for("switchboard"))


@app.route('/users/<int:user_id>/delete', methods=['POST'])
def delete_user(user_id: int):
    try:
        models.delete_user(user_id, db_path=DB_PATH)
    except Exception as e:
        flash(f"Error deleting user: {e}", "error")
        return redirect(url_for('users_list'))
    flash("User deleted", "info")
    return redirect(url_for('users_list'))


if __name__ == "__main__":
    # ensure DB exists
    models.init_db(DB_PATH)
    app.run(host="127.0.0.1", port=5000, debug=True)
