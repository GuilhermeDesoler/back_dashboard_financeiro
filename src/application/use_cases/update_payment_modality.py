from src.domain.entities import PaymentModality
from src.domain.repositories import PaymentModalityRepository


class UpdatePaymentModality:
    def __init__(self, repository: PaymentModalityRepository):
        self._repository = repository

    def execute(
        self,
        modality_id: str,
        name: str = None,
        color: str = None,
        bank_name: str = None,
        fee_percentage: float = None,
        rental_fee: float = None,
        is_active: bool = None,
        is_credit_plan: bool = None,
        allows_anticipation: bool = None,
        allows_credit_payment: bool = None
    ) -> PaymentModality:
        modality = self._repository.find_by_id(modality_id)
        if not modality:
            raise ValueError("Modalidade não encontrada")

        # Atualizar bank_name primeiro para usar na validação
        updated_bank_name = modality.bank_name
        if bank_name is not None:
            updated_bank_name = bank_name.strip() if bank_name else ""
            modality.bank_name = updated_bank_name

        if name is not None:
            if not name.strip():
                raise ValueError("Nome da modalidade não pode ser vazio")

            # Verificar duplicatas considerando name + bank_name
            existing = self._repository.find_by_name(name, updated_bank_name)
            if existing and existing.id != modality_id:
                raise ValueError(f"Modalidade '{name}' já existe para o banco '{updated_bank_name}'")

            modality.name = name.strip()

        if color is not None:
            if not color.strip():
                raise ValueError("Cor da modalidade não pode ser vazia")

            modality.color = color.strip()

        if fee_percentage is not None:
            modality.fee_percentage = float(fee_percentage)

        if rental_fee is not None:
            modality.rental_fee = float(rental_fee)

        if is_active is not None:
            modality.is_active = is_active

        if is_credit_plan is not None:
            modality.is_credit_plan = is_credit_plan

        if allows_anticipation is not None:
            modality.allows_anticipation = allows_anticipation

        if allows_credit_payment is not None:
            modality.allows_credit_payment = allows_credit_payment

        updated = self._repository.update(modality_id, modality)
        if not updated:
            raise ValueError("Erro ao atualizar modalidade")

        return updated
