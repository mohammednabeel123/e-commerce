from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os 
app = Flask(
    __name__,
    template_folder="app/templates",
    static_folder="app/static"
)
# =========================
# CONFIG
# =========================

app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "postgresql://velora_3szh_user:WAUVWpGKyODPmk986YooiXK7lXJGJ8hz@dpg-d7hucg9j2pic73agj4mg-a/velora_3szh",
    "sqlite:///store.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
# =========================
# MODELS
# =========================
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    is_admin = db.Column(db.Boolean, default=False)

    cart_items = db.relationship(
        "CartItem",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan"
    )




class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    product_id = db.Column(db.Integer, nullable=False)
    product_name = db.Column(db.String(150), nullable=False)
    price = db.Column(db.Float, nullable=False)
    image = db.Column(db.String(255), nullable=False)

    size = db.Column(db.String(20), nullable=False)
    color = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)




class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    customer_name = db.Column(db.String(120), nullable=False)
    customer_email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(30), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    address = db.Column(db.Text, nullable=False)
    note = db.Column(db.Text, nullable=True)

    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default="Pending")

    created_at = db.Column(db.DateTime, server_default=db.func.now())

    items = db.relationship(
        "OrderItem",
        backref="order",
        lazy=True,
        cascade="all, delete-orphan"
    )


class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("order.id"), nullable=False)

    product_id = db.Column(db.Integer, nullable=False)
    product_name = db.Column(db.String(150), nullable=False)
    price = db.Column(db.Float, nullable=False)
    image = db.Column(db.String(255), nullable=False)

    size = db.Column(db.String(20), nullable=False)
    color = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Integer, nullable=False) 

# =========================
# PRODUCTS (TEMP DATA)
# =========================
products = [
    {
        "id": 1,
        "name": "Black Oversized T-Shirt",
        "price": 29,
        "category": "men",
        "images": ["images/image1.jpg", "images/image1_same.jpg"],
        "sizes": ["S", "M", "L", "XL"],
        "colors": ["Black"],
        "description": "Relaxed oversized t-shirt.",
        "is_new": True,
        "on_sale": False
    },
    {
        "id": 2,
        "name": "White Oversized T-Shirt",
        "price": 59,
        "category": "men",
        "images": ["images/image2.jpg", "images/image2_same.jpg"],
        "sizes": ["M", "L", "XL"],
        "colors": ["White"],
        "description": "Minimal oversized tee.",
        "is_new": True,
        "on_sale": True
    },
    {
        "id": 3,
        "name": "Vintage Tee",
        "price": 49,
        "category": "men",
        "images": ["images/image3.jpg", "images/image3_same.jpg"],
        "sizes": ["S", "M", "L"],
        "colors": ["Cream"],
        "description": "Vintage style tee.",
        "is_new": False,
        "on_sale": False
    },
    {
        "id": 4,
        "name": "Pink Shirt",
        "price": 59,
        "category": "women",
        "images": ["images/image4.jpg", "images/image4_same.jpg"],
        "sizes": ["S", "M", "L"],
        "colors": ["Pink"],
        "description": "Elegant pink shirt.",
        "is_new": True,
        "on_sale": False
    },
    {
        "id": 5,
        "name": "Kids Hoodie",
        "price": 30,
        "category": "kids",
        "images": ["images/kid1.jpg", "images/kid1_same.jpg", "images/kid1_same_same.jpg"],
        "sizes": ["S", "M", "L"],
        "colors": ["Pink"],
        "description": "Bear Hoodie For Kids",
        "is_new": True,
        "on_sale": False
    }
]

def get_product(product_id):
    return next((p for p in products if p["id"] == product_id), None)

def get_current_user():
    user_id = session.get("user_id")

    if not user_id:
        return None

    
    return db.session.get(User, user_id)


def get_current_admin():
    user = get_current_user()

    if not user:
        return None

    if not user.is_admin:
        return None

    return user


# =========================
# CONTEXT PROCESSOR (CART COUNT)
# =========================
@app.context_processor
def inject_cart_count():
    current_user = get_current_user()

    if not current_user:
        return dict(cart_count=0)

    count = db.session.query(db.func.sum(CartItem.quantity)).filter_by(
        user_id=current_user.id
    ).scalar()

    return dict(cart_count=count or 0)

# =========================
# ROUTES
# =========================

@app.route("/")
def home():
    return render_template("main/index.html", products=products[:4], transparent_nav=True)

@app.route("/shop")
def shop():
    return render_template("shop/shop.html", products=products, page_title="Shop")

