"""
Rotas da API para Compras no Crediário
"""
from flask import Blueprint, request, jsonify, g
from datetime import datetime

from src.database import get_tenant_db, get_shared_db
from src.infra.repositories import (
    MongoCreditPurchaseRepository,
    MongoCreditInstallmentRepository,
    MongoFinancialEntryRepository,
    MongoPaymentModalityRepository,
    MongoAuditLogRepository
)
from src.application.use_cases import (
    CreateCreditPurchase,
    GetCreditPurchaseDetails,
    CancelCreditPurchase,
    PayCreditInstallment,
    UnpayCreditInstallment,
    GetCreditDashboard
)
from src.application.middleware import require_auth, require_feature
from src.application.services.audit_service import AuditService

credit_purchase_bp = Blueprint("credit_purchases", __name__)


def get_repositories(company_id: str):
    """Retorna repositórios do banco de dados da empresa"""
    tenant_db = get_tenant_db(company_id)
    shared_db = get_shared_db()

    credit_purchase_repo = MongoCreditPurchaseRepository(tenant_db)
    credit_installment_repo = MongoCreditInstallmentRepository(tenant_db)
    financial_entry_repo = MongoFinancialEntryRepository(tenant_db["financial_entries"])
    modality_repo = MongoPaymentModalityRepository(tenant_db["payment_modalities"])
    audit_repo = MongoAuditLogRepository(shared_db["audit_logs"])

    return (
        credit_purchase_repo,
        credit_installment_repo,
        financial_entry_repo,
        modality_repo,
        audit_repo
    )


# ==================== COMPRAS NO CREDIÁRIO ====================

@credit_purchase_bp.route("/credit-purchases", methods=["POST"])
@require_auth
@require_feature("credit_purchases.create")
def create_credit_purchase():
    """
    Cria uma nova compra no crediário e gera as parcelas automaticamente.

    Body:
        pagante_nome: str (obrigatório)
        descricao_compra: str (obrigatório)
        valor_total: float (obrigatório)
        numero_parcelas: int (obrigatório)
        data_inicio_pagamento: str ISO (obrigatório)
        pagante_documento: str (opcional)
        pagante_telefone: str (opcional)
        valor_entrada: float (opcional, default: 0)
        intervalo_dias: int (opcional, default: 30)
        taxa_juros_mensal: float (opcional, default: 0)

    Returns:
        201: Compra criada com parcelas
        400: Dados inválidos
        500: Erro interno
    """
    try:
        data = request.get_json()

        # Validar campos obrigatórios
        required_fields = [
            "pagante_nome",
            "descricao_compra",
            "valor_total",
            "numero_parcelas",
            "data_inicio_pagamento"
        ]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Campo obrigatório: {field}"}), 400

        # Parsear dados
        pagante_nome = data["pagante_nome"]
        descricao_compra = data["descricao_compra"]
        valor_total = float(data["valor_total"])
        numero_parcelas = int(data["numero_parcelas"])
        data_inicio_pagamento = datetime.fromisoformat(data["data_inicio_pagamento"])

        pagante_documento = data.get("pagante_documento")
        pagante_telefone = data.get("pagante_telefone")
        valor_entrada = float(data.get("valor_entrada", 0.0))
        intervalo_dias = int(data.get("intervalo_dias", 30))
        taxa_juros_mensal = float(data.get("taxa_juros_mensal", 0.0))

        # Obter repositórios
        (purchase_repo, installment_repo, _, _, audit_repo) = get_repositories(g.company_id)
        audit_service = AuditService(audit_repo)

        # Executar use case
        use_case = CreateCreditPurchase(purchase_repo, installment_repo)
        result = use_case.execute(
            pagante_nome=pagante_nome,
            descricao_compra=descricao_compra,
            valor_total=valor_total,
            numero_parcelas=numero_parcelas,
            data_inicio_pagamento=data_inicio_pagamento,
            registrado_por_user_id=g.user_id,
            registrado_por_nome=g.name,
            pagante_documento=pagante_documento,
            pagante_telefone=pagante_telefone,
            valor_entrada=valor_entrada,
            intervalo_dias=intervalo_dias,
            taxa_juros_mensal=taxa_juros_mensal
        )

        # Log de auditoria
        audit_service.log(
            action="CREATE_CREDIT_PURCHASE",
            user_id=g.user_id,
            user_email=g.email,
            company_id=g.company_id,
            target_type="credit_purchase",
            target_id=result["credit_purchase"]["id"],
            details={
                "pagante_nome": pagante_nome,
                "valor_total": valor_total,
                "numero_parcelas": numero_parcelas
            }
        )

        return jsonify(result), 201

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Erro interno do servidor"}), 500


