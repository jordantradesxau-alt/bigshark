from flask import *
import os
import psycopg2
import requests
import send_from_directory
from datetime import datetime

app = Flask(__name__)

# =========================
# ENV VARIABLES (RENDER)
# =========================
app.secret_key = os.getenv("SECRET_KEY", "dev_secret")

DATABASE_URL = os.getenv("DATABASE_URL")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")


# =========================
# DATABASE CONNECTION (SUPABASE POSTGRES)
# =========================
def get_db():
    return psycopg2.connect(DATABASE_URL, sslmode='require')

# =========================
# HOME
# =========================
@app.route('/')
def home():

    conn = get_db()
    cur = conn.cursor()

    cur.execute('SELECT * FROM store WHERE category=%s', ("offers",))
    data = cur.fetchall()

    cur.execute('SELECT * FROM store WHERE category=%s', ("other",))
    data1 = cur.fetchall()

    conn.close()

    return render_template(
        'index.html',
        category_offers=data,
        category_other=data1
    )


# =========================
# SIGNUP
# =========================
@app.route('/signup', methods=['POST', 'GET'])
def signup():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        location = request.form['location']

        if len(password) < 8:
            return render_template('index.html', error="PASSWORD MUST BE 8+ CHARACTERS")

        conn = get_db()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO users(username, password, email, location)
            VALUES (%s, %s, %s, %s)
        """, (username, password, email, location))

        conn.commit()
        conn.close()

        return render_template('index.html', success="SIGNUP SUCCESSFUL")

    return render_template('index.html')


# =========================
# LOGIN
# =========================
@app.route('/login', methods=['POST', 'GET'])
def login():

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        conn = get_db()
        cur = conn.cursor()

        cur.execute("""
            SELECT * FROM users WHERE email=%s AND password=%s
        """, (email, password))

        user = cur.fetchone()
        conn.close()

        if user is None:
            return render_template('index.html', error="INVALID CREDENTIALS")

        session['key'] = user[0]  # username or id depending on schema

        return redirect('/')

    return render_template('index.html')


# =========================
# LOGOUT
# =========================
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


# =========================
# MEN
# =========================
@app.route('/mensattire')
def mensattire():

    conn = get_db()
    cur = conn.cursor()

    cur.execute('SELECT * FROM store WHERE category=%s', ("menstops",))
    data = cur.fetchall()

    cur.execute('SELECT * FROM store WHERE category=%s', ("mensbt",))
    data1 = cur.fetchall()

    cur.execute('SELECT * FROM store WHERE category=%s', ("other",))
    data2 = cur.fetchall()

    conn.close()

    return render_template(
        'mensattire.html',
        category_menstops=data,
        category_mensbt=data1,
        category_other=data2
    )


# =========================
# ACCESSORIES
# =========================
@app.route('/accesories')
def accesories():

    conn = get_db()
    cur = conn.cursor()

    cur.execute('SELECT * FROM store WHERE category=%s', ("accesories",))
    data = cur.fetchall()

    cur.execute('SELECT * FROM store WHERE category=%s', ("other",))
    data1 = cur.fetchall()

    conn.close()

    return render_template(
        'accesories.html',
        category_accesories=data,
        category_other=data1
    )


# =========================
# WOMEN
# =========================
@app.route('/womensattire')
def womensattire():

    conn = get_db()
    cur = conn.cursor()

    cur.execute('SELECT * FROM store WHERE category=%s', ("womenstops",))
    data = cur.fetchall()

    cur.execute('SELECT * FROM store WHERE category=%s', ("womensbt",))
    data1 = cur.fetchall()

    cur.execute('SELECT * FROM store WHERE category=%s', ("other",))
    data2 = cur.fetchall()

    conn.close()

    return render_template(
        'womensattire.html',
        category_womenstops=data,
        category_womensbt=data1,
        category_other=data2
    )


# =========================
# SINGLE ITEM
# =========================
@app.route('/singleitem/<item>')
def singleitem(item):

    conn = get_db()
    cur = conn.cursor()

    cur.execute('SELECT * FROM store WHERE item=%s', (item,))
    shop = cur.fetchone()

    cur.execute('SELECT * FROM store WHERE category=%s LIMIT 10', ("other",))
    others = cur.fetchall()

    conn.close()

    return render_template('singleitem.html', item=shop, category_other=others)


# =========================
# STATIC PAGES
# =========================
@app.route('/wellnesstips')
def wellnesstips():
    return render_template('wellnesstips.html')


@app.route('/healthproducts')
def healthproducts():
    return render_template('healthproducts.html')


@app.route('/robots.txt')
def robots():
    return send_from_directory(app.root_path, 'robots.txt')

@app.route('/sitemap.xml')
def sitemap():
    return send_from_directory(app.root_path, 'sitemap.xml')


# =========================
# UPLOAD (SUPABASE STORAGE READY)
# =========================
@app.route('/upload', methods=['POST', 'GET'])
def upload():

    if request.method == 'POST':

        item = request.form['item']
        description = request.form['description']
        currentp = request.form['currentp']
        category = request.form['category']
        image = request.files['image']

        # =========================
        # SUPABASE STORAGE UPLOAD
        # =========================
        filename = image.filename

        upload_url = f"{SUPABASE_URL}/storage/v1/object/store-images/{filename}"

        headers = {
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/octet-stream"
        }

        requests.post(upload_url, headers=headers, data=image.read())

        image_url = f"{SUPABASE_URL}/storage/v1/object/public/store-images/{filename}"

        # =========================
        # SAVE TO DB
        # =========================
        conn = get_db()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO store(item, description, currentp, category, image)
            VALUES (%s, %s, %s, %s, %s)
        """, (item, description, currentp, category, image_url))

        conn.commit()
        conn.close()

        return render_template('upload.html', message="UPLOADED TO SUPABASE")

    return render_template('upload.html')

