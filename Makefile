#==============================================================================
# DESAFIO - SISTEMA DE CONTAS (CLEAN ARCHITECTURE)
#==============================================================================
# Orquestração de Ambiente, Infraestrutura e Testes
# Autor: HB | Versão: 0.1.0
#==============================================================================

-include .env

# --- CONFIGURAÇÕES DE AMBIENTE ---
PODMAN      := podman
COMPOSE     := podman-compose
PYTHON      := python3
PYTEST      := uv run python -m pytest

# --- ALIASES OPERACIONAIS (DRY) ---
PURGE_DB    := $(PODMAN) unshare rm -rf $(APP_DB)
PRUME_IMG   := $(PODMAN) image prune --filter "label=stage=builder" -f
STOP_ALL    := $(COMPOSE) stop $(DB_CONTAINER) $(APP_CONTAINER)
BUILD_IMG   := $(PODMAN) build -t $(APP_IMAGE):$(APP_VERSION)
MYSQL_DUMP  := $(PODMAN) exec $(DB_CONTAINER) mysqldump -u root -p'$(MYSQL_ROOT_PASSWORD)' '$(MYSQL_DATABASE)'

MIGRATE_RUN :=  alembic upgrade head
MIGRATE_GEN :=  alembic revision --autogenerate -m "auto migration"

CLEAN_MIGRATE := rm -rf ./migrations/versions/*

WAIT_FOR_DB = @printf "Subindo $(DB_CONTAINER) ..."; \
	until [ "$$($(PODMAN) inspect --format='{{.State.Health.Status}}' $(DB_CONTAINER) 2>/dev/null)" = "healthy" ]; do \
		printf "."; \
		sleep 1; \
	done; \
	printf "\n $(DB_CONTAINER) ON LINE | Estabelecendo Conexão ... "; \
	until mysql -h $(MYSQL_HOST) -P $(MYSQL_PORT) --protocol=tcp -u root -p'$(MYSQL_ROOT_PASSWORD)' -e "SELECT 1" >/dev/null 2>&1; do \
		printf ">"; \
		sleep 1; \
	done; \
	echo "[PRONTO]"

.PHONY: dev build clean stop setup backup deploy dev-db tests help
.DEFAULT_GOAL := dev

## help: Exibe esta lista de comandos úteis.
help:
	@echo "Comandos disponíveis:"
	@sed -n 's/^##//p' $(MAKEFILE_LIST) | column -t -s ':' | sed -e 's/^/ /'

## setup: (SANDBOX) Reseta o ambiente local, limpa o DB e ajusta permissões.
setup: clean
	@$(PURGE_DB)
	@mkdir -p $(APP_DB)/mysql
	@$(PODMAN) unshare chown -R 999:999 $(APP_DB)
	@$(PODMAN) unshare chmod -R 755 $(APP_DB)/mysql
	@python3 utils/scripts/db/setup-db.py

## dev: Reinicia infraestrutura, reconstrói imagem e sobe containers.
dev: stop setup
	@$(BUILD_IMG) .
	@$(COMPOSE) up -d --force-recreate
	$(WAIT_FOR_DB)
	@$(MIGRATE_GEN)
	@$(MIGRATE_RUN)
	@$(PRUME_IMG)

# dev-db: Inicia apenas o container do banco de dados (Perfil dev-db)
dev-db:
	@$(MAKE) stop setup
	@$(COMPOSE) --profile dev-db up -d --force-recreate
	$(WAIT_FOR_DB)
	@$(MIGRATE_GEN)
	@$(MIGRATE_RUN)

## stop: Interrompe a execução dos containers sem remover volumes.
stop:
	@$(STOP_ALL) 2>/dev/null || true

# [INTERNAL] clean: Remove containers, volumes, imagens locais e destrói o DB
clean: stop
	@$(PRUME_IMG)  2>/dev/null || true
	@$(COMPOSE) down -v 2>/dev/null || true
	@$(PURGE_DB) 2>/dev/null || true
	@$(PODMAN) rmi $(APP_IMAGE):$(APP_VERSION) 2>/dev/null || true
	@$(CLEAN_MIGRATE)  2>/dev/null || true

## build: Purga total e reconstrução da imagem final
build: clean
	@$(BUILD_IMG) --no-cache .
	@$(PRUME_IMG)

## deploy: Build da imagem de deploy
deploy: build setup
	@$(COMPOSE) -f docker-compose.yml up -d
	$(WAIT_FOR_DB)
	@echo "Executando migrações no container $(APP_CONTAINER)..."
	@$(MIGRATE_RUN)

## backup: Backup do DB para pasta ./backup_data.
backup:
	@mkdir -p ./backup_data
	@$(MYSQL_CON) \
		--single-transaction --routines --triggers --events --hex-blob --complete-insert \
		--skip-add-locks --quick --set-gtid-purged=OFF \
		> ./backup_data/backup_$(MYSQL_DATABASE)_$(shell date +%Y%m%d_%H%M).sql

## tests: Executa a suíte de testes garantindo que o PYTHONPATH inclua 'src' para o ambiente local.
tests:
	@echo "--- [Iniciando Suíte de Testes] ---"
	@PYTHONPATH=src $(PYTEST) -vvv -s tests/
