from fastapi import FastAPI, WebSocket
from starlette.middleware.cors import CORSMiddleware

from database import Base, engine
from routes import auth, pos, payments, dashboard, users

# Inicializar base de datos
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AKARI API",
    description="API para el sistema AKARI",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite cualquier origen (puedes restringirlo a tu dominio)
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permite todos los encabezados
)


# Incluir routers
app.include_router(auth.router, prefix="/auth")
app.include_router(pos.router, prefix="/pos")
app.include_router(payments.router, prefix="/payments")
app.include_router(dashboard.router, prefix="/dashboard")
app.include_router(users.router, prefix="/users")

# WebSocket
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message received: {data}")

# Health check
@app.get("/")
def health_check():
    return {"message": "API is running"}