import os
from pathlib import Path
from typing import List, Optional

MONGO_URI = "MONGO_URI"
MONGO_DATABASE = "MONGO_DATABASE"


class EnvironmentError(Exception):
    pass


class Environment:
    __instance = None

    def __new__(cls):
        if Environment.__instance is None:
            Environment.__instance = super().__new__(cls)
        return Environment.__instance

    REQUIRED_VARIABLES: List[str] = [
        MONGO_URI,
        MONGO_DATABASE,
    ]

    def __init__(self):
        if not hasattr(self, "_initialized"):
            self._load_env_file()
            self._validate_environment()
            self._load_variables()
            self._initialized = True

    def _load_env_file(self) -> None:
        env_path = Path(__file__).parent.parent.parent / ".env"

        if not env_path.exists():
            raise EnvironmentError(
                f"Arquivo .env não encontrado em: {env_path}\n"
                f"Por favor, crie o arquivo .env baseado no .env.example"
            )

        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        if "=" in line:
                            key, value = line.split("=", 1)
                            key = key.strip()
                            value = value.strip().strip('"').strip("'")
                            if key and value:
                                os.environ[key] = value
        except Exception as e:
            raise EnvironmentError(f"Erro ao ler arquivo .env: {str(e)}") from e

    def _validate_environment(self) -> None:
        missing_vars: List[str] = []
        empty_vars: List[str] = []

        for var in self.REQUIRED_VARIABLES:
            value = os.getenv(var)
            if value is None:
                missing_vars.append(var)
            elif not value.strip():
                empty_vars.append(var)

        errors = []
        if missing_vars:
            errors.append(f"Variáveis não encontradas: {', '.join(missing_vars)}")
        if empty_vars:
            errors.append(f"Variáveis vazias: {', '.join(empty_vars)}")

        if errors:
            error_msg = "Erro na validação das variáveis de ambiente:\n"
            error_msg += "\n".join(f"  - {error}" for error in errors)
            error_msg += (
                f"\n\nVariáveis obrigatórias: {', '.join(self.REQUIRED_VARIABLES)}"
            )
            error_msg += "\n\nVerifique seu arquivo .env e garanta que todas as variáveis estão definidas."
            raise EnvironmentError(error_msg)

    def _load_variables(self) -> None:
        for var in self.REQUIRED_VARIABLES:
            setattr(self, var, os.getenv(var))

    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:

        return os.getenv(key, default)

    def require(self, key: str) -> str:
        value = os.getenv(key)
        if value is None:
            raise EnvironmentError(
                f"Variável de ambiente obrigatória não encontrada: {key}"
            )
        return value

    @property
    def mongo_uri(self) -> str:
        return self.require(MONGO_URI)

    @property
    def mongo_database(self) -> str:
        return self.require(MONGO_DATABASE)
