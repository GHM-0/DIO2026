# src.infrastructure.lifecycle.py

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI

from infrastructure.config import settings
from infrastructure.persistence.async_sqlalchemy_database import AsyncSqlAlchemyDatabase

db_instance = AsyncSqlAlchemyDatabase(database_url=settings.USER_ASYNC) # type: ignore[attr-defined]

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    await db_instance.connect()
    yield
    await db_instance.disconnect()
