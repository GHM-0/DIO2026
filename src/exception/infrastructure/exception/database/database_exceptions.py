# src.infrastructure.database.database_exceptions.py

from exception.infrastructure.exception.infra_exception import InfraException


class DatabaseException(InfraException):
    """ Sinaliza falhas técnicas genéricas de banco de dados.
    Ex: Timeouts, erros de sintaxe SQL, quedas de pool.
    """
    pass

class DataBaseConnectionException(DatabaseException):
    """ Sinaliza falha crítica na tentativa de estabelecer conexão.
    Exigência de Auditoria: Passar o Host/Driver no parâmetro 'entity'.
    """
    pass