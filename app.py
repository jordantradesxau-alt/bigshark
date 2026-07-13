"""
Big Shark Apparel - Complete Flask Application
E-Commerce Store with Admin Dashboard
Deployment: Render
Database: PostgreSQL (Supabase)
Storage: Supabase Storage
"""

import os
import uuid
import requests
from datetime import datetime
from functools import wraps
from flask import *
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2
import psycopg2.extras

# ============================================================
# APPLICATION INITIALIZATION
# ============================================================

app = Flask(__name__)

# Environment Configuration
app.secret_key = os.getenv("SECRET_KEY", "dev_secret_key_change_in_production")
DATABASE_URL = os.getenv("DATABASE_URL")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_db():
    """Create and return a PostgreSQL database connection."""
    try:
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        conn.cursor_factory = psycopg2.extras.RealDictCursor
        return conn
    except psycopg2.OperationalError as e:
        print(f"Database connection error: {e}")
        return None

def close_db(conn, cursor=None):
    """Safely close database connection and cursor."""
    try:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    except Exception as e:
        print(f"Error closing connection: {e}")

# ============================================================
# IMAGE UPLOAD HELPER
# ============================================================

def upload_image(file, folder='products'):
    """Upload an image to Supabase Storage and return the public URL."""
    if not file or not file.filename:
        return None
    
    try:
        # Get file extension
        ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else 'jpg'
        
        # Generate unique filename
        filename = f"{folder}/{uuid.uuid4().hex}.{ext}"
        
        # Supabase Storage endpoints
        upload_url = f"{SUPABASE_URL}/storage/v1/object/store-images/{filename}"
        
        headers = {
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "apikey": SUPABASE_KEY,
            "Content-Type": "application/octet-stream"
        }
        
        response = requests.post(upload_url, headers=headers, data=file.read())
        
        if response.status_code not in [200, 201]:
            print(f"Upload failed: {response.text}")
            return None
        
        # Generate public URL
        image_url = f"{SUPABASE_URL}/storage/v1/object/public/store-images/{filename}"
        return image_url
        
    except Exception as e:
        print(f"Upload error: {e}")
        return None
        
        image_url = f"{SUPABASE_URL}/storage/v1/object/public/store-images/{filename}"
        return image_url
    except Exception as e:
        print(f"Upload error: {e}")
        return None
        
        # Get public URL
        image_url = f"{SUPABASE_URL}/storage/v1/object/public/store-images/{filename}"
        return image_url
    except Exception as e:
        print(f"Upload error: {e}")
        return None

# ============================================================
# AUTHENTICATION DECORATORS
# ============================================================

def login_required(f):
    """Decorator to require admin login."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            flash('Please login to access the admin panel.', 'warning')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

def user_login_required(f):
    """Decorator to require user login."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to view special offers.', 'warning')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# ============================================================
# CONTEXT PROCESSOR
# ============================================================

@app.context_processor
def cart_count():
    """Make cart count available to all templates."""
    cart = session.get('cart', {})
    count = sum(item.get('qty', 0) for item in cart.values())
    return dict(cart_count=count)

# ============================================================
# HOME PAGE
# ============================================================

@app.route('/')
def index():
    conn = get_db()
    if not conn:
        return render_template('index.html', 
                             offers=[],
                             other_products=[],
                             featured_reviews=[],
                             carousel_images=[])

    try:
        cursor = conn.cursor()

        # Get offers
        cursor.execute("SELECT * FROM inventory WHERE category = 'offers' AND status = 'active' ORDER BY created_at DESC LIMIT 10")
        offers = cursor.fetchall()

        # Get other products
        cursor.execute("SELECT * FROM inventory WHERE category != 'offers' AND status = 'active' ORDER BY created_at DESC LIMIT 20")
        other_products = cursor.fetchall()

        # Get featured reviews
        cursor.execute("SELECT * FROM customer_reviews WHERE status = 'approved' AND is_featured = true ORDER BY created_at DESC LIMIT 3")
        featured_reviews = cursor.fetchall()

        # Get carousel images from site_settings
        cursor.execute("SELECT setting_value FROM site_settings WHERE setting_key = 'carousel_images'")
        carousel_result = cursor.fetchone()
        carousel_images = []
        if carousel_result:
            carousel_images = carousel_result['setting_value'].split(',')

        close_db(conn, cursor)

        return render_template('index.html',
                             offers=offers,
                             other_products=other_products,
                             featured_reviews=featured_reviews,
                             carousel_images=carousel_images)
    except Exception as e:
        print(f"Index error: {e}")
        close_db(conn)
        return render_template('index.html', offers=[], other_products=[], featured_reviews=[], carousel_images=[])



