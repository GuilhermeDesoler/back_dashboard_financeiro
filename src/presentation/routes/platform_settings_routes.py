from flask import Blueprint, jsonify, g, request
from src.database import get_tenant_db
from src.infra.repositories import MongoPlatformSettingsRepository
from src.application.use_cases import GetPlatformSettings
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
        print("company_id:", getattr(g, "company_id", None))

        repository = get_repository(g.company_id)
        use_case = GetPlatformSettings(repository)
        settings = use_case.execute()

        return jsonify(settings.to_dict()), 200

    except Exception:
        return jsonify({"error": "Erro interno do servidor"}), 500
    

@platform_settings_bp.route("/platform-settings/markup", methods=["PUT"])
@require_auth
@require_role("admin")
def update_markup_settings():
    """Atualiza configurações de markup (apenas admin)"""
    try:
        data = request.get_json()

        markup_default = data.get("markup_default")
        markup_cost = data.get("markup_cost")
        markup_percentage = data.get("markup_percentage")

        repository = get_repository(g.company_id)
        settings = repository.update_markup_settings(
            markup_default=markup_default,
            markup_cost=markup_cost,
            markup_percentage=markup_percentage
        )

        return jsonify(settings.to_dict()), 200

    except Exception as e:
        return jsonify({"error": f"Erro ao atualizar configurações: {str(e)}"}), 500
