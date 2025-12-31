"""
Entidade de Compra no Crediário (Registro Bruto/Master)
"""
from datetime import datetime
from typing import Optional
from uuid import uuid4


class CreditPurchase:
    """
    Representa uma compra realizada no crediário (dados brutos).
    Contém informações gerais da compra que será parcelada.
    """

    def __init__(
        self,
        pagante_nome: str,
        descricao_compra: str,
        valor_total: float,
        numero_parcelas: int,
        data_inicio_pagamento: datetime,
        registrado_por_user_id: str,
        registrado_por_nome: str,
        pagante_documento: Optional[str] = None,
        pagante_telefone: Optional[str] = None,
        valor_entrada: float = 0.0,
        intervalo_dias: int = 30,
        taxa_juros_mensal: float = 0.0,
        status: str = "ativo",
        id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        """
        Args:
            pagante_nome: Nome do cliente/pagante
            descricao_compra: Descrição do que foi comprado
            valor_total: Valor total da compra
            numero_parcelas: Quantidade de parcelas
            data_inicio_pagamento: Data do primeiro vencimento
            registrado_por_user_id: ID do usuário que criou o registro
            registrado_por_nome: Nome do usuário que criou o registro
            pagante_documento: CPF/CNPJ do pagante (opcional)
            pagante_telefone: Telefone de contato (opcional)
            valor_entrada: Valor da entrada paga (default: 0)
            intervalo_dias: Dias entre parcelas (default: 30)
            taxa_juros_mensal: Taxa de juros mensal em % (default: 0)
            status: Status da compra (ativo, cancelado, concluido)
            id: UUID da compra (gerado automaticamente se não fornecido)
            created_at: Data de criação (gerada automaticamente)
            updated_at: Data de atualização (gerada automaticamente)
        """
        self.id = id or str(uuid4())

        # Informações do Pagante
        self.pagante_nome = pagante_nome
        self.pagante_documento = pagante_documento
        self.pagante_telefone = pagante_telefone

        # Informações da Compra
        self.descricao_compra = descricao_compra
        self.valor_total = valor_total
        self.valor_entrada = valor_entrada
        self.numero_parcelas = numero_parcelas

        # Configurações de Pagamento
        self.data_inicio_pagamento = data_inicio_pagamento
        self.intervalo_dias = intervalo_dias
        self.taxa_juros_mensal = taxa_juros_mensal

        # Auditoria e Controle
        self.registrado_por_user_id = registrado_por_user_id
        self.registrado_por_nome = registrado_por_nome
        self.status = status

        # Timestamps
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def to_dict(self) -> dict:
        """Converte a entidade para dicionário"""
        return {
            "id": self.id,
            "pagante_nome": self.pagante_nome,
            "pagante_documento": self.pagante_documento,
            "pagante_telefone": self.pagante_telefone,
            "descricao_compra": self.descricao_compra,
            "valor_total": self.valor_total,
            "valor_entrada": self.valor_entrada,
            "numero_parcelas": self.numero_parcelas,
            "data_inicio_pagamento": self.data_inicio_pagamento,
            "intervalo_dias": self.intervalo_dias,
            "taxa_juros_mensal": self.taxa_juros_mensal,
            "registrado_por_user_id": self.registrado_por_user_id,
            "registrado_por_nome": self.registrado_por_nome,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @staticmethod
    def from_dict(data: dict) -> "CreditPurchase":
        """Cria uma entidade a partir de um dicionário"""
        return CreditPurchase(
            id=data.get("id"),
            pagante_nome=data["pagante_nome"],
            pagante_documento=data.get("pagante_documento"),
            pagante_telefone=data.get("pagante_telefone"),
            descricao_compra=data["descricao_compra"],
            valor_total=data["valor_total"],
            valor_entrada=data.get("valor_entrada", 0.0),
            numero_parcelas=data["numero_parcelas"],
            data_inicio_pagamento=data["data_inicio_pagamento"],
            intervalo_dias=data.get("intervalo_dias", 30),
            taxa_juros_mensal=data.get("taxa_juros_mensal", 0.0),
            registrado_por_user_id=data["registrado_por_user_id"],
            registrado_por_nome=data["registrado_por_nome"],
            status=data.get("status", "ativo"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )

    def cancel(self) -> None:
        """Cancela a compra"""
        self.status = "cancelado"
        self.updated_at = datetime.utcnow()

    def complete(self) -> None:
        """Marca a compra como concluída (todas parcelas pagas)"""
        self.status = "concluido"
        self.updated_at = datetime.utcnow()

    def reactivate(self) -> None:
        """Reativa a compra"""
        self.status = "ativo"
        self.updated_at = datetime.utcnow()

    def update_contact_info(
        self,
        pagante_telefone: Optional[str] = None,
        pagante_documento: Optional[str] = None
    ) -> None:
        """Atualiza informações de contato do pagante"""
        if pagante_telefone is not None:
            self.pagante_telefone = pagante_telefone
        if pagante_documento is not None:
            self.pagante_documento = pagante_documento
        self.updated_at = datetime.utcnow()

    def validate(self) -> None:
        """Valida os dados da compra"""
        if not self.pagante_nome or not self.pagante_nome.strip():
            raise ValueError("Nome do pagante é obrigatório")

        if not self.descricao_compra or not self.descricao_compra.strip():
            raise ValueError("Descrição da compra é obrigatória")

        if self.valor_total <= 0:
            raise ValueError("Valor total deve ser maior que zero")

        if self.valor_entrada < 0:
            raise ValueError("Valor de entrada não pode ser negativo")

        if self.valor_entrada >= self.valor_total:
            raise ValueError("Valor de entrada deve ser menor que o valor total")

        if self.numero_parcelas <= 0:
            raise ValueError("Número de parcelas deve ser maior que zero")

        if self.intervalo_dias <= 0:
            raise ValueError("Intervalo entre parcelas deve ser maior que zero")

        if self.taxa_juros_mensal < 0:
            raise ValueError("Taxa de juros não pode ser negativa")

        if not self.registrado_por_user_id:
            raise ValueError("ID do usuário que registrou é obrigatório")

        if not self.registrado_por_nome or not self.registrado_por_nome.strip():
            raise ValueError("Nome do usuário que registrou é obrigatório")
