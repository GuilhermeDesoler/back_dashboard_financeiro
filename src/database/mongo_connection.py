from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from typing import Optional, Dict
from src.config import Environment


class MongoConnection:
    """
    Gerenciador de conexões MongoDB com suporte a multi-tenancy

    Mantém compatibilidade com código legado, mas adiciona suporte
    para múltiplos databases (um por empresa)
    """
    _instance: Optional["MongoConnection"] = None
    _client: Optional[MongoClient] = None
    _shared_db: Optional[Database] = None
    _tenant_dbs: Dict[str, Database] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MongoConnection, cls).__new__(cls)
            cls._instance._tenant_dbs = {}
        return cls._instance

    def __init__(self):
        if self._client is None:
            self._connect()

    def _connect(self) -> None:
        env = Environment()

        try:
            self._client = MongoClient(env.mongo_uri)
            # shared_db contém: companies, users, features
            self._shared_db = self._client["shared_db"]

            self._client.admin.command("ping")

            print(f"Conexão estabelecida com MongoDB (Multi-Tenant)")

        except Exception as e:
            error_msg = f"Erro ao conectar ao MongoDB: {str(e)}"
            print(error_msg)
            raise ConnectionError(error_msg) from e

    @property
    def client(self) -> MongoClient:
        if self._client is None:
            self._connect()
        assert self._client is not None
        return self._client

    @property
    def database(self) -> Database:
        """Retorna shared_db (compatibilidade com código legado)"""
        if self._shared_db is None:
            self._connect()
        assert self._shared_db is not None
        return self._shared_db

    @property
    def shared_db(self) -> Database:
        """Retorna o banco de dados compartilhado (companies, users, features)"""
        if self._shared_db is None:
            self._connect()
        assert self._shared_db is not None
        return self._shared_db

    def get_tenant_db(self, company_id: str, company_name: str = None) -> Database:
        """
        Retorna o banco de dados específico de uma empresa

        Args:
            company_id: ID da empresa
            company_name: Nome da empresa (opcional, usado para criar db_name mais legível)

        Returns:
            Database específico da empresa
        """
        if not company_id:
            raise ValueError("company_id é obrigatório")

        if company_id not in self._tenant_dbs:
            if company_name:
                # Sanitiza o nome da empresa para usar como nome do database
                # Remove caracteres especiais e espaços, converte para minúsculas
                import re
                safe_name = re.sub(r'[^a-zA-Z0-9_]', '_', company_name.lower())
                safe_name = re.sub(r'_+', '_', safe_name)  # Remove underscores duplicados
                safe_name = safe_name.strip('_')  # Remove underscores das pontas
                db_name = f"company_{safe_name}"
            else:
                # Fallback: usa hash curto do company_id
                import hashlib
                short_id = hashlib.md5(company_id.encode()).hexdigest()[:8]
                db_name = f"cmp_{short_id}_db"

            self._tenant_dbs[company_id] = self._client[db_name]

        return self._tenant_dbs[company_id]

    def create_tenant_db(self, company_id: str, company_name: str = None) -> Database:
        """
        Cria e inicializa banco de dados para uma empresa

        Args:
            company_id: ID da empresa
            company_name: Nome da empresa (opcional)

        Returns:
            Database criado
        """
        tenant_db = self.get_tenant_db(company_id, company_name)

        # Cria índices para financial_entries
        tenant_db["financial_entries"].create_index("date")
        tenant_db["financial_entries"].create_index("modality_id")
        tenant_db["financial_entries"].create_index([("date", -1)])

        # Cria índices para payment_modalities
        tenant_db["payment_modalities"].create_index("name", unique=True)
        tenant_db["payment_modalities"].create_index("is_active")

        # Cria índices para roles
        tenant_db["roles"].create_index("name", unique=True)

        print(f"Banco de dados criado para empresa: {company_id}")

        return tenant_db

    def get_collection(self, collection_name: str, company_id: Optional[str] = None) -> Collection:
        """
        Retorna uma collection

        Args:
            collection_name: Nome da collection
            company_id: ID da empresa (None = shared_db)

        Returns:
            Collection
        """
        if company_id:
            return self.get_tenant_db(company_id)[collection_name]
        return self.shared_db[collection_name]

    def close(self) -> None:
        if self._client:
            self._client.close()
            print(f"Conexão fechada")
            self._client = None
            self._shared_db = None
            self._tenant_dbs = {}


def get_db() -> Database:
    """Retorna shared_db (compatibilidade)"""
    return MongoConnection().shared_db


def get_shared_db() -> Database:
    """Retorna banco de dados compartilhado"""
    return MongoConnection().shared_db


def get_tenant_db(company_id: str) -> Database:
    """Retorna banco de dados da empresa"""
    return MongoConnection().get_tenant_db(company_id)


def get_collection(collection_name: str, company_id: Optional[str] = None) -> Collection:
    """Retorna collection (shared ou tenant)"""
    return MongoConnection().get_collection(collection_name, company_id)


def create_tenant_db(company_id: str, company_name: str = None) -> Database:
    """Cria banco de dados para empresa"""
    return MongoConnection().create_tenant_db(company_id, company_name)


def close_connection() -> None:
    MongoConnection().close()
