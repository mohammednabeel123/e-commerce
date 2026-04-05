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
        "images": [
            "images/image1.jpg",
            "images/image1_same.jpg"
        ]
    },
    {
        "id": 2,
        "name": "White Hoodie",
        "price": 59,
        "category": "men",
        "images": [
            "images/image2.jpg",
            "images/image2_same.jpg"
        ]
    },
    {
        "id": 2,
        "name": "White Hoodie",
        "price": 59,
        "category": "men",
        "images": [
            "images/image3.jpg",
            "images/image3_same.jpg"
        ]
    },
    {
        "id": 2,
        "name": "White Hoodie",
        "price": 59,
        "category": "men",
        "images": [
            "images/image2.jpg",
            "images/image2_same.jpg"
        ]
    },
    {
        "id": 2,
        "name": "White Hoodie",
        "price": 59,
        "category": "men",
        "images": [
            "images/image2.jpg",
            "images/image2_same.jpg"
        ]
    },
]

@app.route("/")
def home():
    featured_products = products[:4]
    return render_template("main/index.html", products=featured_products)

@app.route("/shop")
def shop():
    return render_template("shop/shop.html", products=products)

@app.route("/shop/<category>")
def shop_category(category):
    filtered_products = [p for p in products if p["category"] == category]
    return render_template("shop/shop.html", products=filtered_products, category=category)

if __name__ == "__main__":
    app.run(debug=True)