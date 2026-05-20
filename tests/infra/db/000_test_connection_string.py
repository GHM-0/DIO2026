# tests/infra/db/000_test_connection_string.py

import pytest
from infrastructure.config import settings

@pytest.mark.parametrize("variable, name", [
    (settings.MYSQL_HOST, "HOST"),
    (settings.MYSQL_PORT, "PORT"),
    (settings.MYSQL_USER, "USER"),
    (settings.MYSQL_PASSWORD, "PASSWORD"),
    (settings.MYSQL_DATABASE, "DATABASE"),
    (settings.MYSQL_ROOT_PASSWORD, "ROOT_PASSWORD"),
])
def test_env_variables_presence(variable, name):
    """Garante que as configurações essenciais foram carregadas do ambiente."""
    assert variable is not None, f"{name} não configurado nas variáveis de ambiente"
    assert str(variable).strip() != "", f"{name} está presente mas vazio"


def test_debug_url_connection_by_user(db_url):
    """
    Valida se a URL de conexão assíncrona gerada pelo sistema coincide com 
    a construção esperada a partir das variáveis de ambiente.
    """

    # Validação da Injeção: O settings real deve ser igual à fixture de auxílio
    assert str(settings.USER_ASYNC) == db_url


def test_debug_url_connections_by_root(db_root_url):

    assert str(settings.ROOT_SYNC_SETUP) == db_root_url
