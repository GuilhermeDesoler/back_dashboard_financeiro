"""
Entidade de Parcela do Crediário (Registro Tabelado)
"""
from datetime import datetime, date
from typing import Optional
from uuid import uuid4


class CreditInstallment:
    """
    Representa uma parcela individual de uma compra no crediário.
    Cada compra gera N parcelas que serão pagas ao longo do tempo.
    """

    def __init__(
        self,
        credit_purchase_id: str,
        numero_parcela: int,
        valor_parcela: float,
        data_vencimento: datetime,
        valor_juros: float = 0.0,
        valor_multa: float = 0.0,
        status: str = "pendente",
        data_pagamento: Optional[datetime] = None,
        financial_entry_id: Optional[str] = None,
        pago_por_user_id: Optional[str] = None,
        pago_por_nome: Optional[str] = None,
        observacao: str = "",
        id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        """
        Args:
            credit_purchase_id: ID da compra no crediário (FK)
            numero_parcela: Número da parcela (1, 2, 3...)
            valor_parcela: Valor original da parcela
            data_vencimento: Data de vencimento da parcela
            valor_juros: Valor de juros aplicados (default: 0)
            valor_multa: Valor de multa por atraso (default: 0)
            status: Status da parcela (pendente, pago, atrasado, cancelado)
            data_pagamento: Data em que foi pago (None se não pago)
            financial_entry_id: ID do lançamento financeiro vinculado (quando pago)
            pago_por_user_id: ID do usuário que registrou o pagamento
            pago_por_nome: Nome do usuário que registrou o pagamento
            observacao: Observações sobre a parcela
            id: UUID da parcela (gerado automaticamente)
            created_at: Data de criação
            updated_at: Data de atualização
        """
        self.id = id or str(uuid4())
        self.credit_purchase_id = credit_purchase_id
        self.numero_parcela = numero_parcela
        self.valor_parcela = valor_parcela
        self.valor_juros = valor_juros
        self.valor_multa = valor_multa
        self.data_vencimento = data_vencimento
        self.data_pagamento = data_pagamento
        self.status = status
        self.financial_entry_id = financial_entry_id
        self.pago_por_user_id = pago_por_user_id
        self.pago_por_nome = pago_por_nome
        self.observacao = observacao
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def to_dict(self) -> dict:
        """Converte a entidade para dicionário"""
        return {
            "id": self.id,
            "credit_purchase_id": self.credit_purchase_id,
            "numero_parcela": self.numero_parcela,
            "valor_parcela": self.valor_parcela,
            "valor_juros": self.valor_juros,
            "valor_multa": self.valor_multa,
            "valor_total": self.get_valor_total(),
            "data_vencimento": self.data_vencimento,
            "data_pagamento": self.data_pagamento,
            "status": self.status,
            "financial_entry_id": self.financial_entry_id,
            "pago_por_user_id": self.pago_por_user_id,
            "pago_por_nome": self.pago_por_nome,
            "observacao": self.observacao,
            "dias_atraso": self.get_dias_atraso(),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @staticmethod
    def from_dict(data: dict) -> "CreditInstallment":
        """Cria uma entidade a partir de um dicionário"""
        return CreditInstallment(
            id=data.get("id"),
            credit_purchase_id=data["credit_purchase_id"],
            numero_parcela=data["numero_parcela"],
            valor_parcela=data["valor_parcela"],
            valor_juros=data.get("valor_juros", 0.0),
            valor_multa=data.get("valor_multa", 0.0),
            data_vencimento=data["data_vencimento"],
            data_pagamento=data.get("data_pagamento"),
            status=data.get("status", "pendente"),
            financial_entry_id=data.get("financial_entry_id"),
            pago_por_user_id=data.get("pago_por_user_id"),
            pago_por_nome=data.get("pago_por_nome"),
            observacao=data.get("observacao", ""),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )

    def get_valor_total(self) -> float:
        """Calcula o valor total da parcela (parcela + juros + multa)"""
        return self.valor_parcela + self.valor_juros + self.valor_multa

    def get_dias_atraso(self) -> int:
        """
        Calcula os dias de atraso da parcela.
        Retorna 0 se já foi paga ou se ainda não venceu.
        """
        if self.data_pagamento is not None:
            # Se já foi paga, verificar se foi paga com atraso
            vencimento_date = self.data_vencimento.date() if isinstance(self.data_vencimento, datetime) else self.data_vencimento
            pagamento_date = self.data_pagamento.date() if isinstance(self.data_pagamento, datetime) else self.data_pagamento

            if pagamento_date > vencimento_date:
                return (pagamento_date - vencimento_date).days
            return 0

        # Se não foi paga, calcular atraso baseado na data atual
        hoje = date.today()
        vencimento_date = self.data_vencimento.date() if isinstance(self.data_vencimento, datetime) else self.data_vencimento

        if hoje > vencimento_date:
            return (hoje - vencimento_date).days
        return 0

    def marcar_como_pago(
        self,
        data_pagamento: datetime,
        financial_entry_id: str,
        pago_por_user_id: str,
        pago_por_nome: str,
        valor_juros: float = 0.0,
        valor_multa: float = 0.0,
        observacao: str = ""
    ) -> None:
        """
        Marca a parcela como paga e vincula ao lançamento financeiro.

        Args:
            data_pagamento: Data em que foi realizado o pagamento
            financial_entry_id: ID do lançamento financeiro criado
            pago_por_user_id: ID do usuário que registrou o pagamento
            pago_por_nome: Nome do usuário que registrou o pagamento
            valor_juros: Juros cobrados no pagamento
            valor_multa: Multa cobrada no pagamento
            observacao: Observações sobre o pagamento
        """
        self.status = "pago"
        self.data_pagamento = data_pagamento
        self.financial_entry_id = financial_entry_id
        self.pago_por_user_id = pago_por_user_id
        self.pago_por_nome = pago_por_nome
        self.valor_juros = valor_juros
        self.valor_multa = valor_multa
        if observacao:
            self.observacao = observacao
        self.updated_at = datetime.utcnow()

    def desfazer_pagamento(self) -> None:
        """
        Remove o pagamento da parcela, voltando para status pendente ou atrasado.
        """
        self.data_pagamento = None
        self.financial_entry_id = None
        self.pago_por_user_id = None
        self.pago_por_nome = None

        # Recalcular status baseado na data de vencimento
        if self.get_dias_atraso() > 0:
            self.status = "atrasado"
        else:
            self.status = "pendente"

        self.updated_at = datetime.utcnow()

    def marcar_como_cancelado(self) -> None:
        """Cancela a parcela"""
        self.status = "cancelado"
        self.updated_at = datetime.utcnow()

    def atualizar_status_automatico(self) -> None:
        """
        Atualiza o status da parcela automaticamente baseado na data de vencimento.
        Deve ser chamado por um job/rotina periódica.
        """
        # Se já está pago ou cancelado, não alterar
        if self.status in ["pago", "cancelado"]:
            return

        dias_atraso = self.get_dias_atraso()

        if dias_atraso > 0:
            self.status = "atrasado"
        else:
            self.status = "pendente"

        self.updated_at = datetime.utcnow()

    def validate(self) -> None:
        """Valida os dados da parcela"""
        if not self.credit_purchase_id:
            raise ValueError("ID da compra no crediário é obrigatório")

        if self.numero_parcela <= 0:
            raise ValueError("Número da parcela deve ser maior que zero")

        if self.valor_parcela <= 0:
            raise ValueError("Valor da parcela deve ser maior que zero")

        if self.valor_juros < 0:
            raise ValueError("Valor de juros não pode ser negativo")

        if self.valor_multa < 0:
            raise ValueError("Valor de multa não pode ser negativo")

        if not self.data_vencimento:
            raise ValueError("Data de vencimento é obrigatória")

        valid_statuses = ["pendente", "pago", "atrasado", "cancelado"]
        if self.status not in valid_statuses:
            raise ValueError(f"Status deve ser um dos seguintes: {', '.join(valid_statuses)}")

        # Se status é "pago", deve ter data de pagamento
        if self.status == "pago":
            if not self.data_pagamento:
                raise ValueError("Parcela paga deve ter data de pagamento")
            if not self.financial_entry_id:
                raise ValueError("Parcela paga deve ter ID do lançamento financeiro")
            if not self.pago_por_user_id:
                raise ValueError("Parcela paga deve ter ID do usuário que registrou o pagamento")
