from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime


# Modelos Pydantic para validación
class ProductBase(BaseModel):
    Product_name: str
    Quantity: int
    Color: str
    SKU: str
    ID_provider: int
    Price_Sell: float
    Price_Buy: float
    Image_URL: str
    Image_URL2: Optional[str] = None
    Image_URL3: Optional[str] = None


class ProductResponse(ProductBase):
    ID_product: int

    class Config:
        from_attributes = True


class CategoryBase(BaseModel):
    name: str
    img_url: Optional[str] = None


class CategoryResponse(CategoryBase):
    ID_Category: int

    class Config:
        from_attributes = True


class ProductCategoryBase(BaseModel):
    ID_Product: int
    ID_Category: int


class NotificationBase(BaseModel):
    ID_Product: int
    Min_Stock: int


class NotificationResponse(NotificationBase):
    ID_Notification: int

    class Config:
        from_attributes = True


class ProviderBase(BaseModel):
    Name: str
    Address: Optional[str] = None
    Contact_info: Optional[str] = None


class ProviderResponse(ProviderBase):
    ID_provider: int

    class Config:
        from_attributes = True


# Modelos Pydantic para validación
class UserCreate(BaseModel):
    Username: str
    Phone: str
    Password: str


class UserLogin(BaseModel):
    Username: str
    Password: str


class Token(BaseModel):
    access_token: str
    Username: str
    User_type: str
    ID_user: int


# Modelos Pydantic para validación
class CartTransactionBase(BaseModel):
    ID_User: int
    ID_Product: int
    Quantity: int
    Payment_method: str = None
    Order_status: str = "Pendiente"


class CartTransactionResponse(CartTransactionBase):
    ID_Transaction: int
    Total_amount: float
    Order_date: Optional[datetime] = None

    class Config:
        from_attributes = True


class TicketBase(BaseModel):
    ID_client: int
    ID_user: int
    ID_Code: Optional[int] = None
    Issue_details: Optional[str] = None


class TicketResponse(TicketBase):
    ID_ticket: int
    Prev_Price: float
    Final_Price: float
    Created_at: datetime
    Updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TicketDetailResponse(TicketResponse):
    client_name: str
    user_name: str
    cart_transactions: List[CartTransactionResponse]


class ClientBase(BaseModel):
    Name: str
    Address: Optional[str] = None
    Contact_info: Optional[str] = None


class ClientResponse(ClientBase):
    ID_client: int

    class Config:
        from_attributes = True


class PromotionalCodeBase(BaseModel):
    Code: str
    Discount: float
    ExpirationDate: datetime
    IsActive: bool = True


class PromotionalCodeResponse(PromotionalCodeBase):
    ID_Code: int

    class Config:
        from_attributes = True


class CartUpdateRequest(BaseModel):
    ID_user: int
    ID_ticket: int


# Modelos Pydantic para respuestas
class TotalSalesResponse(BaseModel):
    Venta_Total: float


class TopItemResponse(BaseModel):
    ID_Product: int
    Product_name: str
    count: int


class TopClientResponse(BaseModel):
    ID_client: int
    Name: str
    count: int


class UserBase(BaseModel):
    Username: str
    Phone: Optional[str] = None
    User_type: str = "vendedor"


class UserCreate(UserBase):
    Password: str


class UserResponse(UserBase):
    ID_user: int
    CreatedAt: datetime
    UpdatedAt: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    Username: Optional[str] = None
    Phone: Optional[str] = None
    Password: Optional[str] = None
    User_type: Optional[str] = None
