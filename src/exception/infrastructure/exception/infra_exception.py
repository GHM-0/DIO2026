# src/infrastructure/database/infra_exception.py
from exception.core.exception.base_exception import CustomException

class InfraException(CustomException):
    """Base para todas as exceções da camada de infraestrutura."""