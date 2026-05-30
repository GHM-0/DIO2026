# src.application.use_case.exception.create_transaction_exception.py

from exception.application.use_case.exception.usecase_exception import UseCaseException


class CreateTransactionException(UseCaseException):
    pass

class UserNotAuthorizedException(CreateTransactionException):
    pass

class TransactionNaoPodeSerCriadoException(CreateTransactionException):
    pass