@app.context_processor
def cart_count():

    cart = session.get('cart', {})

    count = sum(item['qty'] for item in cart.values())

    return dict(cart_count=count)

@app.route('/cart')
def cart():

    cart_items = session.get('cart', {})

    total = 0

    for item in cart_items.values():
        total += float(item['price']) * int(item['qty'])

    return render_template(
        'cart.html',
        cart_items=cart_items,
        total=total
    )


@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():

    item_name = request.form['item']
    price = request.form['price']
    image = request.form['image']

    qty = int(request.form.get('qty', 1))

    cart = session.get('cart', {})

    if item_name in cart:
        cart[item_name]['qty'] += qty
    else:
        cart[item_name] = {
            'name': item_name,
            'price': float(price),
            'image': image,
            'qty': qty
        }

    session['cart'] = cart

    return redirect('/cart')


@app.route('/remove_from_cart/<item_name>')
def remove_from_cart(item_name):

    cart = session.get('cart', {})

    if item_name in cart:
        del cart[item_name]

    session['cart'] = cart

    return redirect('/cart')


@app.route('/checkout')
def checkout():

    cart = session.get('cart', {})

    total = sum(
        float(item['price']) * int(item['qty'])
        for item in cart.values()
    )

    return render_template(
        'checkout.html',
        cart_items=cart,
        total=total
    )


@app.route('/place_order', methods=['POST'])
def place_order():

    customer_name = request.form['customer_name']
    phone = request.form['phone']
    email = request.form['email']
    location = request.form['location']
    address = request.form['address']

    cart = session.get('cart', {})

    if not cart:
        return redirect('/cart')

    total = sum(
        float(item['price']) * int(item['qty'])
        for item in cart.values()
    )

    order_number = "BS" + datetime.now().strftime("%Y%m%d%H%M%S")

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO orders
        (
            order_number,
            customer_name,
            phone,
            email,
            location,
            address,
            total_amount,
            status
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        RETURNING id
    """, (
        order_number,
        customer_name,
        phone,
        email,
        location,
        address,
        total,
        'Pending'
    ))

    order_id = cur.fetchone()[0]

    for item in cart.values():

        subtotal = (
            float(item['price']) *
            int(item['qty'])
        )

        cur.execute("""
            INSERT INTO order_items
            (
                order_id,
                product_name,
                quantity,
                unit_price,
                subtotal
            )
            VALUES (%s,%s,%s,%s,%s)
        """, (
            order_id,
            item['name'],
            item['qty'],
            item['price'],
            subtotal
        ))

    conn.commit()
    conn.close()

    session.pop('cart', None)

    return redirect(
        f'/order_success/{order_number}'
    )


@app.route('/order_success/<order_number>')
def order_success(order_number):

    return render_template(
        'order_success.html',
        order_number=order_number
    )

# =========================
# RUN
# =========================
if __name__ == '__main__':
    app.run(debug=True, port=7070)
