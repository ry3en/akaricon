import jwt
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import List, Optional, Dict, Any, Union, Annotated
from pydantic import BaseModel, Field
from datetime import timedelta, datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, Date, DateTime, Boolean, Table, \
    MetaData, func, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from sqlalchemy.sql import select
from passlib.context import CryptContext
import os
from dotenv import load_dotenv
import urllib.parse
from contextlib import contextmanager

# Cargar variables de entorno
load_dotenv()

app = FastAPI(title="Akari API", description="API para el sistema Akari")

# Configuración de conexión a la base de datos
DATABASE_CONFIG = {
    'server': os.getenv('DB_SERVER', 'practicasuni.database.windows.net'),
    'database': os.getenv('DB_NAME', 'akari'),
    'username': os.getenv('DB_USER', 'admon'),
    'password': os.getenv('DB_PASSWORD', 'Abeja123!'),
    'driver': os.getenv('DB_DRIVER', 'ODBC Driver 17 for SQL Server'),
}

# Crear la URL de conexión para SQLAlchemy
params = urllib.parse.quote_plus(
    f"DRIVER={{{DATABASE_CONFIG['driver']}}};"
    f"SERVER={DATABASE_CONFIG['server']};"
    f"DATABASE={DATABASE_CONFIG['database']};"
    f"UID={DATABASE_CONFIG['username']};"
    f"PWD={DATABASE_CONFIG['password']}"
)

DATABASE_URL = f"mssql+pyodbc:///?odbc_connect={params}"

# Crear el motor de conexión
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Configuración JWT
SECRET_KEY = os.getenv('JWT_SECRET_KEY', "b16191c9589984e86de2d8cd044e49f8")
ALGORITHM = os.getenv('JWT_ALGORITHM', "HS256")

# Configuración de seguridad
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Base para los modelos SQLAlchemy
Base = declarative_base()


# Definición de las tablas usando SQLAlchemy
class Category(Base):
    __tablename__ = "Categories"

    ID_Category = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    img_url = Column(String(500))

    # Relaciones
    products = relationship("ProductCategory", back_populates="category")


class Client(Base):
    __tablename__ = "Clients"

    ID_client = Column(Integer, primary_key=True, index=True)
    Name = Column(String(255))
    Address = Column(String(255))
    Contact_info = Column(String(255))

    # Relaciones
    tickets = relationship("Ticket", back_populates="client")


class Product(Base):
    __tablename__ = "Products"

    ID_product = Column(Integer, primary_key=True, index=True)
    Product_name = Column(String(255))
    Quantity = Column(Integer)
    Color = Column(String(255))
    SKU = Column(String(255))
    ID_provider = Column(Integer, ForeignKey("Providers.ID_provider"))
    Ubi = Column(String(255))  # Esta columna no está en la definición SQL, pero se usa en el código
    Price_Sell = Column(Float)
    Price_Buy = Column(Float)
    Image_URL = Column(String(255))
    Image_URL2 = Column(String(255))
    Image_URL3 = Column(String(255))

    # Relaciones
    categories = relationship("ProductCategory", back_populates="product")
    notifications = relationship("Notification", back_populates="product")
    cart_transactions = relationship("CartTransaction", back_populates="product")
    provider = relationship("Provider", back_populates="products")


class Notification(Base):
    __tablename__ = "Notifications"

    ID_Notification = Column(Integer, primary_key=True, index=True)
    ID_Product = Column(Integer, ForeignKey("Products.ID_product"))
    Min_Stock = Column(Integer)

    # Relaciones
    product = relationship("Product", back_populates="notifications")


class ProductCategory(Base):
    __tablename__ = "ProductCategories"

    ID_Product = Column(Integer, ForeignKey("Products.ID_product"), primary_key=True)
    ID_Category = Column(Integer, ForeignKey("Categories.ID_Category"), primary_key=True)

    # Relaciones
    product = relationship("Product", back_populates="categories")
    category = relationship("Category", back_populates="products")


