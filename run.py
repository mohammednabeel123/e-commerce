from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(
    __name__,
    template_folder="app/templates",
    static_folder="app/static"
)
app.secret_key = "dev-secret-key-change-this-later"

products = [
    {
        "id": 1,
        "name": "Black Oversized T-Shirt",
        "price": 29,
        "category": "men",
        "images": ["images/image1.jpg", "images/image1_same.jpg"],
        "sizes": ["S", "M", "L", "XL"],
        "colors": ["Black"],
        "description": "Relaxed oversized t-shirt with a clean everyday silhouette.",
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
        "description": "Minimal oversized tee designed for a modern streetwear fit.",
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
        "description": "Soft vintage-inspired tee with a timeless silhouette.",
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
        "description": "Elegant pink shirt with a refined minimal finish.",
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

def get_product_by_id(product_id):
    return next((product for product in products if product["id"] == product_id), None)

@app.route("/cart/add", methods=["POST"])
def add_to_cart():
    product_id = request.form.get("product_id", type=int)
    size = request.form.get("size")
    color = request.form.get("color")
    quantity = request.form.get("quantity", type=int, default=1)

    product = get_product_by_id(product_id)

    if not product:
        return redirect(url_for("shop"))

    if not size or size not in product["sizes"]:
        return redirect(url_for("shop"))

    if not color or color not in product["colors"]:
        return redirect(url_for("shop"))

    if quantity < 1:
        quantity = 1

    cart = session.get("cart", [])

    existing_item = next(
        (
            item for item in cart
            if item["product_id"] == product_id
            and item["size"] == size
            and item["color"] == color
        ),
        None
    )

    if existing_item:
        existing_item["quantity"] += quantity
    else:
        cart.append({
            "product_id": product["id"],
            "name": product["name"],
            "price": product["price"],
            "image": product["images"][0],
            "size": size,
            "color": color,
            "quantity": quantity
        })
    session["cart"] = cart
    return redirect(url_for("shop"))


@app.context_processor
def inject_cart_count():
    cart = session.get("cart", [])
    cart_count = sum(item["quantity"] for item in cart)
    return dict(cart_count=cart_count)



@app.route("/")
def home():
    featured_products = products[:4]
    return render_template("main/index.html", products=featured_products, transparent_nav=True)

@app.route("/shop")
def shop():
    return render_template("shop/shop.html", products=products, page_title="Shop", transparent_nav=False)

@app.route("/shop/men")
def men():
    filtered_products = [p for p in products if p["category"] == "men"]
    return render_template("shop/shop.html", products=filtered_products, page_title="Men")

@app.route("/shop/women")
def women():
    filtered_products = [p for p in products if p["category"] == "women"]
    return render_template("shop/shop.html", products=filtered_products, page_title="Women")

@app.route("/shop/kids")
def kids():
    filtered_products = [p for p in products if p["category"] == "kids"]
    return render_template("shop/shop.html", products=filtered_products, page_title="Kids")

@app.route("/shop/new-arrivals")
def new_arrivals():
    filtered_products = [p for p in products if p["is_new"]]
    return render_template("shop/shop.html", products=filtered_products, page_title="New Arrivals")

@app.route("/shop/sale")
def sale():
    filtered_products = [p for p in products if p["on_sale"]]
    return render_template("shop/shop.html", products=filtered_products, page_title="Sale")

@app.route("/login")
def login():
    return render_template("auth/login.html", transparent_nav=False)

@app.route("/signup")
def signup():
    return render_template("auth/signup.html", transparent_nav=False)

@app.route("/reset-password")
def reset_password():
    return render_template("auth/reset.html", transparent_nav=False)


@app.route("/cart")
def cart():
    cart_items = session.get("cart", [])
    cart_total = sum(item["price"] * item["quantity"] for item in cart_items)

    return render_template(
        "shop/cart.html",
        cart=cart_items,
        cart_total=cart_total,
        transparent_nav=False
    )

@app.route("/cart/increase", methods=["POST"])
def increase_cart_item():
    product_id = request.form.get("product_id", type=int)
    size = request.form.get("size")
    color = request.form.get("color")

    cart = session.get("cart", [])

    for item in cart:
        if (
            item["product_id"] == product_id
            and item["size"] == size
            and item["color"] == color
        ):
            item["quantity"] += 1
            break

    session["cart"] = cart
    return redirect(url_for("cart")) 

@app.route("/cart/decrease", methods=["POST"])
def decrease_cart_item():
    product_id = request.form.get("product_id", type=int)
    size = request.form.get("size")
    color = request.form.get("color")

    cart = session.get("cart", [])

    for item in cart:
        if (item["product_id"] == product_id
            and item["size"] == size
            and item["color"] == color
        ):
            item["quantity"] -= 1

            if item["quantity"] <= 0:
                cart.remove(item)
            break

    session["cart"] = cart
    return redirect(url_for("cart"))

@app.route("/cart/remove", methods=["POST"])
def remove_cart_item():
    product_id = request.form.get("product_id", type=int)
    size = request.form.get("size")
    color = request.form.get("color")

    cart = session.get("cart", [])

    cart = [
        item for item in cart
        if not (
            item["product_id"] == product_id
            and item["size"] == size
            and item["color"] == color
        )
    ]

    session["cart"] = cart
    return redirect(url_for("cart"))

if __name__ == "__main__":
    app.run(debug=True)