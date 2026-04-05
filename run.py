from flask import Flask, render_template

app = Flask(
    __name__,
    template_folder="app/templates",
    static_folder="app/static"
)

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
    }
]

@app.route("/")
def home():
    featured_products = products[:4]
    return render_template("main/index.html", products=featured_products)

@app.route("/shop")
def shop():
    return render_template("shop/shop.html", products=products, page_title="Shop")

@app.route("/shop/men")
def men():
    filtered_products = [p for p in products if p["category"] == "men"]
    return render_template("shop/shop.html", products=filtered_products, page_title="Men")

@app.route("/shop/women")
def women():
    filtered_products = [p for p in products if p["category"] == "women"]
    return render_template("shop/shop.html", products=filtered_products, page_title="Women")

@app.route("/shop/new-arrivals")
def new_arrivals():
    filtered_products = [p for p in products if p["is_new"]]
    return render_template("shop/shop.html", products=filtered_products, page_title="New Arrivals")

@app.route("/shop/sale")
def sale():
    filtered_products = [p for p in products if p["on_sale"]]
    return render_template("shop/shop.html", products=filtered_products, page_title="Sale")

if __name__ == "__main__":
    app.run(debug=True)