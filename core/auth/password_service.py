#Função responsável por criptografar e ler a senha

import bcrypt


class PasswordService:
    @staticmethod
    def gerar_hash(senha: str) -> str:
        senha_bytes = senha.encode("utf-8")
        hash_bytes = bcrypt.hashpw(senha_bytes, bcrypt.gensalt())
        return hash_bytes.decode("utf-8")

    @staticmethod
    def verificar_senha(senha: str, senha_hash: str) -> bool:
        senha_bytes = senha.encode("utf-8")
        hash_bytes = senha_hash.encode("utf-8")
        return bcrypt.checkpw(senha_bytes, hash_bytes)