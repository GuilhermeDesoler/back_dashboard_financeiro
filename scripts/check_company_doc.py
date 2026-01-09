"""
Script para verificar o documento da empresa
"""
import sys
from pathlib import Path
import json

# Adiciona o diretório raiz ao path
sys.path.append(str(Path(__file__).parent.parent))

from src.database.mongo_connection import MongoConnection
from bson import ObjectId


def json_serial(obj):
    """JSON serializer para objetos especiais"""
    if isinstance(obj, ObjectId):
        return str(obj)
    raise TypeError(f"Type {type(obj)} not serializable")


def main():
    conn = MongoConnection()
    shared_db = conn.shared_db

    # Busca a empresa São Luiz Calçados
    company = shared_db['companies'].find_one({'name': 'São Luiz Calçados'})

    if not company:
        print("❌ Empresa São Luiz Calçados não encontrada!")
        return

    print("📄 Documento completo da empresa:")
    print(json.dumps(company, indent=2, default=json_serial, ensure_ascii=False))


if __name__ == '__main__':
    main()