class PromotionalCode(Base):
    __tablename__ = "PromotionalCodes"

    ID_Code = Column(Integer, primary_key=True, index=True)
    Code = Column(String(50), nullable=False)
    Discount = Column(Float)
    ExpirationDate = Column(Date)
    IsActive = Column(Boolean, default=True)

    # Relaciones
    tickets = relationship("Ticket", back_populates="promo_code")


class Provider(Base):
    __tablename__ = "Providers"

    ID_provider = Column(Integer, primary_key=True, index=True)
    Name = Column(String(255))
    Address = Column(String(255))  # Esta columna no está en la definición SQL, pero se usa en el código
    Contact_info = Column(String(255))  # Esta columna no está en la definición SQL, pero se usa en el código

    # Relaciones
    products = relationship("Product", back_populates="provider")


class User(Base):
    __tablename__ = "Users"

    ID_user = Column(Integer, primary_key=True, index=True)
    Username = Column(String(255))
    Password = Column(String(255))
    User_type = Column(String(50), default="vendedor")
    UpdatedAt = Column(DateTime)
    CreatedAt = Column(DateTime, default=datetime.utcnow)
    Phone = Column(String(50))

    # Relaciones
    cart_transactions = relationship("CartTransaction", back_populates="user")
    tickets = relationship("Ticket", back_populates="user")


class CartTransaction(Base):
    __tablename__ = "CartTransactions"

    ID_Transaction = Column(Integer, primary_key=True, index=True)
    ID_User = Column(Integer, ForeignKey("Users.ID_user"))
    ID_Product = Column(Integer, ForeignKey("Products.ID_product"))
    Quantity = Column(Integer)
    Total_amount = Column(Float)
    Payment_method = Column(String(100))
    Added_Date = Column(DateTime, default=datetime.utcnow)
    Order_date = Column(Date)
    Order_status = Column(String(50))
    ID_Ticket = Column(Integer, ForeignKey("Tickets.ID_ticket"))

    # Relaciones
    user = relationship("User", back_populates="cart_transactions")
    product = relationship("Product", back_populates="cart_transactions")
    ticket = relationship("Ticket", back_populates="cart_transactions")


class Ticket(Base):
    __tablename__ = "Tickets"

    ID_ticket = Column(Integer, primary_key=True, index=True)
    ID_client = Column(Integer, ForeignKey("Clients.ID_client"))
    ID_user = Column(Integer, ForeignKey("Users.ID_user"))
    Issue_details = Column(String(1000))
    Created_at = Column(DateTime, default=datetime.utcnow)
    Updated_at = Column(DateTime)
    ID_Code = Column(Integer, ForeignKey("PromotionalCodes.ID_Code"))
    ID_Cart = Column(Integer)
    Final_Price = Column(Float)
    Prev_Price = Column(Float)

    # Relaciones
    client = relationship("Client", back_populates="tickets")
    user = relationship("User", back_populates="tickets")
    promo_code = relationship("PromotionalCode", back_populates="tickets")
    cart_transactions = relationship("CartTransaction", back_populates="ticket")


# Modelos Pydantic para validación
class ProviderBase(BaseModel):
    Name: str
    Address: Optional[str] = None
    Contact_info: Optional[str] = None


class ProviderCreate(ProviderBase):
    pass


class ProviderResponse(ProviderBase):
    ID_provider: int

    class Config:
        orm_mode = True


class PromoCodeBase(BaseModel):
    Code: str
    Discount: float
    ExpirationDate: str


class PromoCodeCreate(PromoCodeBase):
    pass


class PromoCodeResponse(PromoCodeBase):
    ID_Code: int
    IsActive: Optional[bool] = True

    class Config:
        orm_mode = True


class ClientBase(BaseModel):
    Name: str
    Address: Optional[str] = None
    Contact_info: Optional[str] = None


class ClientCreate(ClientBase):
    pass


class ClientResponse(ClientBase):
    ID_client: int

    class Config:
        orm_mode = True


