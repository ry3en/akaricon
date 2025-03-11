from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from decimal import Decimal
from sqlalchemy import func

from dependences import get_db
from models import CartTransaction, Product, Ticket, Client, User, PromotionalCode
from schemas import CartTransactionResponse, CartTransactionBase, TicketResponse, TicketBase, CartUpdateRequest, \
    ClientResponse, ClientBase, PromotionalCodeBase, PromotionalCodeResponse, TicketDetailResponse

# Instancia de router
router = APIRouter(tags=["Payments"])


# Endpoints para CartTransactions
@router.post("/cart", response_model=CartTransactionResponse, status_code=status.HTTP_201_CREATED)
def create_cart_transaction(transaction: CartTransactionBase, db: Session = Depends(get_db)):
    # Verificar si el producto existe y obtener su precio
    product = db.query(Product).filter(Product.ID_product == transaction.ID_Product).first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    # Calcular el monto total
    total_amount = product.Price_Sell * transaction.Quantity

    # Crear la transacción
    db_transaction = CartTransaction(
        ID_User=transaction.ID_User,
        ID_Product=transaction.ID_Product,
        Quantity=transaction.Quantity,
        Total_amount=total_amount,
        Payment_method=transaction.Payment_method,
        Order_date=datetime.now(),
        Order_status=transaction.Order_status
    )

    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)

    return db_transaction


@router.get("/cart", response_model=List[CartTransactionResponse])
def get_cart_transactions(user: Optional[int] = None, db: Session = Depends(get_db)):
    if user:
        transactions = db.query(CartTransaction).filter(
            CartTransaction.ID_User == user,
            CartTransaction.Order_status == "Pendiente"
        ).all()
    else:
        transactions = db.query(CartTransaction).all()

    return transactions


@router.put("/cart", status_code=status.HTTP_200_OK)
def update_cart_transactions(data: CartUpdateRequest, db: Session = Depends(get_db)):
    # Actualizar todas las transacciones pendientes del usuario con el ID del ticket
    result = db.query(CartTransaction).filter(
        CartTransaction.ID_User == data.ID_user,
        CartTransaction.Order_status == "Pendiente"
    ).update({
        "ID_Ticket": data.ID_ticket,
        "Order_status": "Completado"
    })

    if result == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No pending cart transactions found for this user"
        )

    db.commit()

    return {"status": "Cart transactions updated", "count": result}


# Endpoints para Tickets
@router.post("/tickets", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
def create_ticket(ticket: TicketBase, db: Session = Depends(get_db)):
    # Calcular el precio previo (suma de transacciones pendientes)
    pre_price = db.query(func.sum(CartTransaction.Total_amount)).filter(
        CartTransaction.ID_User == ticket.ID_user,
        CartTransaction.Order_status == "Pendiente"
    ).scalar() or 0

    final_price = pre_price

    # Si hay un código promocional, aplicar descuento
    if ticket.ID_Code:
        promo_code = db.query(PromotionalCode).filter(PromotionalCode.ID_Code == ticket.ID_Code).first()

        if promo_code and promo_code.IsActive:
            # Verificar si el código ha expirado
            if promo_code.ExpirationDate and promo_code.ExpirationDate < datetime.now():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Promotional code has expired"
                )

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
        Created_at=datetime.now()
    )

    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)

    return db_ticket


@router.get("/tickets/{ticket_id}", response_model=TicketDetailResponse)
def get_ticket_details(ticket_id: int, db: Session = Depends(get_db)):
    # Obtener el ticket con las relaciones
    ticket = db.query(Ticket).filter(Ticket.ID_ticket == ticket_id).first()

    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )

    # Obtener detalles del cliente y usuario
    client = db.query(Client).filter(Client.ID_client == ticket.ID_client).first()
    user = db.query(User).filter(User.ID_user == ticket.ID_user).first()

    # Obtener transacciones del carrito
    cart_transactions = db.query(CartTransaction).filter(CartTransaction.ID_Ticket == ticket_id).all()

    # Construir respuesta
    response = {
        **ticket.__dict__,
        "client_name": client.Name if client else "",
        "user_name": user.Username if user else "",
        "cart_transactions": cart_transactions
    }

    return response


# Endpoints para Clientes
@router.post("/clients", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
def create_client(client: ClientBase, db: Session = Depends(get_db)):
    db_client = Client(
        Name=client.Name,
        Address=client.Address,
        Contact_info=client.Contact_info
    )

    db.add(db_client)
    db.commit()
    db.refresh(db_client)

    return db_client


@router.get("/clients", response_model=List[ClientResponse])
def get_clients(db: Session = Depends(get_db)):
    clients = db.query(Client).all()
    return clients


# Endpoints para Códigos Promocionales
@router.post("/promocodes", response_model=PromotionalCodeResponse, status_code=status.HTTP_201_CREATED)
def create_promo_code(promo: PromotionalCodeBase, db: Session = Depends(get_db)):
    db_promo = PromotionalCode(
        Code=promo.Code,
        Discount=promo.Discount,
        ExpirationDate=promo.ExpirationDate,
        IsActive=promo.IsActive
    )

    db.add(db_promo)
    db.commit()
    db.refresh(db_promo)

    return db_promo