@credit_purchase_bp.route("/credit-purchases", methods=["GET"])
@require_auth
@require_feature("credit_purchases.read")
def list_credit_purchases():
    """
    Lista todas as compras no crediário com filtros opcionais.

    Query params:
        status: str (ativo, cancelado, concluido)
        pagante_nome: str (busca parcial)
        page: int (default: 1)
        per_page: int (default: 20, max: 100)

    Returns:
        200: Lista de compras
        500: Erro interno
    """
    try:
        # Parâmetros de filtro
        status = request.args.get("status")
        pagante_nome = request.args.get("pagante_nome")

        # Paginação
        page = int(request.args.get("page", 1))
        per_page = min(int(request.args.get("per_page", 20)), 100)
        skip = (page - 1) * per_page

        # Obter repositórios
        (purchase_repo, _, _, _, _) = get_repositories(g.company_id)

        # Buscar compras
        purchases = purchase_repo.find_all(
            status=status,
            pagante_nome=pagante_nome,
            skip=skip,
            limit=per_page
        )

        # Contar total
        total = purchase_repo.count(status=status, pagante_nome=pagante_nome)

        return jsonify({
            "items": [p.to_dict() for p in purchases],
            "total": total,
            "page": page,
            "per_page": per_page
        }), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Erro interno do servidor"}), 500


@credit_purchase_bp.route("/credit-purchases/<credit_purchase_id>", methods=["GET"])
@require_auth
@require_feature("credit_purchases.read")
def get_credit_purchase(credit_purchase_id):
    """
    Busca uma compra no crediário pelo ID com todos os detalhes e parcelas.

    Returns:
        200: Compra encontrada com parcelas
        404: Compra não encontrada
        500: Erro interno
    """
    try:
        # Obter repositórios
        (purchase_repo, installment_repo, _, _, _) = get_repositories(g.company_id)

        # Executar use case
        use_case = GetCreditPurchaseDetails(purchase_repo, installment_repo)
        result = use_case.execute(credit_purchase_id)

        if not result:
            return jsonify({"error": "Compra não encontrada"}), 404

        return jsonify(result), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Erro interno do servidor"}), 500


@credit_purchase_bp.route("/credit-purchases/<credit_purchase_id>", methods=["PUT"])
@require_auth
@require_feature("credit_purchases.update")
def update_credit_purchase(credit_purchase_id):
    """
    Atualiza informações de uma compra no crediário.

    Body (todos opcionais):
        pagante_telefone: str
        pagante_documento: str
        descricao_compra: str

    Returns:
        200: Compra atualizada
        404: Compra não encontrada
        400: Dados inválidos
        500: Erro interno
    """
    try:
        data = request.get_json()

        # Obter repositórios
        (purchase_repo, _, _, _, audit_repo) = get_repositories(g.company_id)
        audit_service = AuditService(audit_repo)

        # Buscar compra
        credit_purchase = purchase_repo.find_by_id(credit_purchase_id)
        if not credit_purchase:
            return jsonify({"error": "Compra não encontrada"}), 404

        # Atualizar campos permitidos
        if "pagante_telefone" in data:
            credit_purchase.pagante_telefone = data["pagante_telefone"]
        if "pagante_documento" in data:
            credit_purchase.pagante_documento = data["pagante_documento"]
        if "descricao_compra" in data:
            credit_purchase.descricao_compra = data["descricao_compra"]

        # Salvar
        updated_purchase = purchase_repo.update(credit_purchase)

        # Log de auditoria
        audit_service.log(
            action="UPDATE_CREDIT_PURCHASE",
            user_id=g.user_id,
            user_email=g.email,
            company_id=g.company_id,
            target_type="credit_purchase",
            target_id=credit_purchase_id,
            details=data
        )

        return jsonify(updated_purchase.to_dict()), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Erro interno do servidor"}), 500