class ProductBase(BaseModel):
    Product_name: str
    Quantity: int
    Color: Optional[str] = None
    SKU: str
    Ubi: Optional[str] = None
    Price_Sell: float
    Price_Buy: float
    Image_URL: Optional[str] = None


class ProductCreate(ProductBase):
    pass


class ProductResponse(ProductBase):
    ID_product: int

    class Config:
        orm_mode = True


class ProductCategoryBase(BaseModel):
    ID_Product: int
    ID_Category: int


class ProductCategoryCreate(ProductCategoryBase):
    pass


class ProductCategoryResponse(ProductCategoryBase):
    class Config:
        orm_mode = True


class UserBase(BaseModel):
    Username: str
    Phone: Optional[str] = None


class UserRegister(UserBase):
    Password: str


class UserLogin(BaseModel):
    Username: str
    Password: str


class UserResponse(UserBase):
    ID_user: int
    User_type: str
    CreatedAt: datetime

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str
    Username: str
    User_type: str
    ID_user: int


class TokenData(BaseModel):
    username: Optional[str] = None


class CartTransactionBase(BaseModel):
    ID_User: int
    ID_Product: int
    Quantity: int
    Payment_method: str
    Order_status: Optional[str] = "Pendiente"


class CartTransactionCreate(CartTransactionBase):
    pass


class CartTransactionUpdate(BaseModel):
    Quantity: int
    Total_amount: float
    Payment_method: str
    Added_Date: Optional[datetime] = None
    Order_date: Optional[datetime] = None
    Order_status: str
    ID_Transaction: int


class CartTransactionResponse(CartTransactionBase):
    ID_Transaction: int
    Total_amount: float
    Added_Date: datetime
    Order_date: Optional[datetime] = None

    class Config:
        orm_mode = True


class NotificationBase(BaseModel):
    ID_Product: int
    Min_Stock: int


class NotificationCreate(NotificationBase):
    pass


class NotificationResponse(NotificationBase):
    ID_Notification: int

    class Config:
        orm_mode = True


class TicketBase(BaseModel):
    ID_client: int
    ID_user: int
    ID_Code: Optional[int] = None
    Issue_details: Optional[str] = None


class TicketCreate(TicketBase):
    pass


class TicketResponse(TicketBase):
    ID_ticket: int
    Created_at: datetime
    Updated_at: Optional[datetime] = None
    Final_Price: float
    Prev_Price: float

    class Config:
        orm_mode = True


class CartTransactionsUpdate(BaseModel):
    ID_user: int
    ID_ticket: int