# ============================================================
# CATEGORY PAGES
# ============================================================

@app.route('/mensattire')
def mensattire():
    conn = get_db()
    if not conn:
        return render_template('mensattire.html', menstops=[], mensbt=[], other=[])

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM inventory WHERE category = 'menstops' AND status = 'active' ORDER BY created_at DESC")
        menstops = cursor.fetchall()
        
        cursor.execute("SELECT * FROM inventory WHERE category = 'mensbt' AND status = 'active' ORDER BY created_at DESC")
        mensbt = cursor.fetchall()
        
        cursor.execute("SELECT * FROM inventory WHERE category != 'menstops' AND category != 'mensbt' AND status = 'active' ORDER BY created_at DESC LIMIT 10")
        other = cursor.fetchall()
        
        close_db(conn, cursor)
        return render_template('mensattire.html', menstops=menstops, mensbt=mensbt, other=other)
    except Exception as e:
        print(f"Mensattire error: {e}")
        close_db(conn)
        return render_template('mensattire.html', menstops=[], mensbt=[], other=[])

@app.route('/womensattire')
def womensattire():
    conn = get_db()
    if not conn:
        return render_template('womensattire.html', womenstops=[], womensbt=[], other=[])

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM inventory WHERE category = 'womenstops' AND status = 'active' ORDER BY created_at DESC")
        womenstops = cursor.fetchall()
        
        cursor.execute("SELECT * FROM inventory WHERE category = 'womensbt' AND status = 'active' ORDER BY created_at DESC")
        womensbt = cursor.fetchall()
        
        cursor.execute("SELECT * FROM inventory WHERE category != 'womenstops' AND category != 'womensbt' AND status = 'active' ORDER BY created_at DESC LIMIT 10")
        other = cursor.fetchall()
        
        close_db(conn, cursor)
        return render_template('womensattire.html', womenstops=womenstops, womensbt=womensbt, other=other)
    except Exception as e:
        print(f"Womensattire error: {e}")
        close_db(conn)
        return render_template('womensattire.html', womenstops=[], womensbt=[], other=[])

@app.route('/accesories')
def accesories():
    conn = get_db()
    if not conn:
        return render_template('accesories.html', accessories=[], other=[])

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM inventory WHERE category = 'accesories' AND status = 'active' ORDER BY created_at DESC")
        accessories = cursor.fetchall()
        
        cursor.execute("SELECT * FROM inventory WHERE category != 'accesories' AND status = 'active' ORDER BY created_at DESC LIMIT 10")
        other = cursor.fetchall()
        
        close_db(conn, cursor)
        return render_template('accesories.html', accessories=accessories, other=other)
    except Exception as e:
        print(f"Accesories error: {e}")
        close_db(conn)
        return render_template('accesories.html', accessories=[], other=[])

@app.route('/healthproducts')
def healthproducts():
    return render_template('healthproducts.html')

@app.route('/wellnesstips')
def wellnesstips():
    return render_template('wellnesstips.html')

# ============================================================
# SINGLE ITEM PAGE
# ============================================================

@app.route('/singleitem/<item_name>')
def singleitem(item_name):
    conn = get_db()
    if not conn:
        return render_template('singleitem.html', item=None, other=[])

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM inventory WHERE item = %s AND status = 'active'", (item_name,))
        item = cursor.fetchone()
        
        if not item:
            close_db(conn, cursor)
            return render_template('singleitem.html', item=None, other=[])

        # Get related products (same category)
        cursor.execute("SELECT * FROM inventory WHERE category = %s AND id != %s AND status = 'active' LIMIT 10", (item['category'], item['id']))
        other = cursor.fetchall()

        close_db(conn, cursor)
        return render_template('singleitem.html', item=item, other=other)
    except Exception as e:
        print(f"Singleitem error: {e}")
        close_db(conn)
        return render_template('singleitem.html', item=None, other=[])

# ============================================================
# SPECIAL OFFERS (Logged-in Users Only)
# ============================================================

