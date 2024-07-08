from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta
import pyodbc
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)

# Configuración de conexión a la base de datos
DATABASE_CONFIG = {
    'server': 'practicasuni.database.windows.net',
    'database': 'akari',
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


@app.route('/')
def index():
    return "API is running!"


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


@app.route('/categories/<int:category_id>', methods=['GET'])
def get_category_name(category_id):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT name FROM Categories WHERE ID_Category = ?"
            cursor.execute(query, (category_id,))
            category = cursor.fetchone()
            if category:
                return jsonify({'name': category[0]})
            else:
                return jsonify({'error': 'Category not found'}), 404
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
                data = {"access_token": access_token, "Username": username, "User_type": user.User_type,
                        "ID_user": user.ID_user}
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
            query = "INSERT INTO Products (Product_name, Quantity, Color, SKU, Ubi, Price_Sell, Price_Buy, Image_URL) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
            cursor.execute(query, (
                data['Product_name'],
                data['Quantity'],
                data['Color'],
                data['SKU'],
                data['Ubi'],
                data['Price_Sell'],
                data['Price_Buy'],
                data['Image_URL']
            ))
            conn.commit()
        return jsonify({'status': 'Product created'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/productcategory', methods=['POST'])
def add_product_category():
    data = request.json
    product_id = data.get('ID_Product')
    category_id = data.get('ID_Category')

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            query = "INSERT INTO ProductCategories (ID_Product, ID_Category) VALUES (?, ?)"
            cursor.execute(query, (product_id, category_id))
            conn.commit()
        return jsonify({'status': 'Category added to product'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Update a product
@app.route('/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    data = request.json
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE Products 
                SET Product_name = ?, Quantity = ?, Color = ?, SKU = ?, Ubi = ?, Price_Sell = ?, Price_Buy = ?, Image_URL = ?
                WHERE ID_Product = ?
            """, (
                data['Product_name'],
                data['Quantity'],
                data['Color'],
                data['SKU'],
                data['Ubi'],
                data['Price_Sell'],
                data['Price_Buy'],
                data['Image_URL'],
                product_id
            ))
            conn.commit()
            if cursor.rowcount == 0:
                return jsonify({'error': 'Product not found'}), 404
            return jsonify({'status': 'Product updated'}), 200
    except Exception as e:
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
                query = """
                    SELECT P.* 
                    FROM Products P
                    JOIN ProductCategories PC ON P.ID_product = PC.ID_Product
                    WHERE PC.ID_Category = ?
                """
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

            # Verificar si ID_Product está presente en la solicitud
            if 'ID_Product' not in data:
                return jsonify({'error': 'ID_Product no está presente en la solicitud.'}), 400

            # Check current stock
            cursor.execute("SELECT Quantity FROM Products WHERE ID_Product = ?", (data['ID_Product'],))
            product = cursor.fetchone()
            if product is None:
                return jsonify({'error': 'Product not found'}), 404

            current_quantity = product[0]
            new_quantity = current_quantity - data['Quantity']

            if new_quantity < 0:
                return jsonify({'error': 'Insufficient stock'}), 400

            # Insert into CartTransactions
            query = "INSERT INTO CartTransactions (ID_User, ID_Product, Quantity, Total_amount, Payment_method, Added_Date, Order_date, Order_status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
            cursor.execute(query, (
                data['ID_User'],
                data['ID_Product'],
                data['Quantity'],
                data['Total_amount'],
                data['Payment_method'],
                data['Added_Date'],
                data['Order_date'],
                data['Order_status']
            ))

            # Update product quantity
            cursor.execute("UPDATE Products SET Quantity = ? WHERE ID_Product = ?", (new_quantity, data['ID_Product']))
            conn.commit()

        return jsonify({'status': 'Cart transaction created and product quantity updated'}), 201
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
                SET Quantity = ?, Total_amount = ?, Payment_method = ?, Added_Date = ?, Order_date = ?, Order_status = ?
                WHERE ID_Transaction = ?
            """, (
                data['Quantity'],
                data['Total_amount'],
                data['Payment_method'],
                data['Added_Date'],
                data['Order_date'],
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


# Create a notification
@app.route('/notifications', methods=['POST'])
def create_notification():
    data = request.json
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            query = "INSERT INTO Notifications (ID_Product, Min_Stock) VALUES (?, ?)"
            cursor.execute(query, (
                data['ID_Product'],
                data['Min_Stock']
            ))
            conn.commit()
        return jsonify({'status': 'Notification created'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Get notifications
@app.route('/notifications', methods=['GET'])
def get_notifications():
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Notifications")
            notifications = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
        return jsonify(notifications)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Update a notification
@app.route('/notifications/<int:notification_id>', methods=['PUT'])
def update_notification(notification_id):
    data = request.json
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE Notifications
                SET Min_Stock = ?
                WHERE ID_Notification = ?
            """, (
                data['Min_Stock'],
                notification_id
            ))
            conn.commit()
            if cursor.rowcount == 0:
                return jsonify({'error': 'Notification not found'}), 404
            return jsonify({'status': 'Notification updated'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Delete a notification
@app.route('/notifications/<int:notification_id>', methods=['DELETE'])
def delete_notification(notification_id):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Notifications WHERE ID_Notification = ?", (notification_id,))
            conn.commit()
            if cursor.rowcount == 0:
                return jsonify({'error': 'Notification not found'}), 404
            return jsonify({'status': f'Notification with ID {notification_id} deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Create a ticket
@app.route('/tickets', methods=['POST'])
def create_ticket():
    data = request.json
    id_client = data.get('ID_client')
    id_user = data.get('ID_user')
    id_cart = data.get('ID_Cart')
    id_code = data.get('ID_Code')
    issue_details = data.get('Issue_details')

    pre_price = 0
    final_price = 0
    discount = 0

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Calcular Pre_Price basado en los elementos del carrito
            cursor.execute("SELECT SUM(Total_amount) FROM CartTransactions WHERE ID_Cart = ?", (id_cart,))
            pre_price = cursor.fetchone()[0]
            final_price = pre_price  # Inicialmente, Final_Price es igual a Pre_Price

            # Si se proporciona un código promocional, aplicar el descuento
            if id_code:
                cursor.execute("SELECT Discount FROM PromotionalCodes WHERE ID_Code = ?", (id_code,))
                discount = cursor.fetchone()[0]
                final_price = pre_price - (pre_price * (discount / 100))

            # Insertar el ticket en la base de datos
            cursor.execute("""
                INSERT INTO Tickets (ID_client, ID_user, ID_Cart, ID_Code, Issue_details, Prev_Price, Final_Price)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (id_client, id_user, id_cart, id_code, issue_details, pre_price, final_price))
            cursor.execute("SELECT SCOPE_IDENTITY()")
            ticket_id = cursor.fetchone()[0]

            conn.commit()

            return jsonify({"ID_ticket": ticket_id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
