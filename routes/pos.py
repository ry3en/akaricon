from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from dependences import get_db
from models import Product, Category, ProductCategory, CartTransaction, Notification, Provider
from schemas import ProductResponse, ProductBase, CategoryResponse, ProductCategoryBase, NotificationResponse, \
    NotificationBase, ProviderResponse, ProviderBase

# Instancia de router
router = APIRouter(tags=["Point of Sale"])


# Endpoints para Productos
@router.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(product: ProductBase, db: Session = Depends(get_db)):
    db_product = Product(
        Product_name=product.Product_name,
        Quantity=product.Quantity,
        Color=product.Color,
        SKU=product.SKU,
        ID_provider=product.ID_provider,
        Price_Sell=product.Price_Sell,
        Price_Buy=product.Price_Buy,
        Image_URL=product.Image_URL,
        Image_URL2=product.Image_URL2,
        Image_URL3=product.Image_URL3
    )

    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


@router.get("/products", response_model=List[ProductResponse])
def get_products(category: Optional[int] = None, prod: Optional[int] = None, db: Session = Depends(get_db)):
    if prod:
        products = db.query(Product).filter(Product.ID_product == prod).all()
    elif category:
        products = db.query(Product).join(ProductCategory).filter(ProductCategory.ID_Category == category).all()
    else:
        products = db.query(Product).all()

    return products


@router.put("/products/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, product: ProductBase, db: Session = Depends(get_db)):
    db_product = db.query(Product).filter(Product.ID_product == product_id).first()

    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    for field, value in product.dict().items():
        setattr(db_product, field, value)

    db.commit()
    db.refresh(db_product)
    return db_product


@router.delete("/products/{product_id}", status_code=status.HTTP_200_OK)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    # Primero eliminar las referencias en ProductCategories
    db.query(ProductCategory).filter(ProductCategory.ID_Product == product_id).delete()

    # Ahora eliminar el producto
    product = db.query(Product).filter(Product.ID_product == product_id).first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    db.delete(product)
    db.commit()

    return {"status": f"Product with ID {product_id} deleted successfully"}


# Endpoints para Categorías
@router.get("/categories", response_model=List[CategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    categories = db.query(Category).all()
    return categories


@router.get("/categories/{category_id}", response_model=CategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.ID_Category == category_id).first()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    return category


# Endpoint para ProductCategory (agregar un producto a una categoría)
@router.post("/productcategory", status_code=status.HTTP_201_CREATED)
def add_product_category(data: ProductCategoryBase, db: Session = Depends(get_db)):
    # Verificar si el producto existe
    product = db.query(Product).filter(Product.ID_product == data.ID_Product).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    # Verificar si la categoría existe
    category = db.query(Category).filter(Category.ID_Category == data.ID_Category).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    # Crear la relación
    db_product_category = ProductCategory(
        ID_Product=data.ID_Product,
        ID_Category=data.ID_Category
    )

    db.add(db_product_category)
    db.commit()

    return {"status": "Category added to product"}


# Endpoints para Notificaciones
@router.post("/notifications", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
def create_notification(notification: NotificationBase, db: Session = Depends(get_db)):
    db_notification = Notification(
        ID_Product=notification.ID_Product,
        Min_Stock=notification.Min_Stock
    )

    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    return db_notification


@router.get("/notifications", response_model=List[NotificationResponse])
def get_notifications(db: Session = Depends(get_db)):
    notifications = db.query(Notification).all()
    return notifications


@router.put("/notifications/{notification_id}", response_model=NotificationResponse)
def update_notification(notification_id: int, notification: NotificationBase, db: Session = Depends(get_db)):
    db_notification = db.query(Notification).filter(Notification.ID_Notification == notification_id).first()

    if not db_notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )

    db_notification.ID_Product = notification.ID_Product
    db_notification.Min_Stock = notification.Min_Stock

    db.commit()
    db.refresh(db_notification)
    return db_notification


@router.delete("/notifications/{notification_id}", status_code=status.HTTP_200_OK)
def delete_notification(notification_id: int, db: Session = Depends(get_db)):
    notification = db.query(Notification).filter(Notification.ID_Notification == notification_id).first()

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )

    db.delete(notification)
    db.commit()

    return {"status": f"Notification with ID {notification_id} deleted successfully"}


# Endpoints para Proveedores
@router.post("/providers", response_model=ProviderResponse, status_code=status.HTTP_201_CREATED)
def create_provider(provider: ProviderBase, db: Session = Depends(get_db)):
    db_provider = Provider(
        Name=provider.Name,
        Address=provider.Address,
        Contact_info=provider.Contact_info
    )

    db.add(db_provider)
    db.commit()
    db.refresh(db_provider)
    return db_provider


@router.get("/providers", response_model=List[ProviderResponse])
def get_providers(db: Session = Depends(get_db)):
    providers = db.query(Provider).all()
    return providers