@app.route("/shop/men")
def men():
    return render_template("shop/shop.html",
        products=[p for p in products if p["category"] == "men"],
        page_title="Men"
    )

@app.route("/shop/women")
def women():
    return render_template("shop/shop.html",
        products=[p for p in products if p["category"] == "women"],
        page_title="Women"
    )

@app.route("/shop/kids")
def kids():
    return render_template("shop/shop.html",
        products=[p for p in products if p["category"] == "kids"],
        page_title="Kids"
    )

@app.route("/shop/new-arrivals")
def new_arrivals():
    return render_template("shop/shop.html",
        products=[p for p in products if p["is_new"]],
        page_title="New Arrivals"
    )

@app.route("/shop/sale")
def sale():
    return render_template("shop/shop.html",
        products=[p for p in products if p["on_sale"]],
        page_title="Sale"
    )

# =========================
# AUTH
# =========================

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        full_name = request.form.get("full_name")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm = request.form.get("confirm_password")

        if not full_name or not email or not password:
            flash("Fill all fields", "danger")
            return redirect(url_for("signup"))

        if password != confirm:
            flash("Passwords do not match", "danger")
            return redirect(url_for("signup"))

        if User.query.filter_by(email=email).first():
            flash("Email already exists", "danger")
            return redirect(url_for("signup"))

        user = User(
            full_name=full_name,
            email=email,
            password_hash=generate_password_hash(password)
        )

        db.session.add(user)
        db.session.commit()

        flash("Account created", "success")
        return redirect(url_for("login"))

    return render_template("auth/signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password_hash, password):
            flash("Invalid login", "danger")
            return redirect(url_for("login"))

        session["user_id"] = user.id
        session["user_name"] = user.full_name

        flash("Logged in successfully", "success")
        return redirect(url_for("home"))

    return render_template("auth/login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out", "success")
    return redirect(url_for("home"))

# =========================
# CART (DATABASE)
# =========================

@app.route("/cart")
def cart():
    current_user = get_current_user()

    if not current_user:
        session.clear()
        flash("Login first", "danger")
        return redirect(url_for("login"))

    items = CartItem.query.filter_by(user_id=current_user.id).all()
    total = sum(i.price * i.quantity for i in items)

    return render_template("shop/cart.html", cart=items, cart_total=total)




@app.route("/cart/add", methods=["POST"])
def add_to_cart():
    current_user = get_current_user()

    if not current_user:
        session.clear()
        flash("Login first", "danger")
        return redirect(url_for("login"))

    product_id = request.form.get("product_id", type=int)
    size = request.form.get("size")
    color = request.form.get("color")
    qty = request.form.get("quantity", type=int, default=1)

    product = get_product(product_id)

    if not product:
        flash("Product not found", "danger")
        return redirect(url_for("shop"))

    existing = CartItem.query.filter_by(
        user_id=current_user.id,
        product_id=product_id,
        size=size,
        color=color
    ).first()

    if existing:
        existing.quantity += qty
    else:
        item = CartItem(
            user_id=current_user.id,
            product_id=product["id"],
            product_name=product["name"],
            price=product["price"],
            image=product["images"][0],
            size=size,
            color=color,
            quantity=qty
        )
        db.session.add(item)

    db.session.commit()
    return redirect(url_for("cart"))


@app.route("/cart/increase", methods=["POST"])
def increase_cart_item():
    current_user = get_current_user()

    if not current_user:
        session.clear()
        flash("Login first", "danger")
        return redirect(url_for("login"))

    item_id = request.form.get("item_id", type=int)

    item = CartItem.query.filter_by(
        id=item_id,
        user_id=current_user.id
    ).first()

    if not item:
        flash("Cart item not found.", "warning")
        return redirect(url_for("cart"))

    item.quantity += 1
    db.session.commit()

    return redirect(url_for("cart"))

@app.route("/cart/decrease", methods=["POST"])
def decrease_cart_item():
    current_user = get_current_user()

    if not current_user:
        session.clear()
        flash("Login first", "danger")
        return redirect(url_for("login"))

    item_id = request.form.get("item_id", type=int)

    item = CartItem.query.filter_by(
        id=item_id,
        user_id=current_user.id
    ).first()

    if not item:
        flash("Cart item not found.", "warning")
        return redirect(url_for("cart"))

    if item.quantity > 1:
        item.quantity -= 1
    else:
        db.session.delete(item)

    db.session.commit()
    return redirect(url_for("cart"))


@app.route("/cart/remove", methods=["POST"])
def remove_cart_item():
    current_user = get_current_user()

    if not current_user:
        session.clear()
        flash("Login first", "danger")
        return redirect(url_for("login"))

    item_id = request.form.get("item_id", type=int)

    item = CartItem.query.filter_by(
        id=item_id,
        user_id=current_user.id
    ).first()

    if not item:
        flash("Cart item not found.", "warning")
        return redirect(url_for("cart"))

    db.session.delete(item)
    db.session.commit()

    return redirect(url_for("cart"))

@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    current_user = get_current_user()

    if not current_user:
        session.clear()
        flash("Login first", "danger")
        return redirect(url_for("login"))

    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()

    if not cart_items:
        flash("Your cart is empty.", "warning")
        return redirect(url_for("cart"))

    cart_total = sum(item.price * item.quantity for item in cart_items)

    if request.method == "POST":
        customer_name = request.form.get("customer_name")
        customer_email = request.form.get("customer_email")
        phone = request.form.get("phone")
        city = request.form.get("city")
        address = request.form.get("address")
        note = request.form.get("note")

        if not all([customer_name, customer_email, phone, city, address]):
            flash("Please fill in all required checkout fields.", "danger")
            return redirect(url_for("checkout"))

        order = Order(
            user_id=current_user.id,
            customer_name=customer_name,
            customer_email=customer_email,
            phone=phone,
            city=city,
            address=address,
            note=note,
            total_price=cart_total,
            status="Pending"
        )

        db.session.add(order)
        db.session.flush()

        for item in cart_items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item.product_id,
                product_name=item.product_name,
                price=item.price,
                image=item.image,
                size=item.size,
                color=item.color,
                quantity=item.quantity
            )
            db.session.add(order_item)

        for item in cart_items:
            db.session.delete(item)

        db.session.commit()

        flash("Order placed successfully.", "success")
        return redirect(url_for("order_success", order_id=order.id))

    return render_template("shop/checkout.html", cart=cart_items, cart_total=cart_total)


