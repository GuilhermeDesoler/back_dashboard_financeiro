from flask import Blueprint, request, jsonify, g
from src.database import get_tenant_db
from src.infra.repositories import MongoPaymentModalityRepository
from src.application.use_cases import (
    CreatePaymentModality,
    ListPaymentModalities,
    UpdatePaymentModality,
    DeletePaymentModality,
    TogglePaymentModality,
)
from src.application.middleware import require_auth, require_feature

payment_modality_bp = Blueprint("payment_modalities", __name__)


def get_repository(company_id: str):
    """Retorna repositório do banco de dados da empresa"""
    tenant_db = get_tenant_db(company_id)
    collection = tenant_db["payment_modalities"]
    return MongoPaymentModalityRepository(collection)


@payment_modality_bp.route("/payment-modalities", methods=["POST"])
@require_auth
@require_feature("payment_modalities.create")
def create_modality():
    try:
        data = request.get_json()
        name = data.get("name")
        color = data.get("color")

        # Usa o DB da empresa do usuário autenticado
        repository = get_repository(g.company_id)
        use_case = CreatePaymentModality(repository)
        modality = use_case.execute(name, color)

        return jsonify(modality.to_dict()), 201

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception:
        return jsonify({"error": "Erro interno do servidor"}), 500


@payment_modality_bp.route("/payment-modalities", methods=["GET"])
@require_auth
@require_feature("payment_modalities.read")
def list_modalities():
    try:
        only_active = request.args.get("only_active", "true").lower() == "true"

        # Usa o DB da empresa do usuário autenticado
        repository = get_repository(g.company_id)
        use_case = ListPaymentModalities(repository)
        modalities = use_case.execute(only_active=only_active)

        return jsonify([m.to_dict() for m in modalities]), 200

    except Exception:
        return jsonify({"error": "Erro interno do servidor"}), 500


@payment_modality_bp.route("/payment-modalities/<modality_id>", methods=["PUT"])
@require_auth
@require_feature("payment_modalities.update")
def update_modality(modality_id):
    try:
        data = request.get_json()
        name = data.get("name")
        color = data.get("color")

        # Usa o DB da empresa do usuário autenticado
        repository = get_repository(g.company_id)
        use_case = UpdatePaymentModality(repository)
        modality = use_case.execute(modality_id, name, color)

        return jsonify(modality.to_dict()), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 404 if "não encontrada" in str(e) else 400
    except Exception:
        return jsonify({"error": "Erro interno do servidor"}), 500


@payment_modality_bp.route("/payment-modalities/<modality_id>", methods=["DELETE"])
@require_auth
@require_feature("payment_modalities.delete")
def delete_modality(modality_id):
    try:
        # Usa o DB da empresa do usuário autenticado
        repository = get_repository(g.company_id)
        use_case = DeletePaymentModality(repository)
        success = use_case.execute(modality_id)

        if success:
            return jsonify({"message": "Modalidade deletada com sucesso"}), 200
        return jsonify({"error": "Erro ao deletar modalidade"}), 500

    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception:
        return jsonify({"error": "Erro interno do servidor"}), 500


@payment_modality_bp.route("/payment-modalities/<modality_id>/toggle", methods=["PATCH"])
@require_auth
@require_feature("payment_modalities.toggle")
def toggle_modality(modality_id):
    try:
        data = request.get_json()
        activate = data.get("activate", True)

        # Usa o DB da empresa do usuário autenticado
        repository = get_repository(g.company_id)
        use_case = TogglePaymentModality(repository)
        modality = use_case.execute(modality_id, activate)

        return jsonify(modality.to_dict()), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception:
        return jsonify({"error": "Erro interno do servidor"}), 500