@credit_purchase_bp.route("/credit-purchases/<credit_purchase_id>/cancel", methods=["PATCH"])
@require_auth
@require_feature("credit_purchases.cancel")
def cancel_credit_purchase_route(credit_purchase_id):
    """
    Cancela uma compra no crediário e suas parcelas pendentes.

    Returns:
        200: Compra cancelada
        404: Compra não encontrada
        400: Compra já cancelada
        500: Erro interno
    """
    try:
        # Obter repositórios
        (purchase_repo, installment_repo, _, _, audit_repo) = get_repositories(g.company_id)
        audit_service = AuditService(audit_repo)

        # Executar use case
        use_case = CancelCreditPurchase(purchase_repo, installment_repo)
        result = use_case.execute(credit_purchase_id)

        # Log de auditoria
        audit_service.log(
            action="CANCEL_CREDIT_PURCHASE",
            user_id=g.user_id,
            user_email=g.email,
            company_id=g.company_id,
            target_type="credit_purchase",
            target_id=credit_purchase_id,
            details={
                "canceled_installments": result["canceled_installments"]
            }
        )

        return jsonify(result), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Erro interno do servidor"}), 500


@credit_purchase_bp.route("/credit-purchases/<credit_purchase_id>", methods=["DELETE"])
@require_auth
@require_feature("credit_purchases.delete")
def delete_credit_purchase(credit_purchase_id):
    """
    Remove uma compra no crediário e suas parcelas.

    ATENÇÃO: Esta operação é irreversível!

    Returns:
        200: Compra removida
        404: Compra não encontrada
        500: Erro interno
    """
    try:
        # Obter repositórios
        (purchase_repo, installment_repo, _, _, audit_repo) = get_repositories(g.company_id)
        audit_service = AuditService(audit_repo)

        # Buscar compra
        credit_purchase = purchase_repo.find_by_id(credit_purchase_id)
        if not credit_purchase:
            return jsonify({"error": "Compra não encontrada"}), 404

        # Deletar parcelas primeiro
        deleted_installments = installment_repo.delete_by_credit_purchase(credit_purchase_id)

        # Deletar compra
        success = purchase_repo.delete(credit_purchase_id)

        if not success:
            return jsonify({"error": "Erro ao deletar compra"}), 500

        # Log de auditoria
        audit_service.log(
            action="DELETE_CREDIT_PURCHASE",
            user_id=g.user_id,
            user_email=g.email,
            company_id=g.company_id,
            target_type="credit_purchase",
            target_id=credit_purchase_id,
            details={
                "deleted_installments": deleted_installments,
                "pagante_nome": credit_purchase.pagante_nome
            }
        )

        return jsonify({
            "message": "Compra deletada com sucesso",
            "deleted_installments": deleted_installments
        }), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Erro interno do servidor"}), 500


# ==================== PARCELAS ====================