@app.route("/order/<int:order_id>")
def order_success(order_id):
    current_user = get_current_user()

    if not current_user:
        session.clear()
        flash("Login first", "danger")
        return redirect(url_for("login"))

    order = Order.query.filter_by(
        id=order_id,
        user_id=current_user.id
    ).first_or_404()
    
    return render_template("shop/order_success.html", order=order)

@app.route("/my-orders")
def my_orders():
    current_user = get_current_user()

    if not current_user:
        session.clear()
        flash("Login first", "danger")
        return redirect(url_for("login"))

    orders = Order.query.filter_by(
        user_id=current_user.id
    ).order_by(Order.created_at.desc()).all()

    return render_template("shop/my_orders.html", orders=orders) 


@app.route("/admin/orders")
def admin_orders():
    admin = get_current_admin()

    if not admin:
        flash("Access denied.", "danger")
        return redirect(url_for("home"))

    orders = Order.query.order_by(Order.created_at.desc()).all()

    return render_template("admin/orders.html", orders=orders)

@app.route("/admin/orders/<int:order_id>")
def admin_order_detail(order_id):
    admin = get_current_admin()

    if not admin:
        flash("Access denied.", "danger")
        return redirect(url_for("home"))

    order = Order.query.get_or_404(order_id)

    return render_template("admin/order_detail.html", order=order)


@app.route("/admin/orders/<int:order_id>/status", methods=["POST"])
def update_order_status(order_id):
    admin = get_current_admin()

    if not admin:
        flash("Access denied.", "danger")
        return redirect(url_for("home"))

    order = Order.query.get_or_404(order_id)

    new_status = request.form.get("status")

    allowed_statuses = ["Pending", "Processing", "Shipped", "Delivered", "Cancelled"]

    if new_status not in allowed_statuses:
        flash("Invalid status.", "danger")
        return redirect(url_for("admin_order_detail", order_id=order.id))

    order.status = new_status
    db.session.commit()

    flash("Order status updated.", "success")
    return redirect(url_for("admin_order_detail", order_id=order.id))

@app.context_processor
def inject_cart_count():
    current_user = get_current_user()

    if not current_user:
        return dict(cart_count=0)

    count = db.session.query(db.func.sum(CartItem.quantity)).filter_by(
        user_id=current_user.id
    ).scalar()

    return dict(cart_count=count or 0)


@app.context_processor
def inject_user():
    return dict(current_user=get_current_user())

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)