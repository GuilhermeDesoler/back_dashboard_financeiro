from flask import Blueprint, jsonify, g
from src.database import get_tenant_db
from src.infra.repositories import MongoPlatformSettingsRepository
from src.application.use_cases import (
    GetPlatformSettings,
    TogglePlatformAnticipation,
)
from src.application.middleware.auth_bypass import require_auth, require_feature, require_role, require_super_admin

platform_settings_bp = Blueprint("platform_settings", __name__)


def get_repository(company_id: str):
    """Retorna repositório do banco de dados da empresa"""
    tenant_db = get_tenant_db(company_id)
    collection = tenant_db["platform_settings"]
    return MongoPlatformSettingsRepository(collection)


@platform_settings_bp.route("/platform-settings", methods=["GET"])
@require_auth
@require_feature("platform_settings.read")
def get_settings():
    try:
        # Usa o DB da empresa do usuário autenticado
        repository = get_repository(g.company_id)
        use_case = GetPlatformSettings(repository)
        settings = use_case.execute()

        return jsonify(settings.to_dict()), 200

    except Exception:
        return jsonify({"error": "Erro interno do servidor"}), 500


@platform_settings_bp.route("/platform-settings/toggle-anticipation", methods=["PATCH"])
@require_auth
@require_feature("platform_settings.toggle_anticipation")
def toggle_anticipation():
    try:
        # Usa o DB da empresa do usuário autenticado
        repository = get_repository(g.company_id)
        use_case = TogglePlatformAnticipation(repository)
        settings = use_case.execute()

        return jsonify(settings.to_dict()), 200

    except Exception:
        return jsonify({"error": "Erro interno do servidor"}), 500