@credit_purchase_bp.route(
    "/credit-purchases/<credit_purchase_id>/installments/<installment_id>/pay",
    methods=["POST"]
)
@require_auth
@require_feature("credit_installments.pay")
def pay_installment(credit_purchase_id, installment_id):
    """
    **ENDPOINT PRINCIPAL: Registra o pagamento de uma parcela**

    Body:
        data_pagamento: str ISO (obrigatório)
        modality_id: str (obrigatório - ID da modalidade de pagamento)
        valor_juros: float (opcional, default: 0)
        valor_multa: float (opcional, default: 0)
        observacao: str (opcional)

    Returns:
        200: Pagamento registrado (parcela atualizada + lançamento criado)
        400: Dados inválidos ou parcela já paga
        404: Parcela não encontrada
        500: Erro interno
    """
    try:
        data = request.get_json()

        # Validar campos obrigatórios
        if "data_pagamento" not in data:
            return jsonify({"error": "Campo obrigatório: data_pagamento"}), 400
        if "modality_id" not in data:
            return jsonify({"error": "Campo obrigatório: modality_id"}), 400

        # Parsear dados
        data_pagamento = datetime.fromisoformat(data["data_pagamento"])
        modality_id = data["modality_id"]
        valor_juros = float(data.get("valor_juros", 0.0))
        valor_multa = float(data.get("valor_multa", 0.0))
        observacao = data.get("observacao", "")

        # Obter repositórios
        (
            purchase_repo,
            installment_repo,
            financial_entry_repo,
            modality_repo,
            audit_repo
        ) = get_repositories(g.company_id)
        audit_service = AuditService(audit_repo)

        # Executar use case
        use_case = PayCreditInstallment(
            installment_repo,
            purchase_repo,
            financial_entry_repo,
            modality_repo
        )
        result = use_case.execute(
            installment_id=installment_id,
            data_pagamento=data_pagamento,
            pago_por_user_id=g.user_id,
            pago_por_nome=g.name,
            modality_id=modality_id,
            valor_juros=valor_juros,
            valor_multa=valor_multa,
            observacao=observacao
        )

        # Log de auditoria
        audit_service.log(
            action="PAY_CREDIT_INSTALLMENT",
            user_id=g.user_id,
            user_email=g.email,
            company_id=g.company_id,
            target_type="credit_installment",
            target_id=installment_id,
            details={
                "credit_purchase_id": credit_purchase_id,
                "numero_parcela": result["installment"]["numero_parcela"],
                "valor_pago": result["installment"]["valor_total"],
                "financial_entry_id": result["financial_entry"]["id"]
            }
        )

        return jsonify(result), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Erro interno do servidor"}), 500


@credit_purchase_bp.route(
    "/credit-purchases/<credit_purchase_id>/installments/<installment_id>/unpay",
    methods=["POST"]
)
@require_auth
@require_feature("credit_installments.unpay")
def unpay_installment(credit_purchase_id, installment_id):
    """
    Desfaz o pagamento de uma parcela (remove lançamento financeiro vinculado).

    Returns:
        200: Pagamento desfeito
        400: Parcela não está paga
        404: Parcela não encontrada
        500: Erro interno
    """
    try:
        # Obter repositórios
        (
            purchase_repo,
            installment_repo,
            financial_entry_repo,
            _,
            audit_repo
        ) = get_repositories(g.company_id)
        audit_service = AuditService(audit_repo)

        # Executar use case
        use_case = UnpayCreditInstallment(
            installment_repo,
            purchase_repo,
            financial_entry_repo
        )
        result = use_case.execute(installment_id)

        # Log de auditoria
        audit_service.log(
            action="UNPAY_CREDIT_INSTALLMENT",
            user_id=g.user_id,
            user_email=g.email,
            company_id=g.company_id,
            target_type="credit_installment",
            target_id=installment_id,
            details={
                "credit_purchase_id": credit_purchase_id,
                "numero_parcela": result["installment"]["numero_parcela"]
            }
        )

        return jsonify(result), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Erro interno do servidor"}), 500


# ==================== DASHBOARD ====================

@credit_purchase_bp.route("/credit-purchases/dashboard/installments-by-date", methods=["GET"])
@require_auth
@require_feature("credit_purchases.read")
def get_dashboard_installments_by_date():
    """
    Obtém dados do dashboard com parcelas agrupadas por data de vencimento.

    Query params:
        start_date: str ISO (obrigatório)
        end_date: str ISO (obrigatório)
        status: str (opcional: pendente, pago, atrasado)

    Returns:
        200: Dados do dashboard
        400: Parâmetros inválidos
        500: Erro interno
    """
    try:
        # Validar parâmetros
        start_date_str = request.args.get("start_date")
        end_date_str = request.args.get("end_date")

        if not start_date_str or not end_date_str:
            return jsonify({
                "error": "Parâmetros obrigatórios: start_date e end_date"
            }), 400

        start_date = datetime.fromisoformat(start_date_str)
        end_date = datetime.fromisoformat(end_date_str)
        status = request.args.get("status")

        # Obter repositórios
        (purchase_repo, installment_repo, _, _, _) = get_repositories(g.company_id)

        # Executar use case
        use_case = GetCreditDashboard(installment_repo, purchase_repo)
        result = use_case.execute(start_date, end_date, status)

        return jsonify(result), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Erro interno do servidor"}), 500


