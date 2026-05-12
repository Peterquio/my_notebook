#1. validar username e senha
#2. criar o banco do usuário
#3. inicializar o schema do banco
#4. salvar informações básicas do usuário no próprio banco

from core.auth.password_service import PasswordService
from core.database.database_manager import DatabaseManager


class RegisterService:
    def registrar_usuario(self, username: str, senha: str) -> bool:
        username = username.strip().lower()

        if not username:
            raise ValueError("O nome de usuário não pode ficar vazio.")

        if len(senha) < 6:
            raise ValueError("A senha deve ter pelo menos 6 caracteres.")

        database_manager = DatabaseManager(username)
        database_manager.inicializar_banco_usuario()

        senha_hash = PasswordService.gerar_hash(senha)

        with database_manager.conectar() as conexao:
            cursor = conexao.cursor()

            cursor.execute(
                """
                INSERT OR IGNORE INTO user_profile (
                    id,
                    username,
                    password_hash
                )
                VALUES (?, ?, ?)
                """,
                (1, username, senha_hash),
            )

            conexao.commit()

        return True