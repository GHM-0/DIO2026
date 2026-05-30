# tests.db.001_test_database_connection

import pytest

from infrastructure.config import settings

from sqlalchemy import text

from exception.infrastructure.exception.database.database_exceptions import DataBaseConnectionException
from infrastructure.persistence.async_sqlalchemy_database import AsyncSqlAlchemyDatabase


@pytest.mark.asyncio
async def test_database_exists_by_user(db_instance: AsyncSqlAlchemyDatabase):
    """
    Valida se a aplicação consegue se autenticar e se o banco de dados
    especificado nas configurações está visível para o usuário da aplicação.
    Nota: Assume que o ambiente (DB e Usuário) já foi provisionado.
    """

    try:
        is_healthy = await db_instance.health_check()
        assert is_healthy is True, "O serviço de banco de dados não respondeu ao health_check."

        async with db_instance.get_session() as session:
            result = await session.execute(text("SELECT DATABASE();"))
            current_db = result.scalar()

            assert current_db == settings.MYSQL_DATABASE, f"Esperado banco {settings.MYSQL_DATABASE}, mas conectado a {current_db}."
    except Exception as e:
        raise DataBaseConnectionException(f"Falha técnica na conexão: {e}") from e