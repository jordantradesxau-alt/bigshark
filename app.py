from flask import *
import os
import psycopg2
import requests

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


# =========================
# RUN
# =========================
if __name__ == '__main__':
    app.run(debug=True, port=7070)