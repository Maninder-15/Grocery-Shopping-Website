from flask import Flask, render_template, request, redirect, session, flash
from flask_mysqldb import MySQL
from config import Config
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = "freshmart_secret_key"

mysql = MySQL(app)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/products")
def products():

    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT
        product_id,
        product_name,
        description,
        price,
        stock,
        image
        FROM products
    """)

    products = cur.fetchall()
    cur.close()

    return render_template("products.html", products=products)

@app.route("/add_to_cart/<int:product_id>", methods=["POST"])
def add_to_cart(product_id):

    if "user_id" not in session:
        return redirect("/login")

    customer_id = session["user_id"]

    cur = mysql.connection.cursor()

    cur.execute(
        """
        SELECT *
        FROM cart
        WHERE customer_id=%s
        AND product_id=%s
        """,
        (customer_id, product_id)
    )

    item = cur.fetchone()

    if item:

        cur.execute(
            """
            UPDATE cart
            SET quantity=quantity+1
            WHERE customer_id=%s
            AND product_id=%s
            """,
            (customer_id, product_id)
        )

    else:

        cur.execute(
            """
            INSERT INTO cart(customer_id,product_id,quantity)
            VALUES(%s,%s,%s)
            """,
            (customer_id, product_id, 1)
        )

    mysql.connection.commit()
    cur.close()

    flash("Product added to cart.")

    return redirect("/products")


@app.route("/cart")
def cart():

    if "user_id" not in session:
        return redirect("/login")

    customer_id = session["user_id"]

    cur = mysql.connection.cursor()

    cur.execute(
        """
        SELECT
        cart.cart_id,
        products.product_id,
        products.product_name,
        products.price,
        products.image,
        cart.quantity
        FROM cart
        INNER JOIN products
        ON cart.product_id=products.product_id
        WHERE cart.customer_id=%s
        """,
        (customer_id,)
    )

    cart_items = cur.fetchall()

    cur.close()

    total = 0

    for item in cart_items:
        total += item["price"] * item["quantity"]

    return render_template(
        "cart.html",
        cart_items=cart_items,
        total=total
    )


@app.route("/remove_from_cart/<int:cart_id>")
def remove_from_cart(cart_id):

    cur = mysql.connection.cursor()

    cur.execute(
        """
        DELETE FROM cart
        WHERE cart_id=%s
        AND customer_id=%s
        """,
        (cart_id,)
    )

    mysql.connection.commit()
    cur.close()

    return redirect("/cart")


@app.route("/update_quantity/<int:cart_id>/<string:action>")
def update_quantity(cart_id, action):

    cur = mysql.connection.cursor()

    if action == "increase":

        cur.execute(
            """
            UPDATE cart
            SET quantity=quantity+1
            WHERE cart_id=%s
            """,
            (cart_id,)
        )

    elif action == "decrease":

        cur.execute(
            """
            UPDATE cart
            SET quantity=quantity-1
            WHERE cart_id=%s
            AND quantity>1
            """,
            (cart_id,)
        )

    mysql.connection.commit()
    cur.close()

    return redirect("/cart")


@app.route("/buy_now/<int:product_id>", methods=["POST"])
def buy_now(product_id):

    if "user_id" not in session:
        return redirect("/login")

    return redirect("/checkout")

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        fullname = request.form["fullname"]
        email = request.form["email"]
        phone = request.form["phone"]
        address = request.form["address"]
        password = generate_password_hash(request.form["password"])

        cur = mysql.connection.cursor()

        cur.execute("""
            SELECT customer_id
            FROM customers
            WHERE email=%s
        """, (email,))

        existing = cur.fetchone()

        if existing:
            cur.close()
            flash("Email already exists.")
            return redirect("/register")

        cur.execute("""
            INSERT INTO customers
            (full_name,email,phone,password,address)
            VALUES(%s,%s,%s,%s,%s)
        """, (
            fullname,
            email,
            phone,
            password,
            address
        ))

        mysql.connection.commit()

        cur.close()

        flash("Registration Successful")

        return redirect("/login")

    return render_template("register.html")

@app.route("/login", methods=["GET","POST"])
def login():

    if request.method=="POST":

        email=request.form["email"]
        password=request.form["password"]

        cur=mysql.connection.cursor()

        cur.execute("""
            SELECT *
            FROM customers
            WHERE email=%s
        """,(email,))

        user=cur.fetchone()

        cur.close()

        if user:

            if check_password_hash(user["password"],password):

                session["user_id"]=user["customer_id"]
                session["user_name"]=user["full_name"]

                return redirect("/products")

        flash("Invalid Email or Password")

    return render_template("login.html")

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")

@app.route("/checkout", methods=["GET", "POST"])
def checkout():

    if "user_id" not in session:
        return redirect("/login")

    customer_id = session["user_id"]

    cur = mysql.connection.cursor()

    if request.method == "POST":

        fullname = request.form["fullname"]
        email = request.form["email"]
        phone = request.form["phone"]
        address = request.form["address"]
        payment = request.form["payment"]

        cur.execute("""
            SELECT
            cart.product_id,
            cart.quantity,
            products.price
            FROM cart
            INNER JOIN products
            ON cart.product_id = products.product_id
            WHERE cart.customer_id=%s
        """,(customer_id,))

        cart_items = cur.fetchall()

        total = 0

        for item in cart_items:
            total += item["price"] * item["quantity"]

        total += 50

        order_date = datetime.now()

        cur.execute("""
            INSERT INTO orders
            (
                customer_id,
                customer_name,
                email,
                phone,
                address,
                payment_method,
                total_amount,
                order_date,
                order_status
            )
            VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """,
        (
            customer_id,
            fullname,
            email,
            phone,
            address,
            payment,
            total,
            order_date,
            "Pending"
        ))

        mysql.connection.commit()

        order_id = cur.lastrowid

        for item in cart_items:

            cur.execute("""
                INSERT INTO order_items
                (
                    order_id,
                    product_id,
                    quantity,
                    price
                )
                VALUES(%s,%s,%s,%s)
            """,
            (
                order_id,
                item["product_id"],
                item["quantity"],
                item["price"]
            ))

            cur.execute("""
                UPDATE products
                SET stock = stock - %s
                WHERE product_id=%s
            """,
            (
                item["quantity"],
                item["product_id"]
            ))

        cur.execute("""
            DELETE FROM cart
            WHERE customer_id=%s
        """,(customer_id,))

        mysql.connection.commit()

        cur.close()

        flash("Order Placed Successfully")

        return redirect("/orders")

    cur.execute("""
        SELECT
        cart.product_id,
        products.product_name,
        cart.quantity,
        products.price
        FROM cart
        INNER JOIN products
        ON cart.product_id=products.product_id
        WHERE customer_id=%s
    """,(customer_id,))

    cart_items = cur.fetchall()

    cur.close()

    total = 0

    for item in cart_items:
        total += item["price"] * item["quantity"]

    return render_template(
        "checkout.html",
        cart_items=cart_items,
        total=total
    )

@app.route("/orders")
def orders():

    if "user_id" not in session:
        return redirect("/login")

    customer_id = session["user_id"]

    cur = mysql.connection.cursor()

    cur.execute("""
            SELECT
        o.order_id,
        c.full_name,
        o.order_date,
        o.payment_method,
        o.total_amount,
        o.order_status
    FROM orders o
    JOIN customers c
        ON o.customer_id = c.customer_id
    ORDER BY o.order_date DESC
    LIMIT 10""")
    orders = cur.fetchall()

    order_data = []

    for order in orders:

        cur.execute("""
            SELECT
            products.product_name,
            order_items.quantity,
            order_items.price
            FROM order_items
            INNER JOIN products
            ON order_items.product_id=products.product_id
            WHERE order_items.order_id=%s
        """,(order["order_id"],))

        items = cur.fetchall()

        order_data.append({
            "order":order,
            "items":items
        })

    cur.close()

    return render_template(
        "orders.html",
        order_data=order_data
    )

@app.route("/payment")
def payment():
    return render_template("payment.html")


@app.route("/profile")
def profile():

    if "user_id" not in session:
        return redirect("/login")

    return render_template("profile.html")

@app.route("/admin")
def admin():
    return redirect("/admin/dashboard")

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        cur = mysql.connection.cursor()

        cur.execute("SELECT DATABASE() AS db")
        print("Database:", cur.fetchone())

        cur.execute("SELECT * FROM admin")
        print("All Admin Records:", cur.fetchall())

        cur.execute("""
            SELECT *
            FROM admin
            WHERE username=%s
            """, (username,))

        admin = cur.fetchone()

        print("Selected Admin:", admin)

        print("Database Row:", admin)
        print("Entered Username:", username)
        print("Entered Password:", password)

        cur.close()

        if admin:

            print("Stored Hash:", admin["password"])
            print("Password Match:", check_password_hash(admin["password"], password))

            if check_password_hash(admin["password"], password):
                session["admin_id"] = admin["admin_id"]
                session["admin_name"] = admin["username"]

                return redirect("/admin/dashboard")

        flash("Invalid Username or Password")

    return render_template("admin/login.html")


@app.route("/admin/dashboard")
def admin_dashboard():

    if "admin_id" not in session:
        return redirect("/admin/login")

    cur = mysql.connection.cursor()

    cur.execute("SELECT COUNT(*) AS total FROM customers")
    total_customers = cur.fetchone()["total"]

    cur.execute("SELECT COUNT(*) AS total FROM products")
    total_products = cur.fetchone()["total"]

    cur.execute("SELECT COUNT(*) AS total FROM orders")
    total_orders = cur.fetchone()["total"]

    cur.execute("""
        SELECT
        IFNULL(SUM(total_amount),0) AS revenue
        FROM orders
    """)
    total_revenue = cur.fetchone()["revenue"]

    cur.execute("""
        SELECT
        order_id,
        customer_name,
        order_date,
        payment_method,
        total_amount,
        order_status
        FROM orders
        ORDER BY order_date DESC
        LIMIT 10
    """)

    recent_orders = cur.fetchall()

    cur.close()

    return render_template(
        "admin/dashboard.html",
        total_customers=total_customers,
        total_products=total_products,
        total_orders=total_orders,
        total_revenue=total_revenue,
        recent_orders=recent_orders
    )

@app.route("/admin/products")
def admin_products():

    if "admin_id" not in session:
        return redirect("/admin/login")

    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT
        p.product_id,
        p.product_name,
        c.category_name,
        p.price,
        p.stock,
        p.image
        FROM products p
        LEFT JOIN categories c
        ON p.category_id = c.category_id
        ORDER BY p.product_id DESC
    """)

    products = cur.fetchall()

    cur.close()

    return render_template(
        "admin/products.html",
        products=products
    )


