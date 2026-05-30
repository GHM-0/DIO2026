# src.infrastructure.config.py

from typing import Any, Optional

from pydantic import Field
from pydantic_settings import BaseSettings,SettingsConfigDict

from exception.infrastructure.exception.database.database_exceptions import DatabaseException
from infrastructure.persistence.database_profiles import DbProfile


# Configuração
class Settings(BaseSettings):
    """
    Gerencia as configurações da aplicação e variáveis de ambiente.

    Esta classe carrega os dados de conexão do banco de dados MySQL
    a partir de um arquivo .env e fornece URLs formatadas para o SQLAlchemy/aiomysql.
    """

    # env
    MYSQL_PORT: Optional[int] = Field(default=None, description="Porta de conexão do Banco")
    MYSQL_HOST: Optional[str] = Field(default=None, description="Endereço IP do Host/DB")
    MYSQL_ROOT: Optional[str] = Field(default=None, description="Nome do root para conexão com DB")
    MYSQL_USER: Optional[str] = Field(default=None, description="Nome do usuário para conexão com DB")
    MYSQL_PASSWORD: Optional[str] = Field(default=None, description="Senha do usuário")
    MYSQL_DATABASE: Optional[str] = Field(default=None, description="Nome do Schema ou Database")
    MYSQL_ROOT_PASSWORD: Optional[str] = Field(default=None, description="Senha de Root")
    CHARSET: Optional[str] = Field(default=None, description="Codificação da base de dados")
    SECRET_KEY: Optional[str] = Field(default=None, description="Chave secreta para geração de tokens")
    ALGORITHM: Optional[str] = Field(default=None, description="Tipo de Criptográfia do Token de Acesso")
    DB_PROFILES: dict[str, dict[str, str|None]] = Field(default_factory=dict, alias="DB_PROFILES")

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

        url:str|None = None

        missing_components:list[str] = profile.missing_fields

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

    # Popula o Dicionário IN Memory
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