"""
Testes automatizados para o sistema de Crediário

Execute com: pytest tests/test_credit_purchase.py -v
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock

# Testes de Entidades
from src.domain.entities.credit_purchase import CreditPurchase
from src.domain.entities.credit_installment import CreditInstallment

# Testes de Use Cases
from src.application.use_cases.create_credit_purchase import CreateCreditPurchase
from src.application.use_cases.pay_credit_installment import PayCreditInstallment
from src.application.use_cases.unpay_credit_installment import UnpayCreditInstallment
from src.application.use_cases.get_credit_purchase_details import GetCreditPurchaseDetails
from src.application.use_cases.cancel_credit_purchase import CancelCreditPurchase


class TestCreditPurchaseEntity:
    """Testes para a entidade CreditPurchase"""

    def test_create_credit_purchase_entity(self):
        """Teste: Criar entidade CreditPurchase"""
        purchase = CreditPurchase(
            pagante_nome="João Silva",
            descricao_compra="Geladeira Brastemp 450L",
            valor_total=3000.00,
            numero_parcelas=10,
            data_inicio_pagamento=datetime(2025, 2, 1),
            registrado_por_user_id="user-123",
            registrado_por_nome="Maria Admin"
        )

        assert purchase.pagante_nome == "João Silva"
        assert purchase.valor_total == 3000.00
        assert purchase.numero_parcelas == 10
        assert purchase.status == "ativo"
        assert purchase.id is not None
        print("✅ CreditPurchase criado com sucesso")

    def test_credit_purchase_validation_error(self):
        """Teste: Validação de campos obrigatórios"""
        purchase = CreditPurchase(
            pagante_nome="",  # Inválido
            descricao_compra="Geladeira",
            valor_total=3000.00,
            numero_parcelas=10,
            data_inicio_pagamento=datetime(2025, 2, 1),
            registrado_por_user_id="user-123",
            registrado_por_nome="Maria Admin"
        )

        with pytest.raises(ValueError, match="Nome do pagante é obrigatório"):
            purchase.validate()
        print("✅ Validação de nome vazio funcionou")

    def test_credit_purchase_to_dict(self):
        """Teste: Conversão para dicionário"""
        purchase = CreditPurchase(
            pagante_nome="João Silva",
            descricao_compra="Geladeira",
            valor_total=3000.00,
            numero_parcelas=10,
            data_inicio_pagamento=datetime(2025, 2, 1),
            registrado_por_user_id="user-123",
            registrado_por_nome="Maria Admin"
        )

        data = purchase.to_dict()
        assert isinstance(data, dict)
        assert data["pagante_nome"] == "João Silva"
        assert data["valor_total"] == 3000.00
        print("✅ Conversão para dict funcionou")

    def test_credit_purchase_cancel(self):
        """Teste: Cancelar compra"""
        purchase = CreditPurchase(
            pagante_nome="João Silva",
            descricao_compra="Geladeira",
            valor_total=3000.00,
            numero_parcelas=10,
            data_inicio_pagamento=datetime(2025, 2, 1),
            registrado_por_user_id="user-123",
            registrado_por_nome="Maria Admin"
        )

        assert purchase.status == "ativo"
        purchase.cancel()
        assert purchase.status == "cancelado"
        print("✅ Cancelamento de compra funcionou")


class TestCreditInstallmentEntity:
    """Testes para a entidade CreditInstallment"""

    def test_create_installment_entity(self):
        """Teste: Criar entidade CreditInstallment"""
        installment = CreditInstallment(
            credit_purchase_id="purchase-123",
            numero_parcela=1,
            valor_parcela=250.00,
            data_vencimento=datetime(2025, 2, 1)
        )

        assert installment.numero_parcela == 1
        assert installment.valor_parcela == 250.00
        assert installment.status == "pendente"
        assert installment.id is not None
        print("✅ CreditInstallment criado com sucesso")

    def test_installment_get_valor_total(self):
        """Teste: Cálculo do valor total (parcela + juros + multa)"""
        installment = CreditInstallment(
            credit_purchase_id="purchase-123",
            numero_parcela=1,
            valor_parcela=250.00,
            data_vencimento=datetime(2025, 2, 1),
            valor_juros=10.00,
            valor_multa=5.00
        )

        assert installment.get_valor_total() == 265.00
        print("✅ Cálculo de valor total funcionou")

    def test_installment_dias_atraso(self):
        """Teste: Cálculo de dias de atraso"""
        # Parcela vencida há 10 dias
        data_vencimento = datetime.now() - timedelta(days=10)
        installment = CreditInstallment(
            credit_purchase_id="purchase-123",
            numero_parcela=1,
            valor_parcela=250.00,
            data_vencimento=data_vencimento
        )

        dias_atraso = installment.get_dias_atraso()
        assert dias_atraso == 10
        print(f"✅ Cálculo de dias de atraso: {dias_atraso} dias")

    def test_installment_marcar_como_pago(self):
        """Teste: Marcar parcela como paga"""
        installment = CreditInstallment(
            credit_purchase_id="purchase-123",
            numero_parcela=1,
            valor_parcela=250.00,
            data_vencimento=datetime(2025, 2, 1)
        )

        assert installment.status == "pendente"

        installment.marcar_como_pago(
            data_pagamento=datetime(2025, 2, 1),
            financial_entry_id="entry-123",
            pago_por_user_id="user-456",
            pago_por_nome="Carlos Vendedor"
        )

        assert installment.status == "pago"
        assert installment.data_pagamento is not None
        assert installment.pago_por_nome == "Carlos Vendedor"
        assert installment.financial_entry_id == "entry-123"
        print("✅ Marcar como pago funcionou")

    def test_installment_desfazer_pagamento(self):
        """Teste: Desfazer pagamento de parcela"""
        # Data futura para não ficar atrasada
        data_futura = datetime.now() + timedelta(days=30)

        installment = CreditInstallment(
            credit_purchase_id="purchase-123",
            numero_parcela=1,
            valor_parcela=250.00,
            data_vencimento=data_futura,
            status="pago",
            data_pagamento=datetime.now(),
            financial_entry_id="entry-123"
        )

        assert installment.status == "pago"

        installment.desfazer_pagamento()

        # Pode ser pendente ou atrasado dependendo da data
        assert installment.status in ["pendente", "atrasado"]
        assert installment.data_pagamento is None
        assert installment.financial_entry_id is None
        print("✅ Desfazer pagamento funcionou")


class TestCreateCreditPurchaseUseCase:
    """Testes para o use case CreateCreditPurchase"""

    def test_create_purchase_generates_installments(self):
        """Teste: Criar compra gera parcelas automaticamente"""
        # Mock dos repositórios
        purchase_repo = Mock()
        installment_repo = Mock()

        # Configurar mocks
        purchase_repo.create.return_value = CreditPurchase(
            id="purchase-123",
            pagante_nome="João Silva",
            descricao_compra="Geladeira",
            valor_total=3000.00,
            numero_parcelas=10,
            data_inicio_pagamento=datetime(2025, 2, 1),
            registrado_por_user_id="user-123",
            registrado_por_nome="Maria Admin",
            valor_entrada=500.00
        )

        installment_repo.create_many.return_value = []

        # Executar use case
        use_case = CreateCreditPurchase(purchase_repo, installment_repo)
        result = use_case.execute(
            pagante_nome="João Silva",
            descricao_compra="Geladeira",
            valor_total=3000.00,
            numero_parcelas=10,
            data_inicio_pagamento=datetime(2025, 2, 1),
            registrado_por_user_id="user-123",
            registrado_por_nome="Maria Admin",
            valor_entrada=500.00
        )

        # Verificar que create_many foi chamado com 10 parcelas
        assert installment_repo.create_many.called
        created_installments = installment_repo.create_many.call_args[0][0]
        assert len(created_installments) == 10

        # Verificar valor das parcelas (3000 - 500) / 10 = 250
        assert created_installments[0].valor_parcela == 250.00

        # Verificar datas de vencimento
        assert created_installments[0].data_vencimento == datetime(2025, 2, 1)
        assert created_installments[1].data_vencimento == datetime(2025, 3, 3)  # 30 dias depois

        print("✅ Geração automática de parcelas funcionou")

    def test_installment_value_adjustment(self):
        """Teste: Ajuste de valor da última parcela por arredondamento"""
        purchase_repo = Mock()
        installment_repo = Mock()

        purchase_repo.create.return_value = CreditPurchase(
            id="purchase-123",
            pagante_nome="João Silva",
            descricao_compra="Notebook",
            valor_total=1000.00,
            numero_parcelas=3,
            data_inicio_pagamento=datetime(2025, 2, 1),
            registrado_por_user_id="user-123",
            registrado_por_nome="Maria Admin",
            valor_entrada=0.00
        )

        installment_repo.create_many.return_value = []

        use_case = CreateCreditPurchase(purchase_repo, installment_repo)
        result = use_case.execute(
            pagante_nome="João Silva",
            descricao_compra="Notebook",
            valor_total=1000.00,
            numero_parcelas=3,
            data_inicio_pagamento=datetime(2025, 2, 1),
            registrado_por_user_id="user-123",
            registrado_por_nome="Maria Admin"
        )

        created_installments = installment_repo.create_many.call_args[0][0]

        # Soma das parcelas deve ser igual ao valor total
        total_parcelas = sum(inst.valor_parcela for inst in created_installments)
        assert total_parcelas == 1000.00

        print(f"✅ Ajuste de arredondamento: {created_installments[0].valor_parcela} + {created_installments[1].valor_parcela} + {created_installments[2].valor_parcela} = {total_parcelas}")


class TestPayCreditInstallmentUseCase:
    """Testes para o use case PayCreditInstallment"""

    def test_pay_installment_creates_financial_entry(self):
        """Teste: Pagar parcela cria FinancialEntry automaticamente"""
        # Mocks
        installment_repo = Mock()
        purchase_repo = Mock()
        financial_entry_repo = Mock()
        modality_repo = Mock()

        # Configurar parcela pendente
        installment = CreditInstallment(
            id="inst-123",
            credit_purchase_id="purchase-123",
            numero_parcela=1,
            valor_parcela=250.00,
            data_vencimento=datetime(2025, 2, 1),
            status="pendente"
        )

        # Configurar compra ativa
        purchase = CreditPurchase(
            id="purchase-123",
            pagante_nome="João Silva",
            descricao_compra="Geladeira",
            valor_total=3000.00,
            numero_parcelas=10,
            data_inicio_pagamento=datetime(2025, 2, 1),
            registrado_por_user_id="user-123",
            registrado_por_nome="Maria Admin",
            status="ativo"
        )

        # Configurar modalidade
        from src.domain.entities.payment_modality import PaymentModality
        modality = PaymentModality(
            id="mod-123",
            name="PIX",
            color="#00FF00",
            is_active=True
        )

        # Configurar mocks
        installment_repo.find_by_id.return_value = installment
        purchase_repo.find_by_id.return_value = purchase
        modality_repo.find_by_id.return_value = modality

        # Mock para verificar se todas parcelas pagas (retorna lista vazia = nenhuma paga ainda)
        installment_repo.find_by_credit_purchase.return_value = [installment]

        from src.domain.entities.financial_entry import FinancialEntry
        financial_entry = FinancialEntry(
            id="entry-123",
            value=250.00,
            date=datetime(2025, 2, 1),
            modality_id="mod-123",
            modality_name="PIX",
            modality_color="#00FF00"
        )
        financial_entry_repo.create.return_value = financial_entry
        installment_repo.update.return_value = installment

        # Executar use case
        use_case = PayCreditInstallment(
            installment_repo,
            purchase_repo,
            financial_entry_repo,
            modality_repo
        )

        result = use_case.execute(
            installment_id="inst-123",
            data_pagamento=datetime(2025, 2, 1),
            pago_por_user_id="user-456",
            pago_por_nome="Carlos Vendedor",
            modality_id="mod-123"
        )

        # Verificar que FinancialEntry foi criado
        assert financial_entry_repo.create.called
        assert installment_repo.update.called
        assert result["installment"]["status"] == "pago"
        assert result["financial_entry"]["id"] == "entry-123"

        print("✅ Pagamento cria FinancialEntry automaticamente")


class TestCancelCreditPurchaseUseCase:
    """Testes para o use case CancelCreditPurchase"""

    def test_cancel_purchase_cancels_pending_installments(self):
        """Teste: Cancelar compra cancela parcelas pendentes"""
        purchase_repo = Mock()
        installment_repo = Mock()

        # Compra ativa
        purchase = CreditPurchase(
            id="purchase-123",
            pagante_nome="João Silva",
            descricao_compra="Geladeira",
            valor_total=3000.00,
            numero_parcelas=10,
            data_inicio_pagamento=datetime(2025, 2, 1),
            registrado_por_user_id="user-123",
            registrado_por_nome="Maria Admin",
            status="ativo"
        )

        purchase_repo.find_by_id.return_value = purchase
        purchase_repo.update.return_value = purchase
        installment_repo.cancel_all_by_credit_purchase.return_value = 7  # 7 parcelas canceladas

        use_case = CancelCreditPurchase(purchase_repo, installment_repo)
        result = use_case.execute("purchase-123")

        assert result["credit_purchase"]["status"] == "cancelado"
        assert result["canceled_installments"] == 7
        assert installment_repo.cancel_all_by_credit_purchase.called

        print("✅ Cancelamento de compra cancela parcelas pendentes")


def test_summary():
    """Exibe resumo dos testes"""
    print("\n" + "="*60)
    print("📊 RESUMO DOS TESTES - SISTEMA DE CREDIÁRIO")
    print("="*60)
    print("\n✅ Entidades:")
    print("   - CreditPurchase: criação, validação, conversão, cancelamento")
    print("   - CreditInstallment: criação, cálculos, marcar/desfazer pagamento")
    print("\n✅ Use Cases:")
    print("   - CreateCreditPurchase: geração automática de parcelas")
    print("   - PayCreditInstallment: criação de FinancialEntry")
    print("   - CancelCreditPurchase: cancelamento de parcelas")
    print("\n🎯 Funcionalidades Validadas:")
    print("   ✓ Registro de pagamento de parcelas")
    print("   ✓ Criação automática de lançamentos financeiros")
    print("   ✓ Cálculo de dias de atraso")
    print("   ✓ Geração automática de parcelas com datas corretas")
    print("   ✓ Ajuste de arredondamento na última parcela")
    print("   ✓ Validações de dados")
    print("="*60 + "\n")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
