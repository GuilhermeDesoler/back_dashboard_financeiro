import os
from typing import Dict
from pymongo import MongoClient
from pymongo.database import Database


class TenantDatabaseManager:
    """
    Gerencia conexões com múltiplos bancos de dados (multi-tenancy)

    Arquitetura:
    - shared_db: Contém companies, users, features (dados compartilhados)
    - company_{company_id}_db: Um DB por empresa com dados sensíveis
    """

    _instance = None
    _shared_db: Database = None
    _tenant_dbs: Dict[str, Database] = {}
    _client: MongoClient = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TenantDatabaseManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Inicializa a conexão com MongoDB"""
        mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
        self._client = MongoClient(mongo_uri)
        self._tenant_dbs = {}

    def get_shared_db(self) -> Database:
        """
        Retorna o banco de dados compartilhado (global)

        Collections:
        - companies: Todas as empresas
        - users: Todos os usuários
        - features: Features do sistema
        """
        if self._shared_db is None:
            db_name = os.getenv("SHARED_DB_NAME", "shared_db")
            self._shared_db = self._client[db_name]
        return self._shared_db

    def get_tenant_db(self, company_id: str) -> Database:
        """
        Retorna o banco de dados específico de uma empresa

        Args:
            company_id: ID da empresa

        Returns:
            Database específico da empresa

        Collections da empresa:
        - financial_entries: Lançamentos financeiros
        - payment_modalities: Modalidades de pagamento
        - platform_settings: Configurações da plataforma
        - roles: Roles específicas da empresa
        """
        if not company_id:
            raise ValueError("company_id é obrigatório")

        if company_id not in self._tenant_dbs:
            # MongoDB tem limite de 38 bytes para nome de database
            # Usamos hash curto do company_id para garantir unicidade
            import hashlib
            short_hash = hashlib.md5(company_id.encode()).hexdigest()[:8]
            db_name = f"cmp_{short_hash}_db"
            self._tenant_dbs[company_id] = self._client[db_name]

        return self._tenant_dbs[company_id]

    def create_tenant_db(self, company_id: str) -> Database:
        """
        Cria um novo banco de dados para uma empresa
        Inicializa com collections e índices necessários

        Args:
            company_id: ID da empresa

        Returns:
            Database criado
        """
        tenant_db = self.get_tenant_db(company_id)

        # Cria collections básicas (MongoDB cria automaticamente no primeiro insert)
        # Mas vamos criar índices importantes

        # Índices para financial_entries
        tenant_db["financial_entries"].create_index("date")
        tenant_db["financial_entries"].create_index("modality_id")
        tenant_db["financial_entries"].create_index([("date", -1)])

        # Índices para payment_modalities
        # Índice único case-insensitive para evitar duplicatas como "PIX" vs "Pix"
        tenant_db["payment_modalities"].create_index(
            "name",
            unique=True,
            collation={"locale": "pt", "strength": 2}  # Case-insensitive
        )
        tenant_db["payment_modalities"].create_index("is_active")

        # Índices para roles
        tenant_db["roles"].create_index("name", unique=True)

        return tenant_db

    def delete_tenant_db(self, company_id: str) -> bool:
        """
        Remove o banco de dados de uma empresa
        **CUIDADO: Esta operação é irreversível!**

        Args:
            company_id: ID da empresa

        Returns:
            True se deletado com sucesso
        """
        import hashlib
        short_hash = hashlib.md5(company_id.encode()).hexdigest()[:8]
        db_name = f"cmp_{short_hash}_db"

        # Remove do cache
        if company_id in self._tenant_dbs:
            del self._tenant_dbs[company_id]

        # Deleta o database
        self._client.drop_database(db_name)
        return True

    def get_collection(self, collection_name: str, company_id: str = None):
        """
        Retorna uma collection específica

        Args:
            collection_name: Nome da collection
            company_id: ID da empresa (None para shared_db)

        Returns:
            Collection do MongoDB
        """
        if company_id:
            db = self.get_tenant_db(company_id)
        else:
            db = self.get_shared_db()

        return db[collection_name]

    def close(self):
        """Fecha todas as conexões"""
        if self._client:
            self._client.close()
            self._client = None
            self._shared_db = None
            self._tenant_dbs = {}


# Singleton global
_tenant_db_manager = None


def get_tenant_db_manager() -> TenantDatabaseManager:
    """Retorna a instância singleton do TenantDatabaseManager"""
    global _tenant_db_manager
    if _tenant_db_manager is None:
        _tenant_db_manager = TenantDatabaseManager()
    return _tenant_db_manager
