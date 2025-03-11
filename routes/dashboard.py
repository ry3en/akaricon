from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List

from dependences import get_db
from models import Ticket, CartTransaction, Product, Client

from schemas import TotalSalesResponse, TopItemResponse, TopClientResponse

# Instancia de router
router = APIRouter(tags=["Dashboard"])


# Endpoint para obtener el total de ventas
@router.get("/total_sales", response_model=TotalSalesResponse)
def get_total_sales(db: Session = Depends(get_db)):
    total_sales = db.query(func.sum(Ticket.Final_Price)).scalar() or 0
    return {"Venta_Total": total_sales}


# Endpoint para obtener los 10 productos más vendidos
@router.get("/top_items", response_model=List[TopItemResponse])
def get_top_items(db: Session = Depends(get_db)):
    top_items = db.query(
        CartTransaction.ID_Product,
        Product.Product_name,
        func.count(CartTransaction.ID_Product).label("count")
    ).join(
        Product, CartTransaction.ID_Product == Product.ID_product
    ).group_by(
        CartTransaction.ID_Product, Product.Product_name
    ).order_by(
        desc("count")
    ).limit(10).all()

    return [{"ID_Product": item[0], "Product_name": item[1], "count": item[2]} for item in top_items]


# Endpoint para obtener los 10 clientes principales
@router.get("/top_clients", response_model=List[TopClientResponse])
def get_top_clients(db: Session = Depends(get_db)):
    top_clients = db.query(
        Ticket.ID_client,
        Client.Name,
        func.count(Ticket.ID_client).label("count")
    ).join(
        Client, Ticket.ID_client == Client.ID_client
    ).group_by(
        Ticket.ID_client, Client.Name
    ).order_by(
        desc("count")
    ).limit(10).all()

    return [{"ID_client": client[0], "Name": client[1], "count": client[2]} for client in top_clients]


# Endpoint para obtener estadísticas por categoría
@router.get("/category_stats")
def get_category_stats(db: Session = Depends(get_db)):
    # Implementación pendiente basada en los requisitos específicos
    pass


# Endpoint para obtener ventas por mes
@router.get("/monthly_sales")
def get_monthly_sales(db: Session = Depends(get_db)):
    # Implementación pendiente basada en los requisitos específicos
    pass