@app.route('/offers')
@user_login_required
def offers_page():
    conn = get_db()
    if not conn:
        return render_template('offers.html', mens_offers=[], womens_offers=[], accessories=[])

    try:
        cursor = conn.cursor()
        
        # Men's offers
        cursor.execute("SELECT * FROM inventory WHERE category = 'offers' AND (category LIKE '%men%' OR category = 'menstops' OR category = 'mensbt') AND status = 'active'")
        mens_offers = cursor.fetchall()
        
        # Women's offers
        cursor.execute("SELECT * FROM inventory WHERE category = 'offers' AND (category LIKE '%women%' OR category = 'womenstops' OR category = 'womensbt') AND status = 'active'")
        womens_offers = cursor.fetchall()
        
        # Accessories offers
        cursor.execute("SELECT * FROM inventory WHERE category = 'offers' AND category = 'accesories' AND status = 'active'")
        accessories = cursor.fetchall()
        
        close_db(conn, cursor)
        return render_template('offers.html', mens_offers=mens_offers, womens_offers=womens_offers, accessories=accessories)
    except Exception as e:
        print(f"Offers error: {e}")
        close_db(conn)
        return render_template('offers.html', mens_offers=[], womens_offers=[], accessories=[])

# ============================================================
# CART FUNCTIONALITY
# ============================================================

@app.route('/cart')
def cart():
    cart_items = session.get('cart', {})
    total = sum(float(item['price']) * int(item['qty']) for item in cart_items.values())
    return render_template('cart.html', cart_items=cart_items, total=total)

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    item_name = request.form.get('item')
    price = request.form.get('price')
    image = request.form.get('image')
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
    flash(f'{item_name} added to cart!', 'success')
    return redirect(request.referrer or '/')

@app.route('/remove_from_cart/<item_name>')
def remove_from_cart(item_name):
    cart = session.get('cart', {})
    if item_name in cart:
        del cart[item_name]
        session['cart'] = cart
        flash(f'{item_name} removed from cart.', 'info')
    return redirect('/cart')

@app.route('/update_cart', methods=['POST'])
def update_cart():
    item_name = request.form.get('item')
    qty = int(request.form.get('qty', 1))
    
    cart = session.get('cart', {})
    
    if item_name in cart:
        if qty <= 0:
            del cart[item_name]
        else:
            cart[item_name]['qty'] = qty
        session['cart'] = cart
    
    return redirect('/cart')

# ============================================================
# CHECKOUT & ORDERS
# ============================================================

@app.route('/checkout')
def checkout():
    cart = session.get('cart', {})
    if not cart:
        flash('Your cart is empty.', 'warning')
        return redirect('/')
    
    total = sum(float(item['price']) * int(item['qty']) for item in cart.values())
    return render_template('checkout.html', cart_items=cart, total=total)

@app.route('/place_order', methods=['POST'])
def place_order():
    customer_name = request.form.get('customer_name')
    phone = request.form.get('phone')
    email = request.form.get('email')
    location = request.form.get('location')
    address = request.form.get('address')
    
    cart = session.get('cart', {})
    
    if not cart:
        flash('Your cart is empty.', 'warning')
        return redirect('/')
    
    total = sum(float(item['price']) * int(item['qty']) for item in cart.values())
    order_number = "BS" + datetime.now().strftime("%Y%m%d%H%M%S")
    
    conn = get_db()
    if not conn:
        flash('Database error. Please try again.', 'danger')
        return redirect('/checkout')
    
    try:
        cursor = conn.cursor()
        
        # Insert order
        cursor.execute("""
            INSERT INTO orders (
                order_number, customer_name, phone, email, location, 
                address, total_amount, status, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
            RETURNING id
        """, (order_number, customer_name, phone, email, location, address, total, 'pending'))
        
        order_id = cursor.fetchone()['id']
        
        # Insert order items
        for item in cart.values():
            cursor.execute("""
                INSERT INTO order_items (
                    order_id, product_name, quantity, unit_price, subtotal
                ) VALUES (%s, %s, %s, %s, %s)
            """, (order_id, item['name'], item['qty'], item['price'], float(item['price']) * int(item['qty'])))
        
        conn.commit()
        close_db(conn, cursor)
        
        # Clear cart
        session.pop('cart', None)
        
        flash('Order placed successfully!', 'success')
        return redirect(f'/order_success/{order_number}')
    except Exception as e:
        print(f"Place order error: {e}")
        close_db(conn)
        flash('Error placing order. Please try again.', 'danger')
        return redirect('/checkout')

