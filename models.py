from sqlalchemy import Column, Integer, String, Numeric, Date, DateTime, Boolean, ForeignKey, func
from sqlalchemy.orm import relationship
from database import Base

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
    Price_Sell = Column(Numeric(10, 2))
    Price_Buy = Column(Numeric(10, 2))
    Image_URL = Column(String(255))
    Image_URL2 = Column(String(255))
    Image_URL3 = Column(String(255))

    # Relaciones
    provider = relationship("Provider", back_populates="products")
    categories = relationship("ProductCategory", back_populates="product")
    notifications = relationship("Notification", back_populates="product")
    cart_transactions = relationship("CartTransaction", back_populates="product")


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
    Discount = Column(Numeric(10, 2))
    ExpirationDate = Column(Date)
    IsActive = Column(Boolean, default=True)

    # Relaciones
    tickets = relationship("Ticket", back_populates="promotional_code")


class Provider(Base):
    __tablename__ = "Providers"

    ID_provider = Column(Integer, primary_key=True, index=True)
    Name = Column(String(255))

    # Relaciones
    products = relationship("Product", back_populates="provider")


class User(Base):
    __tablename__ = "Users"

    ID_user = Column(Integer, primary_key=True, index=True)
    Username = Column(String(255))
    Password = Column(String(255))
    User_type = Column(String(50), default="vendedor")
    UpdatedAt = Column(DateTime)
    CreatedAt = Column(DateTime, default=func.now(), nullable=False)
    Phone = Column(String(50))

    # Relaciones
    tickets = relationship("Ticket", back_populates="user")
    cart_transactions = relationship("CartTransaction", back_populates="user")


class CartTransaction(Base):
    __tablename__ = "CartTransactions"

    ID_Transaction = Column(Integer, primary_key=True, index=True)
    ID_User = Column(Integer, ForeignKey("Users.ID_user"))
    ID_Product = Column(Integer, ForeignKey("Products.ID_product"))
    Quantity = Column(Integer)
    Total_amount = Column(Numeric(10, 2))
    Payment_method = Column(String(100))
    Order_date = Column(Date)
    Order_status = Column(String(50))
    ID_Ticket = Column(Integer)

    # Relaciones
    user = relationship("User", back_populates="cart_transactions")
    product = relationship("Product", back_populates="cart_transactions")


class Ticket(Base):
    __tablename__ = "Tickets"

    ID_ticket = Column(Integer, primary_key=True, index=True)
    ID_client = Column(Integer, ForeignKey("Clients.ID_client"))
    ID_user = Column(Integer, ForeignKey("Users.ID_user"))
    Issue_details = Column(String(1000))
    Created_at = Column(DateTime, default=func.now())
    Updated_at = Column(DateTime)
    ID_Code = Column(Integer, ForeignKey("PromotionalCodes.ID_Code"))
    ID_Cart = Column(Integer)
    Final_Price = Column(Numeric(10, 2))
    Prev_Price = Column(Numeric(10, 2))

    # Relaciones
    client = relationship("Client", back_populates="tickets")
    user = relationship("User", back_populates="tickets")
    promotional_code = relationship("PromotionalCode", back_populates="tickets")