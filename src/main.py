# src.main.py
from fastapi import FastAPI
from infrastructure.lifecycle import Lifespan
from presentation.api.controllers import account_controller, auth_controller, transaction_controller

# FastAPI Ciclo de vida
app = FastAPI(lifespan=Lifespan)

# Rotas
app.include_router(auth_controller.router)
app.include_router(account_controller.router)
app.include_router(transaction_controller.router)