@app.route('/order_success/<order_number>')
def order_success(order_number):
    return render_template('order_success.html', order_number=order_number)

# ============================================================
# USER AUTHENTICATION
# ============================================================

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        location = request.form.get('location')
        
        if len(password) < 8:
            flash('Password must be at least 8 characters.', 'danger')
            return redirect('/')
        
        hashed_password = generate_password_hash(password)
        
        conn = get_db()
        if not conn:
            flash('Database error. Please try again.', 'danger')
            return redirect('/')
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (username, password_hash, email, location, created_at)
                VALUES (%s, %s, %s, %s, NOW())
            """, (username, hashed_password, email, location))
            conn.commit()
            close_db(conn, cursor)
            flash('Signup successful! Please login.', 'success')
        except Exception as e:
            print(f"Signup error: {e}")
            close_db(conn)
            flash('Username or email already exists.', 'danger')
        
        return redirect('/')
    
    return redirect('/')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        conn = get_db()
        if not conn:
            flash('Database error. Please try again.', 'danger')
            return redirect('/')
        
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()
            close_db(conn, cursor)
            
            if user and check_password_hash(user['password_hash'], password):
                session['user_id'] = user['id']
                session['username'] = user['username']
                flash(f'Welcome back, {user["username"]}!', 'success')
                return redirect('/')
            else:
                flash('Invalid email or password.', 'danger')
        except Exception as e:
            print(f"Login error: {e}")
            close_db(conn)
            flash('Login error. Please try again.', 'danger')
        
        return redirect('/')
    
    return redirect('/')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect('/')

# ============================================================
# ADMIN AUTHENTICATION
# ============================================================

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        conn = get_db()
        if not conn:
            flash('Database error. Please try again.', 'danger')
            return render_template('admin/login.html')
        
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM admins WHERE username = %s AND status = 'active'", (username,))
            admin = cursor.fetchone()
            close_db(conn, cursor)
            
            if admin and check_password_hash(admin['password_hash'], password):
                session['admin_id'] = admin['id']
                session['admin_username'] = admin['username']
                session['admin_role'] = admin['role']
                flash(f'Welcome back, {admin["username"]}!', 'success')
                return redirect('/admin/dashboard')
            else:
                flash('Invalid username or password.', 'danger')
        except Exception as e:
            print(f"Admin login error: {e}")
            close_db(conn)
            flash('Login error. Please try again.', 'danger')
        
        return render_template('admin/login.html')
    
    return render_template('admin/login.html')

@app.route('/admin/logout')
def admin_logout():
    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect('/admin/login')

# ============================================================
# ADMIN DASHBOARD
# ============================================================

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    conn = get_db()
    if not conn:
        flash('Database error.', 'danger')
        return render_template('admin/dashboard.html', 
                             total_products=0, total_orders=0, total_users=0, 
                             total_reviews=0, categories={}, recent_products=[], recent_orders=[])

    try:
        cursor = conn.cursor()
        
        # Counts
        cursor.execute("SELECT COUNT(*) as count FROM inventory")
        total_products = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM orders")
        total_orders = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM users")
        total_users = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM customer_reviews WHERE status = 'pending'")
        total_reviews = cursor.fetchone()['count']
        
        # Category breakdown
        cursor.execute("""
            SELECT category, COUNT(*) as count 
            FROM inventory 
            WHERE status = 'active' 
            GROUP BY category 
            ORDER BY count DESC
        """)
        categories = cursor.fetchall()
        
        # Recent products
        cursor.execute("""
            SELECT id, item, currentp, category, image, created_at 
            FROM inventory 
            ORDER BY created_at DESC 
            LIMIT 5
        """)
        recent_products = cursor.fetchall()
        
        # Recent orders
        cursor.execute("""
            SELECT id, order_number, customer_name, total_amount, status, created_at 
            FROM orders 
            ORDER BY created_at DESC 
            LIMIT 5
        """)
        recent_orders = cursor.fetchall()
        
        close_db(conn, cursor)
        return render_template('admin/dashboard.html',
                             total_products=total_products,
                             total_orders=total_orders,
                             total_users=total_users,
                             total_reviews=total_reviews,
                             categories=categories,
                             recent_products=recent_products,
                             recent_orders=recent_orders)
    except Exception as e:
        print(f"Dashboard error: {e}")
        close_db(conn)
        return render_template('admin/dashboard.html',
                             total_products=0, total_orders=0, total_users=0,
                             total_reviews=0, categories={}, recent_products=[], recent_orders=[])

# ============================================================
# ADMIN - PRODUCT MANAGEMENT
# ============================================================

@app.route('/admin/products')
@login_required
def admin_products():
    conn = get_db()
    if not conn:
        flash('Database error.', 'danger')
        return render_template('admin/products.html', products=[])

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM inventory ORDER BY created_at DESC")
        products = cursor.fetchall()
        close_db(conn, cursor)
        return render_template('admin/products.html', products=products)
    except Exception as e:
        print(f"Admin products error: {e}")
        close_db(conn)
        return render_template('admin/products.html', products=[])

@app.route('/admin/products/add', methods=['GET', 'POST'])
@login_required
def admin_product_add():
    if request.method == 'POST':
        item = request.form.get('item')
        description = request.form.get('description')
        currentp = request.form.get('currentp')
        category = request.form.get('category')
        stock_quantity = request.form.get('stock_quantity', 0)
        featured = request.form.get('featured') == 'on'
        status = request.form.get('status', 'active')
        
        if not item or not currentp or not category:
            flash('Item, price, and category are required.', 'danger')
            return render_template('admin/product_form.html')
        
        # Handle image upload
        image_url = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                image_url = upload_image(file, 'products')
                if not image_url:
                    flash('Failed to upload image.', 'danger')
                    return render_template('admin/product_form.html')
        
        conn = get_db()
        if not conn:
            flash('Database error.', 'danger')
            return render_template('admin/product_form.html')
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO inventory (
                    item, description, currentp, category, 
                    image_url, stock_quantity, featured, status, created_at, updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                RETURNING id
            """, (item, description, float(currentp), category, image_url, int(stock_quantity), featured, status))
            
            product_id = cursor.fetchone()['id']
            conn.commit()
            close_db(conn, cursor)
            flash('Product added successfully!', 'success')
            return redirect('/admin/products')
        except Exception as e:
            print(f"Add product error: {e}")
            close_db(conn)
            flash('Error adding product.', 'danger')
    
    return render_template('admin/product_form.html')

