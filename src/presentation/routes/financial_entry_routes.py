from flask import Blueprint, request, jsonify
from datetime import datetime
from src.database import get_collection
from src.infra.repositories import (
    MongoFinancialEntryRepository,
    MongoPaymentModalityRepository,
)
from src.application.use_cases import (
    CreateFinancialEntry,
    ListFinancialEntries,
    UpdateFinancialEntry,
    DeleteFinancialEntry,
)

financial_entry_bp = Blueprint("financial_entries", __name__)


def get_repositories():
    entry_collection = get_collection("financial_entries")
    modality_collection = get_collection("payment_modalities")
    
    entry_repo = MongoFinancialEntryRepository(entry_collection)
    modality_repo = MongoPaymentModalityRepository(modality_collection)
    
    return entry_repo, modality_repo


@financial_entry_bp.route("/financial-entries", methods=["POST"])
def create_entry():
    try:
        data = request.get_json()
        value = float(data.get("value"))
        date_str = data.get("date")
        modality_id = data.get("modality_id")
        
        date = datetime.fromisoformat(date_str)
        
        entry_repo, modality_repo = get_repositories()
        use_case = CreateFinancialEntry(entry_repo, modality_repo)
        entry = use_case.execute(value, date, modality_id)
        
        return jsonify(entry.to_dict()), 201
    
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception:
        return jsonify({"error": "Erro interno do servidor"}), 500


@financial_entry_bp.route("/financial-entries", methods=["GET"])
def list_entries():
    try:
        modality_id = request.args.get("modality_id")
        start_date_str = request.args.get("start_date")
        end_date_str = request.args.get("end_date")

        start_date = datetime.fromisoformat(start_date_str) if start_date_str else None
        end_date = datetime.fromisoformat(end_date_str) if end_date_str else None

        entry_repo, _ = get_repositories()
        use_case = ListFinancialEntries(entry_repo)
        entries = use_case.execute(modality_id, start_date, end_date)

        return jsonify([e.to_dict() for e in entries]), 200

    except Exception:
        return jsonify({"error": "Erro interno do servidor"}), 500


@financial_entry_bp.route("/financial-entries/<entry_id>", methods=["PUT"])
def update_entry(entry_id):
    try:
        data = request.get_json()
        value = float(data.get("value"))
        date_str = data.get("date")
        modality_id = data.get("modality_id")
        
        date = datetime.fromisoformat(date_str)
        
        entry_repo, modality_repo = get_repositories()
        use_case = UpdateFinancialEntry(entry_repo, modality_repo)
        entry = use_case.execute(entry_id, value, date, modality_id)
        
        return jsonify(entry.to_dict()), 200
    
    except ValueError as e:
        return jsonify({"error": str(e)}), 404 if "não encontrado" in str(e) else 400
    except Exception:
        return jsonify({"error": "Erro interno do servidor"}), 500


@financial_entry_bp.route("/financial-entries/<entry_id>", methods=["DELETE"])
def delete_entry(entry_id):
    try:
        entry_repo, _ = get_repositories()
        use_case = DeleteFinancialEntry(entry_repo)
        success = use_case.execute(entry_id)

        if success:
            return jsonify({"message": "Lançamento deletado com sucesso"}), 200
        return jsonify({"error": "Erro ao deletar lançamento"}), 500

    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception:
        return jsonify({"error": "Erro interno do servidor"}), 500
