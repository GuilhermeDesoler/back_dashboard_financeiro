from src.domain.entities import PaymentModality
from src.domain.repositories import PaymentModalityRepository


class UpdatePaymentModality:
    def __init__(self, repository: PaymentModalityRepository):
        self._repository = repository

    def execute(self, modality_id: str, name: str = None, color: str = None) -> PaymentModality:
        modality = self._repository.find_by_id(modality_id)
        if not modality:
            raise ValueError("Modalidade não encontrada")

        if name is not None:
            if not name.strip():
                raise ValueError("Nome da modalidade não pode ser vazio")

            existing = self._repository.find_by_name(name)
            if existing and existing.id != modality_id:
                raise ValueError(f"Modalidade '{name}' já existe")

            modality.name = name.strip()

        if color is not None:
            if not color.strip():
                raise ValueError("Cor da modalidade não pode ser vazia")

            modality.color = color.strip()

        updated = self._repository.update(modality_id, modality)
        if not updated:
            raise ValueError("Erro ao atualizar modalidade")

        return updated