@app.route('/admin/products/edit/<int:product_id>', methods=['GET', 'POST'])
@login_required
def admin_product_edit(product_id):
    conn = get_db()
    if not conn:
        flash('Database error.', 'danger')
        return redirect('/admin/products')
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM inventory WHERE id = %s", (product_id,))
        product = cursor.fetchone()
        
        if not product:
            flash('Product not found.', 'danger')
            close_db(conn, cursor)
            return redirect('/admin/products')
        
        if request.method == 'POST':
            item = request.form.get('item')
            description = request.form.get('description')
            currentp = request.form.get('currentp')
            category = request.form.get('category')
            stock_quantity = request.form.get('stock_quantity', 0)
            featured = request.form.get('featured') == 'on'
            status = request.form.get('status', 'active')
            
            # Handle image upload
            image_url = product['image_url']
            if 'image' in request.files:
                file = request.files['image']
                if file and file.filename:
                    image_url = upload_image(file, 'products')
                    if not image_url:
                        flash('Failed to upload image.', 'danger')
                        close_db(conn, cursor)
                        return render_template('admin/product_form.html', product=product)
            
            cursor.execute("""
                UPDATE inventory SET
                    item = %s,
                    description = %s,
                    currentp = %s,
                    category = %s,
                    image_url = %s,
                    stock_quantity = %s,
                    featured = %s,
                    status = %s,
                    updated_at = NOW()
                WHERE id = %s
            """, (item, description, float(currentp), category, image_url, int(stock_quantity), featured, status, product_id))
            
            conn.commit()
            close_db(conn, cursor)
            flash('Product updated successfully!', 'success')
            return redirect('/admin/products')
        
        close_db(conn, cursor)
        return render_template('admin/product_form.html', product=product)
    except Exception as e:
        print(f"Edit product error: {e}")
        close_db(conn)
        flash('Error loading product.', 'danger')
        return redirect('/admin/products')

