from flask import Blueprint, jsonify, request
from pymongo import MongoClient
from src.database import MongoConnection

migration_bp = Blueprint("migration", __name__)


@migration_bp.route("/migration/clone-to-dev", methods=["POST"])
def clone_to_dev():
    """
    Clona todos os databases do cluster PROD para o cluster DEV

    Body (opcional):
    {
        "dev_uri": "mongodb+srv://...",  # URI do cluster DEV (opcional, usa default)
        "databases": ["shared_db", "cmp_xxx"]  # Lista específica (opcional, copia todos)
    }
    """
    try:
        data = request.get_json() or {}

        # URI do cluster DEV (pode ser passado no body ou usar default)
        dev_uri = data.get("dev_uri", "mongodb+srv://desoler:30271859@cluster0.uenzth9.mongodb.net/")
        specific_dbs = data.get("databases", None)

        # Conexão com PROD (atual)
        prod_conn = MongoConnection()
        prod_client = prod_conn.client

        # Conexão com DEV
        dev_client = MongoClient(dev_uri)

        # Testar conexão DEV
        dev_client.admin.command("ping")

        # Listar todos os databases do PROD
        all_databases = prod_client.list_database_names()

        # Filtrar databases do sistema
        system_dbs = ["admin", "local", "config"]
        databases_to_copy = [db for db in all_databases if db not in system_dbs]

        # Se especificou databases específicos, usar apenas esses
        if specific_dbs:
            databases_to_copy = [db for db in databases_to_copy if db in specific_dbs]

        results = {
            "success": True,
            "databases_copied": [],
            "collections_copied": {},
            "documents_copied": {},
            "errors": []
        }

        for db_name in databases_to_copy:
            try:
                prod_db = prod_client[db_name]
                dev_db = dev_client[db_name]

                collections = prod_db.list_collection_names()
                results["collections_copied"][db_name] = []
                results["documents_copied"][db_name] = {}

                for collection_name in collections:
                    try:
                        # Pegar todos os documentos da collection
                        prod_collection = prod_db[collection_name]
                        dev_collection = dev_db[collection_name]

                        documents = list(prod_collection.find({}))

                        if documents:
                            # Limpar collection existente no DEV
                            dev_collection.delete_many({})
                            # Inserir documentos
                            dev_collection.insert_many(documents)

                        results["collections_copied"][db_name].append(collection_name)
                        results["documents_copied"][db_name][collection_name] = len(documents)

                    except Exception as coll_error:
                        results["errors"].append(f"{db_name}.{collection_name}: {str(coll_error)}")

                results["databases_copied"].append(db_name)

            except Exception as db_error:
                results["errors"].append(f"{db_name}: {str(db_error)}")

        # Fechar conexão DEV
        dev_client.close()

        return jsonify(results), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@migration_bp.route("/migration/list-databases", methods=["GET"])
def list_databases():
    """Lista todos os databases disponíveis no cluster PROD"""
    try:
        prod_conn = MongoConnection()
        prod_client = prod_conn.client

        all_databases = prod_client.list_database_names()
        system_dbs = ["admin", "local", "config"]

        databases_info = []
        for db_name in all_databases:
            if db_name not in system_dbs:
                db = prod_client[db_name]
                collections = db.list_collection_names()

                collection_details = {}
                for coll_name in collections:
                    count = db[coll_name].count_documents({})
                    collection_details[coll_name] = count

                databases_info.append({
                    "name": db_name,
                    "collections": collections,
                    "document_counts": collection_details
                })

        return jsonify({
            "success": True,
            "databases": databases_info
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
