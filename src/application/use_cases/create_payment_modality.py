from src.domain.entities import PaymentModality
from src.domain.repositories import PaymentModalityRepository


class CreatePaymentModality:
    def __init__(self, repository: PaymentModalityRepository):
        self._repository = repository

    def execute(
        self,
        name: str,
        color: str,
        bank_name: str = "",
        fee_percentage: float = 0.0,
        rental_fee: float = 0.0,
        is_active: bool = True,
        is_credit_plan: bool = False,
        allows_anticipation: bool = False,
        allows_credit_payment: bool = False
    ) -> PaymentModality:
        if not name or not name.strip():
            raise ValueError("Nome da modalidade é obrigatório")

        if not color or not color.strip():
            raise ValueError("Cor da modalidade é obrigatória")

        # Verificar duplicatas considerando name + bank_name
        bank_name_normalized = bank_name.strip() if bank_name else ""
        existing = self._repository.find_by_name(name, bank_name_normalized)
        if existing:
            if bank_name_normalized:
                raise ValueError(f"Modalidade '{name}' já existe para o banco '{bank_name_normalized}'")
            else:
                raise ValueError(f"Modalidade '{name}' já existe")

        modality = PaymentModality(
            name=name.strip(),
            color=color.strip(),
            bank_name=bank_name.strip() if bank_name else "",
            fee_percentage=fee_percentage,
            rental_fee=rental_fee,
            is_active=is_active,
            is_credit_plan=is_credit_plan,
            allows_anticipation=allows_anticipation,
            allows_credit_payment=allows_credit_payment
        )

        return self._repository.create(modality)
