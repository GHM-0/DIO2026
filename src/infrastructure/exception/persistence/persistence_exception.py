# src/infrastructure/exception/persistence/persistence_exception.py
from infrastructure.exception.infra_exception import InfraException

class PersistenceException(InfraException):
    """Base para falhas em operações de DML (Runtime/Persistence)."""
    pass

class IntegrityException(PersistenceException):
    """Específica para violações de restrições (ex: Unique Key)."""
    pass
