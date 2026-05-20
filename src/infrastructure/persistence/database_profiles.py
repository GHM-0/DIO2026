from dataclasses import dataclass

@dataclass
class DbProfile:
    profile_name: str
    conn_driver: str
    user_name: str
    user_pass: str
    db_name: str | None = None

    @property
    def is_database_present(self) -> bool:
        """Indica se há uma base de dados associada ao perfil."""
        return self.db_name is not None

    @property
    def missing_fields(self) -> list[str]:
        """Lista campos sem valor. O profile_name é validado antes da inspeção."""
        if not self.profile_name:
            raise ValueError("Registro DbProfile sem nome não é permitido.")

        fields = ["conn_driver", "user_name", "user_pass", "db_name"]
        return [field for field in fields if not getattr(self, field)]