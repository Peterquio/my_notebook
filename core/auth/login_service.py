#Esse service:
#localiza o banco do usuário
#abre conexão
#busca hash da senha
#compara usando bcrypt
#retorna True ou False

from core.auth.password_service import PasswordService
from core.database.database_manager import DatabaseManager


class LoginService:
    def autenticar(self, username: str, senha: str) -> bool:
        username = username.strip().lower()

        database_manager = DatabaseManager(username)

        try:
            with database_manager.get_connection() as conexao:
                cursor = conexao.cursor()

                cursor.execute("""
                    SELECT password_hash
                    FROM user_profile
                    WHERE id = 1
                """)

                resultado = cursor.fetchone()

                if not resultado:
                    return False

                senha_hash = resultado["password_hash"]

                return PasswordService.verificar_senha(
                    senha,
                    senha_hash
                )

        except Exception:
            return False