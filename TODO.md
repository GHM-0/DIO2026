[Clean Architecture - Layered]

[Core]

    [Domain]                 
        Entity                                          # [DONE] FileName = {class_name}_entity.py
            Account                                     # Com métodos de domínio deposit/withdraw
            Transaction (Abstract)                      # [DONE] Com validação de imutabilidade
            Credit                                      # [DONE] Implementa Transaction
            Debit                                       # [DONE] Implementa Transaction
            Transference                                # [DONE] Implementa Transaction
            User*                                       -> Design: user_id externo via Auth JWT
    
        Value_Object                                    # [DONE] FileName = {class_name}.py
            Amount                                      # Validação de valores SEMPRE positivos
            Balance                                     # Controle de saldo
            TransactionType                             # Enum Deposit/Withdraw
            TransactionStatus                           # [DONE] Enum para status da transação
            TransactionResult                           # [DONE] Value Object para o resultado da transação

        Port:                                           # [DONE] 
            IAsyncDatabase                              # Abstração de SGBD (database_interface.py)
            IAsyncDbTransactionUnit                     # Interface de UoW (async_db_transaction_unit_interface.py)
            IAccountRepository, ITransactionRepository  # Interfaces de Repositório (port/repository/*)

[Application]
    
    dto: Data transfer Objects (Request/Response)       # [DONE]  FileName = {class_name}_dto.py
        login_dto.py
        account_dto.py
        transaction_dto.py
        account_statement_dto.py

    use_case:                                           # [DONE] Implementados com Unit of Work
        create_account.py                               # Em account/
        create_transaction.py                           # Em transaction/
        get_account_statement.py                        # Em use_case/ (Geração de extrato)
        get_account_by_id.py / user_id.py               # Em account/
        auth/login.py                                   # Em auth/
        get_transaction_by_id.py                        # Em transaction/
        get_transaction_by_account_id.py                # Em transaction/

[Presentation]

    api/controllers:                                    # [DONE] Controladores FastAPI com DI
            account_controller.py                       # [DONE] Rotas /accounts, extratos (Atenção: Import path)
            auth_controller.py                          # [DONE] Rotas /auth
            transaction_controller.py                   # [DONE] Registrado em main.py

[Infrastructure]

    config.py:                                          # [DONE] Gestão de .env e Perfis DB via Pydantic Settings
    lifecycle.py:                                       # [DONE] Singleton do db_instance para FastAPI (Lifespan)

    [security]
        security.py                                     # [DONE] JWT Provider (security.py)
    
    [persistence]                                       # [DONE]
        database_profiles.py                            # POPO de Metadados de Perfil
        async_sqlalchemy_database.py                    # Gestão de Engine/Pool (NullPool p/ Testes)
        sqlalchemy_transaction_unit.py                  # Implementação AsyncSqlAlchemyTransactionUnit

        [model]                                         # FileName = {class_name}_model.py
            base_model.py
            account_model.py
            transaction_model.py
            models_module.py                            # Agregador de modelos para o Alembic

        [repository]                                    # FileName = {class_name}_repository_impl.py
            account_repository_impl.py
            transaction_repository_impl.py

[Exceptions]                                            # [DONE] {class_name}_exception.py 

    base_exception.py                                             
    [core]  domain
        [entity]
            account, transaction
        [value_object] amount, balance
    [application]                                     
        use_case
    [presentation]                                    
        infra, database, persistence

[tests]       

    conftest.py                                         # [DONE] Fixtures e Mocking de Engine

    [helper]
        integration_fixtures.py                         # Fixtures de Seed de dados

    Estrutura:
        [application] -> dto, use_case
        [core]        -> domain, entity, value_object
        [infra]       -> db, repository, security
        [presentation]                                  # [DONE] Implementar testes de controladores

[ROOT] 

  - src/main.py (Entry Point)                           # [DONE] Registra Auth e Account e Transaction
  - alembic.ini                                         # [DONE] Configuração de roteamento de Migrações
  - [pytest] pytest.ini                                 # [DONE] Configuração de descoberta
  - [migrations] env.py, script.py.mako                 # [DONE] Gestão de Versões (Alembic)
  - [utils] setup-db.py, 000_TEMPLATE_DB.sql            # [DONE] Scripts de Bootstrap e Esquema SQL Inicial
  - [env] .env                                          # [DONE] 
  - [dependency_manager] pyproject.toml, uv.lock        # [DONE] 
  - [docker] Dockerfile, docker-compose.yml             # [DONE] 
  - [Makefile] Alvos: dev, dev-db, setup, tests, clean  # [DONE]
  - README.md                                           # [DONE] 
  - TODO.md (Este arquivo)                              # [DONE] 

[CONFORMITY CHECK - README.md]                          # [DONE]
  - Validação de saldo: Implementar trava para saques superiores ao saldo atual no Use Case/Entidade. # [DONE]
  - Validação de valores: Garantir enforcement de valores positivos em depósitos e saques (Value Objects). # [DONE]

>> Entry Point = src/main.py
>> Auto-Generated Documentation = /docs (Swagger)
---
**Notas de Design e Estudo, pela IA**

**Escolhas Atuais:**
1. **Clean Architecture (Layered)**: Separação estrita entre Domínio, Aplicação e Infraestrutura.
2. **Unit of Work (UoW)**: Orquestração de transações atômicas garantindo integridade entre múltiplos repositórios.
3. **Dependency Injection (DI)**: Uso intensivo de provedores FastAPI para desacoplar Use Cases de implementações físicas.
4. **Ports and Adapters**: Interfaces no Core (`Ports`) implementadas na Infra (`Adapters`), protegendo a lógica de negócio.
5. **JWT Externo**: Identidade de usuário gerenciada via token, sem entidade `User` persistente no domínio local.