# Dependencia para obtener la sesión de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Funciones de autenticación
def verify_password(plain_password, hashed_password):
    """Verifica la contraseña."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    """Genera hash de contraseña."""
    return pwd_context.hash(password)


def create_access_token(data: dict):
    """Crea un token JWT sin fecha de expiración."""
    to_encode = data.copy()
    # No añadimos fecha de expiración para que el token no caduque nunca
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Obtiene el usuario actual a partir del token JWT."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Al no tener expiración, omitimos la verificación de la misma
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_exp": False})
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except Exception:
        raise credentials_exception

    user = db.query(User).filter(User.Username == token_data.username).first()
    if user is None:
        raise credentials_exception
    return user


# Rutas
@app.get("/")
def read_root():
    return {"message": "API is running!"}


@app.post("/providers", response_model=ProviderResponse, status_code=status.HTTP_201_CREATED)
def create_provider(provider: ProviderCreate, db: Session = Depends(get_db)):
    """Crea un nuevo proveedor."""
    try:
        db_provider = Provider(**provider.dict())
        db.add(db_provider)
        db.commit()
        db.refresh(db_provider)
        return db_provider
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@app.post("/promocodes", response_model=PromoCodeResponse, status_code=status.HTTP_201_CREATED)
def create_promo(promo: PromoCodeCreate, db: Session = Depends(get_db)):
    """Crea un nuevo código promocional."""
    try:
        db_promo = PromotionalCode(**promo.dict())
        db.add(db_promo)
        db.commit()
        db.refresh(db_promo)
        return db_promo
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@app.post("/clients", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
def create_client(client: ClientCreate, db: Session = Depends(get_db)):
    """Crea un nuevo cliente."""
    try:
        db_client = Client(**client.dict())
        db.add(db_client)
        db.commit()
        db.refresh(db_client)
        return db_client
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@app.get("/categories/{category_id}")
def get_category_name(category_id: int, db: Session = Depends(get_db)):
    """Obtiene el nombre de una categoría por su ID."""
    try:
        category = db.query(Category).filter(Category.ID_Category == category_id).first()
        if not category:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
        return {"name": category.name}
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@app.post("/register", status_code=status.HTTP_201_CREATED)
def register(user: UserRegister, db: Session = Depends(get_db)):
    """Registra un nuevo usuario."""
    if not user.Username or not user.Password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing username or password")

    try:
        # Verificar si el usuario ya existe
        if db.query(User).filter(User.Username == user.Username).first():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already exists")

        # Crear nuevo usuario con contraseña hasheada
        hashed_password = get_password_hash(user.Password)
        db_user = User(
            Username=user.Username,
            Phone=user.Phone,
            Password=hashed_password,
            CreatedAt=datetime.utcnow()
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return {"msg": "User registered successfully"}
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@app.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Obtiene un token de acceso para un usuario."""
    try:
        # Buscar el usuario por nombre de usuario
        user = db.query(User).filter(User.Username == form_data.username).first()

        if not user or not verify_password(form_data.password, user.Password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Crear token JWT sin expiración
        access_token = create_access_token(data={"sub": user.Username})

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "Username": user.Username,
            "User_type": user.User_type,
            "ID_user": user.ID_user
        }
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@app.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    """Inicia sesión de usuario y devuelve un token JWT."""
    try:
        # Buscar el usuario por nombre de usuario
        db_user = db.query(User).filter(User.Username == user.Username).first()

        if not db_user or not verify_password(user.Password, db_user.Password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Crear token JWT sin expiración
        access_token = create_access_token(data={"sub": db_user.Username})

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "Username": db_user.Username,
            "User_type": db_user.User_type,
            "ID_user": db_user.ID_user
        }
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@app.post("/products", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    """Crea un nuevo producto."""
    try:
        db_product = Product(**product.dict())
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        return {"status": "Product created", "ID_Product": db_product.ID_product}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@app.post("/productcategory", status_code=status.HTTP_201_CREATED)
def add_product_category(product_category: ProductCategoryCreate, db: Session = Depends(get_db)):
    """Añade una categoría a un producto."""
    try:
        # Verificar si el producto existe
        product = db.query(Product).filter(Product.ID_product == product_category.ID_Product).first()
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

        # Verificar si la categoría existe
        category = db.query(Category).filter(Category.ID_Category == product_category.ID_Category).first()
        if not category:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

        # Crear la relación producto-categoría
        db_product_category = ProductCategory(**product_category.dict())
        db.add(db_product_category)
        db.commit()
        return {"status": "Category added to product"}
    except Exception as e:
        db.rollback()
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@app.put("/products/{product_id}")
def update_product(product_id: int, product: ProductCreate, db: Session = Depends(get_db)):
    """Actualiza un producto existente."""
    try:
        # Buscar el producto por ID
        db_product = db.query(Product).filter(Product.ID_product == product_id).first()
        if not db_product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

        # Actualizar los campos del producto
        for key, value in product.dict().items():
            setattr(db_product, key, value)

        db.commit()
        db.refresh(db_product)
        return {"status": "Product updated"}
    except Exception as e:
        db.rollback()
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@app.delete("/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    """Elimina un producto existente."""
    try:
        # Primero, eliminar las relaciones del producto en ProductCategories
        db.query(ProductCategory).filter(ProductCategory.ID_Product == product_id).delete()

        # Después, eliminar el producto
        product = db.query(Product).filter(Product.ID_product == product_id).first()
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

        db.delete(product)
        db.commit()
        return {"status": f"Product with ID {product_id} deleted successfully"}
    except Exception as e:
        db.rollback()
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@app.get("/products")
def get_products(category: Optional[int] = None, prod: Optional[int] = None, db: Session = Depends(get_db)):
    """Obtiene productos con filtros opcionales."""
    try:
        query = db.query(Product)

        if prod:
            # Filtrar por ID de producto
            query = query.filter(Product.ID_product == prod)
        elif category:
            # Filtrar por categoría
            query = query.join(ProductCategory).filter(ProductCategory.ID_Category == category)

        products = query.all()

        # Convertir objetos SQLAlchemy a diccionarios
        result = []
        for product in products:
            product_dict = {
                "ID_product": product.ID_product,
                "Product_name": product.Product_name,
                "Quantity": product.Quantity,
                "Color": product.Color,
                "SKU": product.SKU,
                "ID_provider": product.ID_provider,
                "Ubi": product.Ubi,
                "Price_Sell": product.Price_Sell,
                "Price_Buy": product.Price_Buy,
                "Image_URL": product.Image_URL,
                "Image_URL2": product.Image_URL2,
                "Image_URL3": product.Image_URL3
            }
            result.append(product_dict)

        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@app.get("/categories")
def get_categories(db: Session = Depends(get_db)):
    """Obtiene todas las categorías."""
    try:
        categories = db.query(Category).all()

        # Convertir objetos SQLAlchemy a diccionarios
        result = []
        for category in categories:
            category_dict = {
                "ID_Category": category.ID_Category,
                "name": category.name,
                "img_url": category.img_url
            }
            result.append(category_dict)

        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    """Obtiene todos los usuarios."""
    try:
        users = db.query(User).all()

        # Convertir objetos SQLAlchemy a diccionarios
        result = []
        for user in users:
            user_dict = {
                "ID_user": user.ID_user,
                "Username": user.Username,
                "User_type": user.User_type,
                "Phone": user.Phone,
                "CreatedAt": user.CreatedAt,
                "UpdatedAt": user.UpdatedAt
            }
            result.append(user_dict)

        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@app.get("/clients")
def get_clients(db: Session = Depends(get_db)):
    """Obtiene todos los clientes."""
    try:
        clients = db.query(Client).all()

        # Convertir objetos SQLAlchemy a diccionarios
        result = []
        for client in clients:
            client_dict = {
                "ID_client": client.ID_client,
                "Name": client.Name,
                "Address": client.Address,
                "Contact_info": client.Contact_info
            }
            result.append(client_dict)

        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@app.get("/providers")
def get_providers(db: Session = Depends(get_db)):
    """Obtiene todos los proveedores."""
    try:
        providers = db.query(Provider).all()

        # Convertir objetos SQLAlchemy a diccionarios
        result = []
        for provider in providers:
            provider_dict = {
                "ID_provider": provider.ID_provider,
                "Name": provider.Name,
                "Address": provider.Address,
                "Contact_info": provider.Contact_info
            }
            result.append(provider_dict)

        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@app.get("/carttransactions")
def get_cart_transactions(user: Optional[int] = None, db: Session = Depends(get_db)):
    """Obtiene transacciones del carrito con filtro opcional por usuario."""
    try:
        query = db.query(CartTransaction, Product.Image_URL).join(
            Product, CartTransaction.ID_Product == Product.ID_product
        )

        if user:
            query = query.filter(CartTransaction.ID_User == user, CartTransaction.Order_status == 'Pendiente')

        results = query.all()

        # Convertir resultados a diccionarios
        transactions = []
        for cart_transaction, image_url in results:
            transaction_dict = {
                "ID_Transaction": cart_transaction.ID_Transaction,
                "ID_User": cart_transaction.ID_User,
                "ID_Product": cart_transaction.ID_Product,
                "Quantity": cart_transaction.Quantity,
                "Total_amount": cart_transaction.Total_amount,
                "Payment_method": cart_transaction.Payment_method,
                "Added_Date": cart_transaction.Added_Date,
                "Order_date": cart_transaction.Order_date,
                "Order_status": cart_transaction.Order_status,
                "ID_Ticket": cart_transaction.ID_Ticket,
                "Image_URL": image_url
            }
            transactions.append(transaction_dict)

        return transactions
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@app.put("/carttransactions")
def update_cart_transaction(transaction: CartTransactionUpdate, db: Session = Depends(get_db)):
    """Actualiza una transacción de carrito existente."""
    try:
        # Buscar la transacción por ID
        db_transaction = db.query(CartTransaction).filter(
            CartTransaction.ID_Transaction == transaction.ID_Transaction).first()

        if not db_transaction:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart transaction not found")

        # Actualizar campos
        db_transaction.Quantity = transaction.Quantity
        db_transaction.Total_amount = transaction.Total_amount
        db_transaction.Payment_method = transaction.Payment_method
        db_transaction.Added_Date = transaction.Added_Date or db_transaction.Added_Date
        db_transaction.Order_date = transaction.Order_date
        db_transaction.Order_status = transaction.Order_status

        db.commit()
        db.refresh(db_transaction)

        return {"status": "Cart transaction updated"}
    except Exception as e:
        db.rollback()
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@app.post("/notifications", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
def create_notification(notification: NotificationCreate, db: Session = Depends(get_db)):
    """Crea una nueva notificación."""
    try:
        # Verificar si el producto existe
        product = db.query(Product).filter(Product.ID_product == notification.ID_Product).first()
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

        db_notification = Notification(**notification.dict())
        db.add(db_notification)
        db.commit()
        db.refresh(db_notification)

        return db_notification
    except Exception as e:
        db.rollback()
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@app.get("/notifications")
def get_notifications(db: Session = Depends(get_db)):
    """Obtiene todas las notificaciones."""
    try:
        notifications = db.query(Notification).all()

        # Convertir objetos SQLAlchemy a diccionarios
        result = []
        for notification in notifications:
            notification_dict = {
                "ID_Notification": notification.ID_Notification,
                "ID_Product": notification.ID_Product,
                "Min_Stock": notification.Min_Stock
            }
            result.append(notification_dict)

        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@app.put("/notifications/{notification_id}")
def update_notification(notification_id: int, notification: NotificationBase, db: Session = Depends(get_db)):
    """Actualiza una notificación existente."""
    try:
        # Buscar la notificación por ID
        db_notification = db.query(Notification).filter(Notification.ID_Notification == notification_id).first()

        if not db_notification:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")

        # Actualizar campos
        db_notification.Min_Stock = notification.Min_Stock

        db.commit()
        db.refresh(db_notification)

        return {"status": "Notification updated"}
    except Exception as e:
        db.rollback()
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@app.delete("/notifications/{notification_id}")
def delete_notification(notification_id: int, db: Session = Depends(get_db)):
    """Elimina una notificación existente."""
    try:
        # Buscar la notificación por ID
        db_notification = db.query(Notification).filter(Notification.ID_Notification == notification_id).first()

        if not db_notification:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")

        # Eliminar la notificación
        db.delete(db_notification)
        db.commit()

        return {"status": f"Notification with ID {notification_id} deleted successfully"}
    except Exception as e:
        db.rollback()
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@app.post("/cartTransaction", status_code=status.HTTP_201_CREATED)
def create_cart_transaction(transaction: CartTransactionCreate, db: Session = Depends(get_db)):
    """Crea una nueva transacción de carrito."""
    try:
        # Verificar si el usuario existe
        user = db.query(User).filter(User.ID_user == transaction.ID_User).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        # Verificar si el producto existe y obtener su precio
        product = db.query(Product).filter(Product.ID_product == transaction.ID_Product).first()
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

        # Calcular el monto total
        total_amount = product.Price_Sell * transaction.Quantity

        # Crear la transacción
        db_transaction = CartTransaction(
            ID_User=transaction.ID_User,
            ID_Product=transaction.ID_Product,
            Quantity=transaction.Quantity,
            Total_amount=total_amount,
            Payment_method=transaction.Payment_method,
            Order_date=datetime.utcnow().date(),
            Order_status=transaction.Order_status,
            Added_Date=datetime.utcnow()
        )

        db.add(db_transaction)
        db.commit()
        db.refresh(db_transaction)

        return {"ID_Transaction": db_transaction.ID_Transaction}
    except Exception as e:
        db.rollback()
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@app.post("/tickets", status_code=status.HTTP_201_CREATED)
def create_ticket(ticket: TicketCreate, db: Session = Depends(get_db)):
    """Crea un nuevo ticket."""
    pre_price = 0
    final_price = 0
    discount = 0

    try:
        # Verificar si el cliente existe
        client = db.query(Client).filter(Client.ID_client == ticket.ID_client).first()
        if not client:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")

        # Verificar si el usuario existe
        user = db.query(User).filter(User.ID_user == ticket.ID_user).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        # Calcular Pre_Price basado en los elementos del carrito
        pre_price_result = db.query(func.sum(CartTransaction.Total_amount)).filter(
            CartTransaction.ID_User == ticket.ID_user,
            CartTransaction.Order_status == 'Pendiente'
        ).scalar()

        pre_price = pre_price_result if pre_price_result else 0
        final_price = pre_price  # Inicialmente, Final_Price es igual a Pre_Price

        # Si se proporciona un código promocional, aplicar el descuento
        if ticket.ID_Code:
            promo_code = db.query(PromotionalCode).filter(PromotionalCode.ID_Code == ticket.ID_Code).first()
            if promo_code:
                discount = promo_code.Discount
                final_price = pre_price - (pre_price * (discount / 100))

        # Crear el ticket
        db_ticket = Ticket(
            ID_client=ticket.ID_client,
            ID_user=ticket.ID_user,
            ID_Code=ticket.ID_Code,
            Issue_details=ticket.Issue_details,
            Prev_Price=pre_price,
            Final_Price=final_price,
            Created_at=datetime.utcnow()
        )

        db.add(db_ticket)
        db.commit()
        db.refresh(db_ticket)

        return {"ID_ticket": db_ticket.ID_ticket}
    except Exception as e:
        db.rollback()
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@app.put("/carttransactions/update")
def update_cart_transactions(update: CartTransactionsUpdate, db: Session = Depends(get_db)):
    """Actualiza transacciones de carrito para asociarlas con un ticket."""
    try:
        # Verificar si el usuario existe
        user = db.query(User).filter(User.ID_user == update.ID_user).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        # Verificar si el ticket existe
        ticket = db.query(Ticket).filter(Ticket.ID_ticket == update.ID_ticket).first()
        if not ticket:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

        # Actualizar las transacciones del carrito
        db.query(CartTransaction).filter(
            CartTransaction.ID_User == update.ID_user,
            CartTransaction.Order_status == 'Pendiente'
        ).update({
            "ID_Ticket": update.ID_ticket,
            "Order_status": 'Completado'
        })

        db.commit()

        return {"status": "Cart transactions updated"}
    except Exception as e:
        db.rollback()
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@app.get("/tickets/{ticket_id}")
def get_ticket_details(ticket_id: int, db: Session = Depends(get_db)):
    """Obtiene los detalles de un ticket específico."""
    try:
        # Obtener el ticket con información relacionada
        ticket_query = db.query(
            Ticket.ID_ticket,
            Ticket.ID_client,
            Ticket.ID_user,
            Ticket.Issue_details,
            Ticket.Created_at,
            Ticket.Updated_at,
            Ticket.ID_Code,
            Ticket.Final_Price,
            Ticket.Prev_Price,
            Client.Name.label('client_name'),
            User.Username.label('user_name')
        ).join(
            Client, Ticket.ID_client == Client.ID_client
        ).join(
            User, Ticket.ID_user == User.ID_user
        ).filter(
            Ticket.ID_ticket == ticket_id
        ).first()

        if not ticket_query:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

        # Convertir a diccionario
        ticket = {
            "ID_ticket": ticket_query.ID_ticket,
            "ID_client": ticket_query.ID_client,
            "ID_user": ticket_query.ID_user,
            "Issue_details": ticket_query.Issue_details,
            "Created_at": ticket_query.Created_at,
            "Updated_at": ticket_query.Updated_at,
            "ID_Code": ticket_query.ID_Code,
            "Final_Price": ticket_query.Final_Price,
            "Prev_Price": ticket_query.Prev_Price,
            "client_name": ticket_query.client_name,
            "user_name": ticket_query.user_name
        }

        # Obtener las transacciones del carrito asociadas con el ticket
        cart_transactions_query = db.query(
            CartTransaction.ID_Transaction,
            CartTransaction.ID_User,
            CartTransaction.ID_Product,
            CartTransaction.Quantity,
            CartTransaction.Total_amount,
            CartTransaction.Payment_method,
            CartTransaction.Added_Date,
            CartTransaction.Order_date,
            CartTransaction.Order_status,
            Product.Product_name
        ).join(
            Product, CartTransaction.ID_Product == Product.ID_product
        ).filter(
            CartTransaction.ID_Ticket == ticket_id
        ).all()

        # Convertir a lista de diccionarios
        cart_transactions = []
        for ct in cart_transactions_query:
            cart_transaction = {
                "ID_Transaction": ct.ID_Transaction,
                "ID_User": ct.ID_User,
                "ID_Product": ct.ID_Product,
                "Quantity": ct.Quantity,
                "Total_amount": ct.Total_amount,
                "Payment_method": ct.Payment_method,
                "Added_Date": ct.Added_Date,
                "Order_date": ct.Order_date,
                "Order_status": ct.Order_status,
                "Product_name": ct.Product_name
            }
            cart_transactions.append(cart_transaction)

        # Agregar las transacciones al ticket
        ticket["cart_transactions"] = cart_transactions

        return ticket
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@app.get("/dashboard/total_sales")
def get_total_sales(db: Session = Depends(get_db)):
    """Dashboard: Obtiene el total de ventas."""
    try:
        total_sales = db.query(func.sum(Ticket.Final_Price)).scalar() or 0
        return {"Venta_Total": total_sales}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@app.get("/dashboard/top_items")
def get_top_items(db: Session = Depends(get_db)):
    """Dashboard: Obtiene los 10 productos más vendidos."""
    try:
        # Subconsulta para obtener el conteo de productos vendidos
        top_items_query = db.query(
            CartTransaction.ID_Product,
            Product.Product_name,
            func.count(CartTransaction.ID_Product).label('count')
        ).join(
            Product, CartTransaction.ID_Product == Product.ID_product
        ).group_by(
            CartTransaction.ID_Product, Product.Product_name
        ).order_by(
            func.count(CartTransaction.ID_Product).desc()
        ).limit(10).all()

        # Convertir a lista de diccionarios
        top_items = []
        for item in top_items_query:
            top_item = {
                "ID_Product": item.ID_Product,
                "Product_name": item.Product_name,
                "count": item.count
            }
            top_items.append(top_item)

        return top_items
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@app.get("/dashboard/top_clients")
def get_top_clients(db: Session = Depends(get_db)):
    """Dashboard: Obtiene los 10 clientes más frecuentes."""
    try:
        # Subconsulta para obtener el conteo de clientes con más tickets
        top_clients_query = db.query(
            Ticket.ID_client,
            Client.Name,
            func.count(Ticket.ID_client).label('count')
        ).join(
            Client, Ticket.ID_client == Client.ID_client
        ).group_by(
            Ticket.ID_client, Client.Name
        ).order_by(
            func.count(Ticket.ID_client).desc()
        ).limit(10).all()

        # Convertir a lista de diccionarios
        top_clients = []
        for client in top_clients_query:
            top_client = {
                "ID_client": client.ID_client,
                "Name": client.Name,
                "count": client.count
            }
            top_clients.append(top_client)

        return top_clients
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)