@app.route("/admin/add_product", methods=["GET","POST"])
def add_product():

    if "admin_id" not in session:
        return redirect("/admin/login")

    cur = mysql.connection.cursor()

    if request.method == "POST":

        product_name = request.form["product_name"]
        category_id = request.form["category_id"]
        description = request.form["description"]
        price = request.form["price"]
        stock = request.form["stock"]
        image = request.form["image"]

        cur.execute("""
            INSERT INTO products
            (
                category_id,
                product_name,
                description,
                price,
                stock,
                image
            )
            VALUES(%s,%s,%s,%s,%s,%s)
        """,
        (
            category_id,
            product_name,
            description,
            price,
            stock,
            image
        ))

        mysql.connection.commit()

        cur.close()

        flash("Product Added Successfully")

        return redirect("/admin/products")

    cur.execute("""
        SELECT
        category_id,
        category_name
        FROM categories
        ORDER BY category_name
    """)

    categories = cur.fetchall()

    cur.close()

    return render_template(
        "admin/add_product.html",
        categories=categories
    )


@app.route("/admin/edit_product/<int:product_id>", methods=["GET","POST"])
def edit_product(product_id):

    if "admin_id" not in session:
        return redirect("/admin/login")

    cur = mysql.connection.cursor()

    if request.method == "POST":

        product_name = request.form["product_name"]
        category_id = request.form["category_id"]
        description = request.form["description"]
        price = request.form["price"]
        stock = request.form["stock"]
        image = request.form["image"]

        cur.execute("""
            UPDATE products
            SET
            category_id=%s,
            product_name=%s,
            description=%s,
            price=%s,
            stock=%s,
            image=%s
            WHERE product_id=%s
        """,
        (
            category_id,
            product_name,
            description,
            price,
            stock,
            image,
            product_id
        ))

        mysql.connection.commit()

        flash("Product Updated Successfully")

        return redirect("/admin/products")

    cur.execute("""
        SELECT *
        FROM products
        WHERE product_id=%s
    """,(product_id,))

    product = cur.fetchone()

    cur.execute("""
        SELECT
        category_id,
        category_name
        FROM categories
        ORDER BY category_name
    """)

    categories = cur.fetchall()

    cur.close()

    return render_template(
        "admin/edit_product.html",
        product=product,
        categories=categories
    )

