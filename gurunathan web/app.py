import os
import sqlite3
import uuid
from datetime import datetime
from functools import wraps

from flask import (
    Flask,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "shop.db")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "images", "products")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "gif"}

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "change-this-in-production")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

SHOP_INFO = {
    "name": "Gurunathan Traders",
    "tagline": "Your Trusted Plumbing, Electrical & Hardware Store",
    "phone": "+91 94444 55667",
    "whatsapp": "919444455667",
    "email": "gurunathantraders@example.com",
    "address": "Near Hosur, Tamil Nadu, India",
}


def get_db():
    """Open one SQLite connection per request."""
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_error):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    db = sqlite3.connect(DB_PATH)
    cursor = db.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            image_url TEXT
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            price REAL NOT NULL,
            category_id INTEGER NOT NULL,
            image_url TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (category_id) REFERENCES categories (id)
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS admin_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS contact_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT,
            message TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )

    default_categories = [
        ("Plumbing Materials", "/static/images/site/plumbing.svg"),
        ("Electrical Items", "/static/images/site/electrical.svg"),
        ("Hardware Tools", "/static/images/site/hardware.svg"),
        ("Paints", "/static/images/site/paints.svg"),
    ]
    cursor.executemany(
        "INSERT OR IGNORE INTO categories (name, image_url) VALUES (?, ?)",
        default_categories,
    )

    cursor.execute("SELECT COUNT(*) AS total FROM products")
    if cursor.fetchone()[0] == 0:
        cursor.execute("SELECT id, name FROM categories")
        category_map = {row[1]: row[0] for row in cursor.fetchall()}

        sample_products = [
            (
                "CPVC Pipe 1 inch",
                "Durable hot and cold water CPVC pipe suitable for home plumbing.",
                320.0,
                category_map["Plumbing Materials"],
                "/static/images/site/sample-plumbing.svg",
            ),
            (
                "LED Bulb 12W",
                "Energy-efficient LED bulb for domestic and commercial use.",
                140.0,
                category_map["Electrical Items"],
                "/static/images/site/sample-electrical.svg",
            ),
            (
                "Adjustable Spanner",
                "Heavy-duty adjustable spanner for maintenance and repair work.",
                450.0,
                category_map["Hardware Tools"],
                "/static/images/site/sample-hardware.svg",
            ),
            (
                "Weather Shield Exterior Paint",
                "Long-lasting paint with smooth finish for outdoor walls.",
                1850.0,
                category_map["Paints"],
                "/static/images/site/sample-paints.svg",
            ),
        ]

        cursor.executemany(
            """
            INSERT INTO products (name, description, price, category_id, image_url, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            [(*item, datetime.utcnow().isoformat()) for item in sample_products],
        )

    cursor.execute("SELECT COUNT(*) AS total FROM admin_users")
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            """
            INSERT INTO admin_users (username, password_hash, created_at)
            VALUES (?, ?, ?)
            """,
            (
                "admin",
                generate_password_hash("Admin@123"),
                datetime.utcnow().isoformat(),
            ),
        )

    db.commit()
    db.close()


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def save_product_image(file_storage):
    if not file_storage or file_storage.filename == "":
        return None
    if not allowed_file(file_storage.filename):
        return None

    ext = file_storage.filename.rsplit(".", 1)[1].lower()
    safe_name = secure_filename(file_storage.filename.rsplit(".", 1)[0])
    final_name = f"{safe_name}-{uuid.uuid4().hex[:8]}.{ext}"
    full_path = os.path.join(app.config["UPLOAD_FOLDER"], final_name)
    file_storage.save(full_path)
    return f"/static/images/products/{final_name}"


def login_required(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if not session.get("admin_id"):
            flash("Please login to continue.", "warning")
            return redirect(url_for("admin_login"))
        return view_func(*args, **kwargs)

    return wrapped


@app.context_processor
def inject_shop_info():
    return {"shop": SHOP_INFO}


@app.route("/")
def home():
    db = get_db()
    categories = db.execute("SELECT * FROM categories ORDER BY name").fetchall()
    featured = db.execute(
        """
        SELECT p.*, c.name AS category_name
        FROM products p
        JOIN categories c ON p.category_id = c.id
        ORDER BY p.id DESC
        LIMIT 4
        """
    ).fetchall()
    return render_template("home.html", categories=categories, featured=featured)


@app.route("/products")
def products():
    db = get_db()
    search = request.args.get("q", "").strip()
    category_id = request.args.get("category", "").strip()

    categories = db.execute("SELECT * FROM categories ORDER BY name").fetchall()

    query = (
        """
        SELECT p.*, c.name AS category_name
        FROM products p
        JOIN categories c ON p.category_id = c.id
        WHERE 1 = 1
        """
    )
    params = []

    if search:
        query += " AND (p.name LIKE ? OR p.description LIKE ?)"
        like_term = f"%{search}%"
        params.extend([like_term, like_term])

    if category_id and category_id.isdigit():
        query += " AND p.category_id = ?"
        params.append(int(category_id))

    query += " ORDER BY p.id DESC"
    product_rows = db.execute(query, params).fetchall()

    return render_template(
        "products.html",
        products=product_rows,
        categories=categories,
        search=search,
        active_category=category_id,
    )


@app.route("/services")
def services():
    return render_template("services.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()
        email = request.form.get("email", "").strip()
        message = request.form.get("message", "").strip()

        if not name or not phone or not message:
            flash("Name, phone and message are required.", "danger")
            return redirect(url_for("contact"))

        db = get_db()
        db.execute(
            """
            INSERT INTO contact_messages (name, phone, email, message, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (name, phone, email, message, datetime.utcnow().isoformat()),
        )
        db.commit()
        flash("Thank you. Your message has been sent.", "success")
        return redirect(url_for("contact"))

    return render_template("contact.html")


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if session.get("admin_id"):
        return redirect(url_for("admin_dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        db = get_db()
        user = db.execute(
            "SELECT * FROM admin_users WHERE username = ?",
            (username,),
        ).fetchone()

        if user and check_password_hash(user["password_hash"], password):
            session["admin_id"] = user["id"]
            session["admin_username"] = user["username"]
            flash("Welcome back.", "success")
            return redirect(url_for("admin_dashboard"))

        flash("Invalid username or password.", "danger")

    return render_template("admin/login.html")


@app.route("/admin/logout")
@login_required
def admin_logout():
    session.clear()
    flash("Logged out successfully.", "success")
    return redirect(url_for("admin_login"))


@app.route("/admin")
@login_required
def admin_dashboard():
    db = get_db()
    products_rows = db.execute(
        """
        SELECT p.*, c.name AS category_name
        FROM products p
        JOIN categories c ON p.category_id = c.id
        ORDER BY p.id DESC
        """
    ).fetchall()
    return render_template("admin/dashboard.html", products=products_rows)


@app.route("/admin/products/new", methods=["GET", "POST"])
@login_required
def admin_add_product():
    db = get_db()
    categories = db.execute("SELECT * FROM categories ORDER BY name").fetchall()

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        price_raw = request.form.get("price", "").strip()
        category_id = request.form.get("category_id", "").strip()

        if not name or not description or not price_raw or not category_id:
            flash("All fields are required.", "danger")
            return render_template("admin/product_form.html", categories=categories, product=None)

        try:
            price = float(price_raw)
        except ValueError:
            flash("Price must be a number.", "danger")
            return render_template("admin/product_form.html", categories=categories, product=None)

        image_url = save_product_image(request.files.get("image"))
        if image_url is None:
            image_url = "/static/images/site/product-placeholder.svg"

        db.execute(
            """
            INSERT INTO products (name, description, price, category_id, image_url, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (name, description, price, int(category_id), image_url, datetime.utcnow().isoformat()),
        )
        db.commit()
        flash("Product added successfully.", "success")
        return redirect(url_for("admin_dashboard"))

    return render_template("admin/product_form.html", categories=categories, product=None)


@app.route("/admin/products/<int:product_id>/edit", methods=["GET", "POST"])
@login_required
def admin_edit_product(product_id):
    db = get_db()
    categories = db.execute("SELECT * FROM categories ORDER BY name").fetchall()
    product = db.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()

    if not product:
        flash("Product not found.", "danger")
        return redirect(url_for("admin_dashboard"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        price_raw = request.form.get("price", "").strip()
        category_id = request.form.get("category_id", "").strip()

        if not name or not description or not price_raw or not category_id:
            flash("All fields are required.", "danger")
            return render_template("admin/product_form.html", categories=categories, product=product)

        try:
            price = float(price_raw)
        except ValueError:
            flash("Price must be a number.", "danger")
            return render_template("admin/product_form.html", categories=categories, product=product)

        image_url = product["image_url"]
        new_image_url = save_product_image(request.files.get("image"))
        if new_image_url:
            if image_url and image_url.startswith("/static/images/products/"):
                old_path = os.path.join(BASE_DIR, image_url.lstrip("/"))
                if os.path.exists(old_path):
                    os.remove(old_path)
            image_url = new_image_url

        db.execute(
            """
            UPDATE products
            SET name = ?, description = ?, price = ?, category_id = ?, image_url = ?
            WHERE id = ?
            """,
            (name, description, price, int(category_id), image_url, product_id),
        )
        db.commit()
        flash("Product updated.", "success")
        return redirect(url_for("admin_dashboard"))

    return render_template("admin/product_form.html", categories=categories, product=product)


@app.route("/admin/products/<int:product_id>/delete", methods=["POST"])
@login_required
def admin_delete_product(product_id):
    db = get_db()
    product = db.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()

    if not product:
        flash("Product not found.", "danger")
        return redirect(url_for("admin_dashboard"))

    image_url = product["image_url"]
    if image_url and image_url.startswith("/static/images/products/"):
        image_path = os.path.join(BASE_DIR, image_url.lstrip("/"))
        if os.path.exists(image_path):
            os.remove(image_path)

    db.execute("DELETE FROM products WHERE id = ?", (product_id,))
    db.commit()
    flash("Product deleted.", "success")
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/messages")
@login_required
def admin_messages():
    db = get_db()
    messages = db.execute(
        "SELECT * FROM contact_messages ORDER BY id DESC"
    ).fetchall()
    return render_template("admin/messages.html", messages=messages)


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
