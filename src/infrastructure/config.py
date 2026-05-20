# src.infrastructure.config.py
from typing import Any

from pydantic import Field
from pydantic_settings import BaseSettings,SettingsConfigDict

from infrastructure.exception.database.database_exceptions import DatabaseException
from infrastructure.persistence.database_profiles import DbProfile


# Configuração
class Settings(BaseSettings):
    """
    Gerencia as configurações da aplicação e variáveis de ambiente.

    Esta classe carrega os dados de conexão do banco de dados MySQL
    a partir de um arquivo .env e fornece URLs formatadas para o SQLAlchemy/aiomysql.
    """

    # env
    MYSQL_PORT:int = Field(description="Porta de conexão do Banco")
    MYSQL_HOST:str = Field(description="Endereço IP do Host/DB")
    MYSQL_ROOT: str = Field(description="Nome do root para conexão com DB")
    MYSQL_USER:str = Field(description="Nome do usuário para conexão com DB")
    MYSQL_PASSWORD:str = Field(description="Senha do usuário")
    MYSQL_DATABASE:str = Field(description="Nome do Schema ou Database")
    MYSQL_ROOT_PASSWORD:str = Field(description="Senha de Root")
    CHARSET: str = Field(description="Codificação da base de dados")

    SECRET_KEY: str = Field(description="Chave secreta para geração de tokens")
    ALGORITHM: str = Field(description="Tipo de Criptográfia do Token de Acesso")

    DB_PROFILES: dict[str, dict[str, Any]] = Field(default={}, alias="DB_PROFILES")

    def _get_database_url(
        self,
        profile: DbProfile
    ) -> str:
        """
            Gera a URL de conexão utilizando os componentes processados de DbProfile.

            Args:
                profile: Instância de DbProfile contendo o mapeamento de **perfis**.

            Returns:
                str: String de conexão válida para SQLAlchemy.
        """

        url = None

        missing_components = profile.missing_fields

        if not missing_components or (missing_components == ["db_name"] and not profile.is_database_present):
            
            # TODO: Para ambientes de produção, 'user' e 'passwd' devem ser URL-encoded
            #       para lidar com caracteres especiais. Ex: urllib.parse.quote_plus(user)
            #       Para este exercício básico, assumimos que não há caracteres especiais.
            url = f"mysql+{profile.conn_driver}://{profile.user_name}:{profile.user_pass}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/"
            
            if profile.is_database_present:
                url += f"{profile.db_name}?charset={self.CHARSET}"
            return url

        if missing_components and url is None:
            raise DatabaseException(f"Componentes do perfil '{profile.profile_name}' ausentes: {', '.join(missing_components)}")

        raise DatabaseException("Não foi possível gerar URL de conexão por motivo desconhecido")


    def model_post_init(self, __context: Any) -> None:
        """
        Orquestra a injeção dos perfis a partir do dicionário DB_PROFILES carregado do .env.
        Transforma os metadados brutos em instâncias do POPO DbProfile.
        """

        for name, profile_metadata in self.DB_PROFILES.items():

            resolved_data = {}
            for key, value in profile_metadata.items():
                if isinstance(value, str):
                    resolved_data[key] = getattr(self, value, value)
                else:
                    resolved_data[key] = value

            profile_obj = DbProfile(profile_name=name, **resolved_data)

            setattr(self, name, self._get_database_url(profile_obj))

    model_config = SettingsConfigDict(env_file=".env", extra="allow", env_file_encoding="utf-8")

settings = Settings()