@app.route("/admin/delete_product/<int:product_id>")
def delete_product(product_id):

    if "admin_id" not in session:
        return redirect("/admin/login")

    cur = mysql.connection.cursor()

    cur.execute("""
        DELETE FROM products
        WHERE product_id=%s
    """,(product_id,))

    mysql.connection.commit()

    cur.close()

    flash("Product Deleted Successfully")

    return redirect("/admin/products")

@app.route("/admin/categories")
def admin_categories():

    if "admin_id" not in session:
        return redirect("/admin/login")

    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT
        category_id,
        category_name
        FROM categories
        ORDER BY category_name
    """)

    categories = cur.fetchall()

    cur.close()

    return render_template(
        "admin/categories.html",
        categories=categories
    )


@app.route("/admin/add_category", methods=["POST"])
def add_category():

    if "admin_id" not in session:
        return redirect("/admin/login")

    category_name = request.form["category_name"]

    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT category_id
        FROM categories
        WHERE category_name=%s
    """,(category_name,))

    category = cur.fetchone()

    if category:

        cur.close()

        flash("Category already exists.")

        return redirect("/admin/categories")

    cur.execute("""
        INSERT INTO categories(category_name)
        VALUES(%s)
    """,(category_name,))

    mysql.connection.commit()

    cur.close()

    flash("Category Added Successfully")

    return redirect("/admin/categories")


