from flask import Blueprint, request, jsonify
from src.database import get_collection
from src.infra.repositories import MongoPaymentModalityRepository
from src.application.use_cases import (
    CreatePaymentModality,
    ListPaymentModalities,
    UpdatePaymentModality,
    DeletePaymentModality,
    TogglePaymentModality,
)

payment_modality_bp = Blueprint("payment_modalities", __name__)


def get_repository():
    collection = get_collection("payment_modalities")
    return MongoPaymentModalityRepository(collection)


@payment_modality_bp.route("/payment-modalities", methods=["POST"])
def create_modality():
    try:
        data = request.get_json()
        name = data.get("name")
        
        repository = get_repository()
        use_case = CreatePaymentModality(repository)
        modality = use_case.execute(name)
        
        return jsonify(modality.to_dict()), 201
    
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Erro interno do servidor"}), 500


@payment_modality_bp.route("/payment-modalities", methods=["GET"])
def list_modalities():
    try:
        only_active = request.args.get("only_active", "true").lower() == "true"
        
        repository = get_repository()
        use_case = ListPaymentModalities(repository)
        modalities = use_case.execute(only_active=only_active)
        
        return jsonify([m.to_dict() for m in modalities]), 200
    
    except Exception as e:
        return jsonify({"error": "Erro interno do servidor"}), 500


@payment_modality_bp.route("/payment-modalities/<modality_id>", methods=["PUT"])
def update_modality(modality_id):
    try:
        data = request.get_json()
        name = data.get("name")
        
        repository = get_repository()
        use_case = UpdatePaymentModality(repository)
        modality = use_case.execute(modality_id, name)
        
        return jsonify(modality.to_dict()), 200
    
    except ValueError as e:
        return jsonify({"error": str(e)}), 404 if "não encontrada" in str(e) else 400
    except Exception as e:
        return jsonify({"error": "Erro interno do servidor"}), 500


@payment_modality_bp.route("/payment-modalities/<modality_id>", methods=["DELETE"])
def delete_modality(modality_id):
    try:
        repository = get_repository()
        use_case = DeletePaymentModality(repository)
        success = use_case.execute(modality_id)
        
        if success:
            return jsonify({"message": "Modalidade deletada com sucesso"}), 200
        return jsonify({"error": "Erro ao deletar modalidade"}), 500
    
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": "Erro interno do servidor"}), 500


@payment_modality_bp.route("/payment-modalities/<modality_id>/toggle", methods=["PATCH"])
def toggle_modality(modality_id):
    try:
        data = request.get_json()
        activate = data.get("activate", True)
        
        repository = get_repository()
        use_case = TogglePaymentModality(repository)
        modality = use_case.execute(modality_id, activate)
        
        return jsonify(modality.to_dict()), 200
    
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": "Erro interno do servidor"}), 500
