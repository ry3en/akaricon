from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta
import pyodbc
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)

# Configuración de conexión a la base de datos
DATABASE_CONFIG = {
    'server': 'practicasuni.database.windows.net',
    'database': 'luxaris',
    'username': 'admon',
    'password': '########',
    'driver': '{ODBC Driver 17 for SQL Server}',
}

# Configura la clave secreta para JWT
app.config['JWT_SECRET_KEY'] = '###############'
jwt = JWTManager(app)

def get_db_connection():
    conn = pyodbc.connect(
        f"DRIVER={DATABASE_CONFIG['driver']};"
        f"SERVER={DATABASE_CONFIG['server']};"
        f"DATABASE={DATABASE_CONFIG['database']};"
        f"UID={DATABASE_CONFIG['username']};"
        f"PWD={DATABASE_CONFIG['password']}"
    )
    return conn

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('Username')
    phone = data.get('Phone')
    password = data.get('Password')

    if not username or not password:
        return jsonify({"msg": "Missing username or password"}), 400

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Users WHERE Username = ?", username)
            if cursor.fetchone():
                return jsonify({"msg": "Username already exists"}), 409
            password_hash = generate_password_hash(password)
            cursor.execute("INSERT INTO Users (Username, Phone, Password, CreatedAt) VALUES (?, ?, ?, GETDATE())",
                           (username, phone, password_hash))
            conn.commit()
        return jsonify({"msg": "User registered successfully"}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('Username')
    password = data.get('Password')

    if not username or not password:
        return jsonify({"msg": "Missing username or password"}), 400

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT Username, Password, User_type, ID_user FROM Users WHERE Username = ?", (username,))
            user = cursor.fetchone()

            if user and check_password_hash(user.Password, password):
                access_token = create_access_token(identity=username, expires_delta=timedelta(days=1))
                data = {"access_token": access_token, "Username": username, "User_type": user.User_type, "ID_user": user.ID_user}
                return jsonify(data)
            else:
                return jsonify({"msg": "Bad username or password"}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/products', methods=['POST'])
def create_product():
    data = request.json
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            query = "INSERT INTO Products (Product_name, ID_Category, Barcode, SKU, Image_URL, PriceBuy, PriceBuyMX, Quantity, PriceSell) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
            cursor.execute(query, (
                data['Product_name'],
                data['ID_Category'],
                data['Barcode'],
                data['SKU'],
                data['Image_URL'],
                data['PriceBuy'],
                data['PriceBuyMX'],
                data['Quantity'],
                data['PriceSell']
            ))
            conn.commit()
        return jsonify({'status': 'Product created'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/products', methods=['PUT'])
def update_product():
    data = request.json
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE Products 
                SET Product_name = ?, Image_URL = ?, Quantity = ?, PriceSell = ?
                WHERE ID_Product = ?
            """, (
                data['Product_name'],
                data['Image_URL'],
                data['Quantity'],
                data['PriceSell'],
                data['ID_Product']
            ))
            conn.commit()
            if cursor.rowcount == 0:
                return jsonify({'error': 'Product not found'}), 404
            return jsonify({'status': 'Product updated'}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Products WHERE ID_Product = ?", (product_id,))
            conn.commit()
            if cursor.rowcount == 0:
                return jsonify({'error': 'Product not found'}), 404
            return jsonify({'status': f'Product with ID {product_id} deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/products', methods=['GET'])
def get_products():
    category_id = request.args.get('category')
    product_id = request.args.get('prod')
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            if product_id:
                query = "SELECT * FROM Products WHERE ID_Product = ?"
                cursor.execute(query, (product_id,))
            elif category_id:
                query = "SELECT * FROM Products WHERE ID_Category = ?"
                cursor.execute(query, (category_id,))
            else:
                query = "SELECT * FROM Products"
                cursor.execute(query)
            products = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
        return jsonify(products)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/categories', methods=['GET'])
def get_categories():
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Categories")
            categories = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
        return jsonify(categories)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/brands', methods=['GET'])
def get_brands():
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Brands")
            brands = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
        return jsonify(brands)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
