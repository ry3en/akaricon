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
    'password': 'Abeja123!',
    'driver': '{ODBC Driver 17 for SQL Server}',
}

# Configura la clave secreta para JWT
app.config['JWT_SECRET_KEY'] = 'b16191c9589984e86de2d8cd044e49f8'
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

# Create a provider
@app.route('/providers', methods=['POST'])
def create_provider():
    data = request.json
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            query = "INSERT INTO Providers (Name, Address, Contact_info) VALUES (?, ?, ?)"
            cursor.execute(query, (
                data['Name'],
                data['Address'],
                data['Contact_info']
            ))
            conn.commit()
        return jsonify({'status': 'Provider created'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Create a client
@app.route('/clients', methods=['POST'])
def create_client():
    data = request.json
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            query = "INSERT INTO Clients (Name, Address, Contact_info) VALUES (?, ?, ?)"
            cursor.execute(query, (
                data['Name'],
                data['Address'],
                data['Contact_info']
            ))
            conn.commit()
        return jsonify({'status': 'Client created'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Register a new user
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

# User login
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

# Create a product
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

# Update a product
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

# Delete a product
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

# Get products
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

# Get categories
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

# Get brands
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

# Get users
@app.route('/users', methods=['GET'])
def get_users():
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Users")
            users = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
        return jsonify(users)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Get clients
@app.route('/clients', methods=['GET'])
def get_clients():
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Clients")
            clients = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
        return jsonify(clients)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Get providers
@app.route('/providers', methods=['GET'])
def get_providers():
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Providers")
            providers = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
        return jsonify(providers)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Create cart transaction
@app.route('/carttransactions', methods=['POST'])
def create_cart_transaction():
    data = request.json
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            query = "INSERT INTO CartTransactions (ID_User, ID_Product, Quantity, Unit_price, Total_amount, Payment_method, Status, Order_date, Order_status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
            cursor.execute(query, (
                data['ID_User'],
                data['ID_Product'],
                data['Quantity'],
                data['Unit_price'],
                data['Total_amount'],
                data['Payment_method'],
                data['Status'],
                data['Order_date'],
                data['Order_status']
            ))
            conn.commit()
        return jsonify({'status': 'Cart transaction created'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Get cart transactions
@app.route('/carttransactions', methods=['GET'])
def get_cart_transactions():
    user_id = request.args.get('user')
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            if user_id:
                query = "SELECT * FROM CartTransactions WHERE ID_User = ?"
                cursor.execute(query, (user_id,))
            else:
                query = "SELECT * FROM CartTransactions"
                cursor.execute(query)
            transactions = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
        return jsonify(transactions)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Update cart transaction
@app.route('/carttransactions', methods=['PUT'])
def update_cart_transaction():
    data = request.json
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE CartTransactions 
                SET Quantity = ?, Unit_price = ?, Total_amount = ?, Payment_method = ?, Status = ?, Order_status = ?
                WHERE ID_Transaction = ?
            """, (
                data['Quantity'],
                data['Unit_price'],
                data['Total_amount'],
                data['Payment_method'],
                data['Status'],
                data['Order_status'],
                data['ID_Transaction']
            ))
            conn.commit()
            if cursor.rowcount == 0:
                return jsonify({'error': 'Cart transaction not found'}), 404
            return jsonify({'status': 'Cart transaction updated'}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
