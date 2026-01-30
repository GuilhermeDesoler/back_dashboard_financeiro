from src.domain.repositories import UserRepository
from src.infra.security import PasswordHash


class ChangePassword:
    def __init__(self, user_repository: UserRepository):
        self._user_repository = user_repository

    def execute(self, user_id: str, current_password: str, new_password: str) -> bool:
        """
        Altera a senha de um usuário

        Args:
            user_id: ID do usuário
            current_password: Senha atual
            new_password: Nova senha

        Returns:
            True se a senha foi alterada com sucesso

        Raises:
            ValueError: Se a senha atual estiver incorreta ou se os dados forem inválidos
        """
        if not current_password or not new_password:
            raise ValueError("Senha atual e nova senha são obrigatórias")

        if len(new_password) < 6:
            raise ValueError("A nova senha deve ter pelo menos 6 caracteres")

        user = self._user_repository.find_by_id(user_id)
        if not user:
            raise ValueError("Usuário não encontrado")

        # Verifica se a senha atual está correta
        if not PasswordHash.verify(current_password, user.password_hash):
            raise ValueError("Senha atual incorreta")

        # Gera hash da nova senha
        new_password_hash = PasswordHash.hash(new_password)

        # Atualiza a senha do usuário
        user.password_hash = new_password_hash
        self._user_repository.update(user.id, user)

        return True
