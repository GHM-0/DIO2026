# src.infrastructure.database.model.transaction_model.py
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Integer, Numeric, DateTime, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.functions import func

from infrastructure.persistence.model.base_model import Base

class TransactionModel(Base):
    """
        Modelo SQLAlchemy para a entidade Transaction.
        Mapeia para a tabela 'transactions'.
        """
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    account_orig_id: Mapped[int] = mapped_column(Integer, ForeignKey("accounts.id"), nullable=False)
    account_dest_id: Mapped[int] = mapped_column(Integer, ForeignKey("accounts.id"), nullable=False)
    transaction_type: Mapped[str] = mapped_column(String(25), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(precision=10, scale=2), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=func.now())