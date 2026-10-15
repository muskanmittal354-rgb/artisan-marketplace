import os
from flask import Flask, render_template, request, redirect
from pymongo import MongoClient
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Upload Folder Config
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Database Connection (Apna Mongo URI yahan rakhein)
client = MongoClient("mongodb+srv://muskanmittal354_db_user:Hunarsetu2026@cluster0.egt4ms1.mongodb.net/artisan_marketplaces?retryWrites=true&w=majority")
db = client['hunar_setu_db']

@app.route('/')
def home():
    return redirect('/products')

# 1. Artisan Form Route (Fix for 404 Not Found)
@app.route('/artisan')
def artisan_form():
    return render_template('artisan.html')

# 2. Save Artisan Route
@app.route('/save-artisan', methods=['POST'])
def save_artisan():
    name = request.form.get('name')
    location = request.form.get('location')
    category = request.form.get('category')
    phone = request.form.get('phone')

    db.artisans.insert_one({
        'name': name,
        'location': location,
        'category': category,
        'phone': phone
    })
    return redirect('/products')

@app.route('/artisans')
def view_artisans():
    artisans_list = list(db.artisans.find())
    return render_template('artisans_list.html', artisans=artisans_list)

@app.route('/add-product')
def add_product_form():
    artisans_list = list(db.artisans.find())
    return render_template('add_product.html', artisans=artisans_list)

@app.route('/save-product', methods=['POST'])
def save_product():
    title = request.form.get('title')
    price = request.form.get('price')
    artisan_name = request.form.get('artisan_name')
    description = request.form.get('description')
    
    image_url = ""
    file = request.files.get('image_file')
    if file and file.filename != '':
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        image_url = f"/static/uploads/{filename}"
    else:
        image_url = request.form.get('image_url')

    db.products.insert_one({
        'title': title,
        'price': price,
        'artisan_name': artisan_name,
        'description': description,
        'image_url': image_url
    })
    
    return redirect('/products')

@app.route('/products')
def view_products():
    search_query = request.args.get('search', '')
    category_filter = request.args.get('category', '')
    
    query = {}
    if search_query:
        query['title'] = {'$regex': search_query, '$options': 'i'}
    
    products_list = list(db.products.find(query))
    
    if category_filter:
        filtered_products = []
        for p in products_list:
            artisan = db.artisans.find_one({'name': p.get('artisan_name')})
            if artisan and artisan.get('category') == category_filter:
                filtered_products.append(p)
        products_list = filtered_products

    return render_template('products_list.html', products=products_list, search=search_query, selected_category=category_filter)

@app.route('/artisan/<artisan_name>')
def artisan_profile(artisan_name):
    artisan_details = db.artisans.find_one({'name': artisan_name})
    artisan_products = list(db.products.find({'artisan_name': artisan_name}))
    return render_template('artisan_profile.html', artisan=artisan_details, products=artisan_products, name=artisan_name)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)