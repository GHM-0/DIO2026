# src.main.py

from fastapi import FastAPI
from infrastructure.lifecycle import lifespan
from presentation.api.controllers import account_controller, auth_controller, transaction_controller

# FastAPI Ciclo de vida
app = FastAPI(lifespan=lifespan)

# Rotas
@app.get("/")
async def read_root() -> dict[str,str]:
    return {"message": "Welcome to DIO-BANK API"}

app.include_router(auth_controller.router)
app.include_router(account_controller.router)
app.include_router(transaction_controller.router)