@credit_purchase_bp.route("/credit-purchases/dashboard/totals", methods=["GET"])
@require_auth
@require_feature("credit_purchases.read")
def get_dashboard_totals():
    """
    Obtém totais gerais das parcelas (a receber, recebido, atrasado, etc.).

    Query params:
        start_date: str ISO (opcional)
        end_date: str ISO (opcional)

    Returns:
        200: Totais calculados
        500: Erro interno
    """
    try:
        start_date_str = request.args.get("start_date")
        end_date_str = request.args.get("end_date")

        start_date = datetime.fromisoformat(start_date_str) if start_date_str else None
        end_date = datetime.fromisoformat(end_date_str) if end_date_str else None

        # Obter repositórios
        (_, installment_repo, _, _, _) = get_repositories(g.company_id)

        # Buscar totais
        totals = installment_repo.get_totals(start_date, end_date)

        return jsonify(totals), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Erro interno do servidor"}), 500


@credit_purchase_bp.route("/credit-purchases/dashboard/overdue", methods=["GET"])
@require_auth
@require_feature("credit_purchases.read")
def get_overdue_installments():
    """
    Obtém todas as parcelas atrasadas.

    Returns:
        200: Lista de parcelas atrasadas com dados das compras
        500: Erro interno
    """
    try:
        # Obter repositórios
        (purchase_repo, installment_repo, _, _, _) = get_repositories(g.company_id)

        # Buscar parcelas atrasadas
        overdue_installments = installment_repo.find_overdue()

        # Enriquecer com dados das compras
        result = []
        for inst in overdue_installments:
            inst_dict = inst.to_dict()

            # Buscar dados da compra
            credit_purchase = purchase_repo.find_by_id(inst.credit_purchase_id)
            if credit_purchase:
                inst_dict["pagante_nome"] = credit_purchase.pagante_nome
                inst_dict["pagante_telefone"] = credit_purchase.pagante_telefone
                inst_dict["descricao_compra"] = credit_purchase.descricao_compra

            result.append(inst_dict)

        return jsonify({
            "total_atrasado": sum(inst["valor_total"] for inst in result),
            "quantidade_parcelas": len(result),
            "installments": result
        }), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Erro interno do servidor"}), 500


@credit_purchase_bp.route("/credit-purchases/dashboard/due-soon", methods=["GET"])
@require_auth
@require_feature("credit_purchases.read")
def get_due_soon_installments():
    """
    Obtém parcelas que vencem em breve.

    Query params:
        days: int (default: 7) - Próximos N dias

    Returns:
        200: Lista de parcelas que vencem em breve
        500: Erro interno
    """
    try:
        days = int(request.args.get("days", 7))

        # Obter repositórios
        (purchase_repo, installment_repo, _, _, _) = get_repositories(g.company_id)

        # Buscar parcelas
        due_soon_installments = installment_repo.find_due_soon(days)

        # Enriquecer com dados das compras
        result = []
        for inst in due_soon_installments:
            inst_dict = inst.to_dict()

            # Buscar dados da compra
            credit_purchase = purchase_repo.find_by_id(inst.credit_purchase_id)
            if credit_purchase:
                inst_dict["pagante_nome"] = credit_purchase.pagante_nome
                inst_dict["pagante_telefone"] = credit_purchase.pagante_telefone
                inst_dict["descricao_compra"] = credit_purchase.descricao_compra

            result.append(inst_dict)

        return jsonify({
            "periodo_dias": days,
            "total_valor": sum(inst["valor_total"] for inst in result),
            "quantidade_parcelas": len(result),
            "installments": result
        }), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Erro interno do servidor"}), 500
