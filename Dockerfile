# Dockerfile
# SETUP do Container do Projeto
FROM python:3.14-slim AS builder
LABEL stage=builder
LABEL authors="hellboy"

# Gerenciador de Pacotes
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Deploy
WORKDIR /desafio

# Configurações do Runtime
# Evita cache .pyc
ENV PYTHONDONTWRITEBYTECODE=1
# Evita Desincronia entre eventos e log
ENV PYTHONUNBUFFERED=1

# Uv
# Acelera o load da aplicação
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

# Dependências do projeto
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev


# Deploy
FROM python:3.14-slim AS final

WORKDIR /desafio

# Configura o ambiente para usar o venv
ENV PATH="/desafio/.venv/bin:$PATH"
ENV PYTHONPATH=/desafio/src

# Setup env
# Evita cache .pyc
ENV PYTHONDONTWRITEBYTECODE=1
# Evita Desincronia entre eventos e log
ENV PYTHONUNBUFFERED=1

# Copia o UV para o Layer
COPY --from=builder /desafio/.venv /desafio/.venv

# Cria o Usuário de Serviço
RUN groupadd -g 900 rungroup && \
    useradd -r -u 900 -g rungroup --shell /sbin/nologin --no-create-home run

# Deploy do projeto
COPY . .

# --- Hardened security ---
RUN chown -R root:root /desafio && \
    find /desafio -type d -exec chmod 555 {} + && \
    find /desafio -type f -exec chmod 444 {} + && \
    chmod -R 555 /desafio/.venv/bin

# Muda para usuário não-root por segurança
USER run

EXPOSE 8000

ENTRYPOINT ["python", "-m", "fastapi", "run", "src/main.py"]
CMD ["--host", "0.0.0.0", "--port", "8000"]