@app.route("/admin/edit_category/<int:category_id>", methods=["POST"])
def edit_category(category_id):

    if "admin_id" not in session:
        return redirect("/admin/login")

    category_name = request.form["category_name"]

    cur = mysql.connection.cursor()

    cur.execute("""
        UPDATE categories
        SET category_name=%s
        WHERE category_id=%s
    """,
    (
        category_name,
        category_id
    ))

    mysql.connection.commit()

    cur.close()

    flash("Category Updated Successfully")

    return redirect("/admin/categories")


@app.route("/admin/delete_category/<int:category_id>")
def delete_category(category_id):

    if "admin_id" not in session:
        return redirect("/admin/login")

    cur = mysql.connection.cursor()

    cur.execute("""
        DELETE FROM categories
        WHERE category_id=%s
    """,(category_id,))

    mysql.connection.commit()

    cur.close()

    flash("Category Deleted Successfully")

    return redirect("/admin/categories")

@app.route("/admin/customers")
def admin_customers():

    if "admin_id" not in session:
        return redirect("/admin/login")

    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT
        customer_id,
        full_name,
        email,
        phone,
        address
        FROM customers
        ORDER BY customer_id DESC
    """)

    customers = cur.fetchall()

    cur.close()

    return render_template(
        "admin/customers.html",
        customers=customers
    )


@app.route("/admin/delete_customer/<int:customer_id>")
def delete_customer(customer_id):

    if "admin_id" not in session:
        return redirect("/admin/login")

    cur = mysql.connection.cursor()

    cur.execute("""
        DELETE FROM customers
        WHERE customer_id=%s
    """,(customer_id,))

    mysql.connection.commit()

    cur.close()

    flash("Customer Deleted Successfully")

    return redirect("/admin/customers")

@app.route("/admin/orders")
def admin_orders():

    if "admin_id" not in session:
        return redirect("/admin/login")

    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT
        order_id,
        customer_name,
        email,
        phone,
        payment_method,
        total_amount,
        order_date,
        order_status
        FROM orders
        ORDER BY order_date DESC
    """)

    orders = cur.fetchall()

    cur.close()

    return render_template(
        "admin/orders.html",
        orders=orders
    )


@app.route("/admin/update_order/<int:order_id>", methods=["POST"])
def update_order(order_id):

    if "admin_id" not in session:
        return redirect("/admin/login")

    status = request.form["status"]

    cur = mysql.connection.cursor()

    cur.execute("""
        UPDATE orders
        SET order_status=%s
        WHERE order_id=%s
    """,
    (
        status,
        order_id
    ))

    mysql.connection.commit()

    cur.close()

    flash("Order Status Updated Successfully")

    return redirect("/admin/orders")


@app.route("/admin/delete_order/<int:order_id>")
def delete_order(order_id):

    if "admin_id" not in session:
        return redirect("/admin/login")

    cur = mysql.connection.cursor()

    cur.execute("""
        DELETE FROM order_items
        WHERE order_id=%s
    """,(order_id,))

    cur.execute("""
        DELETE FROM orders
        WHERE order_id=%s
    """,(order_id,))

    mysql.connection.commit()

    cur.close()

    flash("Order Deleted Successfully")

    return redirect("/admin/orders")

@app.route("/admin/logout")
def admin_logout():

    session.pop("admin_id", None)
    session.pop("admin_name", None)

    return redirect("/admin/login")

if __name__=="__main__":
    app.run(debug=True)
    