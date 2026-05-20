# src.infrastructure.lifecycle.py
from contextlib import asynccontextmanager
from fastapi import FastAPI

from infrastructure.config import settings
from infrastructure.persistence.async_sqlalchemy_database import AsyncSqlAlchemyDatabase

db_instance = AsyncSqlAlchemyDatabase(database_url=settings.USER_ASYNC)

# Controle do Ciclo de Vida do APP
@asynccontextmanager
async def Lifespan(app: FastAPI):
    # Conecta o banco de dados ao iniciar a aplicação
    await db_instance.connect()
    
    yield
    
    # Desconecta o banco de dados ao encerrar a aplicação
    await db_instance.disconnect()