@app.route('/admin/products/delete/<int:product_id>')
@login_required
def admin_product_delete(product_id):
    conn = get_db()
    if not conn:
        flash('Database error.', 'danger')
        return redirect('/admin/products')
    
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM inventory WHERE id = %s", (product_id,))
        conn.commit()
        close_db(conn, cursor)
        flash('Product deleted successfully.', 'success')
    except Exception as e:
        print(f"Delete product error: {e}")
        close_db(conn)
        flash('Error deleting product.', 'danger')
    
    return redirect('/admin/products')

# ============================================================
# ADMIN - CATEGORIES
# ============================================================

@app.route('/admin/categories')
@login_required
def admin_categories():
    conn = get_db()
    if not conn:
        flash('Database error.', 'danger')
        return render_template('admin/categories.html', categories=[])

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                category, 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) as active_count
            FROM inventory 
            GROUP BY category 
            ORDER BY total DESC
        """)
        categories = cursor.fetchall()
        close_db(conn, cursor)
        return render_template('admin/categories.html', categories=categories)
    except Exception as e:
        print(f"Categories error: {e}")
        close_db(conn)
        return render_template('admin/categories.html', categories=[])

# ============================================================
# ADMIN - ORDERS
# ============================================================

@app.route('/admin/orders')
@login_required
def admin_orders():
    conn = get_db()
    if not conn:
        flash('Database error.', 'danger')
        return render_template('admin/orders.html', orders=[])

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM orders 
            ORDER BY created_at DESC
        """)
        orders = cursor.fetchall()
        close_db(conn, cursor)
        return render_template('admin/orders.html', orders=orders)
    except Exception as e:
        print(f"Orders error: {e}")
        close_db(conn)
        return render_template('admin/orders.html', orders=[])

@app.route('/admin/orders/<int:order_id>/status', methods=['POST'])
@login_required
def admin_order_status(order_id):
    status = request.form.get('status')
    
    conn = get_db()
    if not conn:
        flash('Database error.', 'danger')
        return redirect('/admin/orders')
    
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE orders SET status = %s, updated_at = NOW() WHERE id = %s", (status, order_id))
        conn.commit()
        close_db(conn, cursor)
        flash('Order status updated!', 'success')
    except Exception as e:
        print(f"Order status error: {e}")
        close_db(conn)
        flash('Error updating order status.', 'danger')
    
    return redirect('/admin/orders')

# ============================================================
# ADMIN - REVIEWS
# ============================================================

@app.route('/admin/reviews')
@login_required
def admin_reviews():
    conn = get_db()
    if not conn:
        flash('Database error.', 'danger')
        return render_template('admin/reviews.html', reviews=[])

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM customer_reviews ORDER BY created_at DESC")
        reviews = cursor.fetchall()
        close_db(conn, cursor)
        return render_template('admin/reviews.html', reviews=reviews)
    except Exception as e:
        print(f"Reviews error: {e}")
        close_db(conn)
        return render_template('admin/reviews.html', reviews=[])

@app.route('/admin/reviews/<int:review_id>/approve')
@login_required
def admin_review_approve(review_id):
    conn = get_db()
    if not conn:
        flash('Database error.', 'danger')
        return redirect('/admin/reviews')
    
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE customer_reviews SET status = 'approved' WHERE id = %s", (review_id,))
        conn.commit()
        close_db(conn, cursor)
        flash('Review approved!', 'success')
    except Exception as e:
        print(f"Approve review error: {e}")
        close_db(conn)
        flash('Error approving review.', 'danger')
    
    return redirect('/admin/reviews')

@app.route('/admin/reviews/<int:review_id>/delete')
@login_required
def admin_review_delete(review_id):
    conn = get_db()
    if not conn:
        flash('Database error.', 'danger')
        return redirect('/admin/reviews')
    
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM customer_reviews WHERE id = %s", (review_id,))
        conn.commit()
        close_db(conn, cursor)
        flash('Review deleted.', 'success')
    except Exception as e:
        print(f"Delete review error: {e}")
        close_db(conn)
        flash('Error deleting review.', 'danger')
    
    return redirect('/admin/reviews')

# ============================================================
# ERROR HANDLERS
# ============================================================

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

# ============================================================
# APPLICATION ENTRY POINT
# ============================================================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
