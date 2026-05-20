# utils.scripts.db.setup-db.py

import pathlib
import sys

# ./desafio

root_path = (pathlib.Path(__file__).parent  # utils/scripts/db
             .parent                        # utils/scripts
             .parent                        # utils
             .parent                        # desafio (root)
             .resolve())


# set path on python
sys.path.append(str(root_path / "src"))

# Leitura do settings "obj"
try:
    from infrastructure.config import settings
except ImportError:
    # Aborta a Execução caso não haja Settings
    print("Garanta  que as variáveis de ambiente e o Settings estejam configurados")
    sys.exit(1)


def setup() -> None:
    """
    Realiza a Criação do Script SQL inicial contendo o template ajustado para o app
    """

    # ./utils/scripts/db
    current_dir = pathlib.Path(__file__).parent.resolve()

    # Template Base contendo os marcadores para substituição via .env
    template_path = current_dir / "000_TEMPLATE_DB.sql"

    # Localização para o Script ajustado
    sql_path = root_path / "mysql" / "docker-entrypoint-initdb.d" / "001_CREATE_DB.sql"

    # Remover arquivos antigos
    # /mysql/docker-entrypoint-initdb.d/001_CREATE_DB.sql
    if sql_path.exists():
        sql_path.unlink(missing_ok=True)

    # Cria a pasta de saída caso não exista
    sql_path.parent.mkdir(parents=True, exist_ok=True) # mkdir -p $sql_path

    # verifica a existência do template
    if not template_path.exists():
        print(f"{template_path} parece não existir!")
        return

    # Substitui os place holds pelas variáveis de .env
    sql_content = template_path.read_text(encoding="utf-8")

    # Passar na Conexão use_unicode=True

    placeholders = settings.model_dump()
    for key, value in placeholders.items():
        tag = f"${{{key}}}"
        if tag in sql_content:
            sql_content = sql_content.replace(tag,str(value))

    sql_path.write_text(sql_content,encoding="utf-8")

if __name__ == "__main__":
    setup()
