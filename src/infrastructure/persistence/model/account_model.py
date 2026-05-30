# src.infrastructure.database.model.account_model.py

from datetime import datetime
from decimal import Decimal

from sqlalchemy import Integer, Numeric, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.functions import func

from infrastructure.persistence.model.base_model import Base


class AccountModel(Base):
    """
    Modelo SQLAlchemy para a entidade Account.
    Mapeia para a tabela 'accounts'.
    """

    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, unique=False)
    balance: Mapped[Decimal] = mapped_column(Numeric(precision=10, scale=2), nullable=False, default=Decimal("0.00"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
