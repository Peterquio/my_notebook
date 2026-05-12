import bcrypt


def gerar_hash_senha(senha: str) -> str:
    senha_bytes = senha.encode("utf-8")
    hash_bytes = bcrypt.hashpw(senha_bytes, bcrypt.gensalt())
    return hash_bytes.decode("utf-8")


def verificar_senha(senha: str, hash_salvo: str) -> bool:
    senha_bytes = senha.encode("utf-8")
    hash_bytes = hash_salvo.encode("utf-8")
    return bcrypt.checkpw(senha_bytes, hash_bytes)