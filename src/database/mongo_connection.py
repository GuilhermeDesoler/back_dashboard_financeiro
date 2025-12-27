from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from typing import Optional
from src.config import Environment


class MongoConnection:
    _instance: Optional["MongoConnection"] = None
    _client: Optional[MongoClient] = None
    _database: Optional[Database] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MongoConnection, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._client is None:
            self._connect()

    def _connect(self) -> None:
        env = Environment()

        try:
            self._client = MongoClient(env.mongo_uri)
            self._database = self._client[env.mongo_database]

            self._client.admin.command("ping")

            print(f"Conexão estabelecida")

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
        if self._database is None:
            self._connect()
        assert self._database is not None
        return self._database

    def get_collection(self, collection_name: str) -> Collection:
        return self.database[collection_name]

    def close(self) -> None:
        if self._client:
            self._client.close()
            print(f"Conexão fechada")
            self._client = None
            self._database = None


def get_db() -> Database:
    return MongoConnection().database


def get_collection(collection_name: str) -> Collection:
    return MongoConnection().get_collection(collection_name)


def close_connection() -> None:
    MongoConnection().close()
