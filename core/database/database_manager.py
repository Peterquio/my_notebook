#1. Descobrir o caminho do banco do usuário
#2. Abrir conexão com SQLite
#3. Inicializar a estrutura mínima do banco (GLOBAL_SCHEMA)

from sqlite3 import Connection

from core.database.connection import criar_conexao
from core.database.schema import GLOBAL_SCHEMA
from core.database.database_paths import (
    inicializar_pastas_database,
    obter_caminho_banco_usuario,
)


class DatabaseManager:
    def __init__(self, username: str):
        self.username = username
        self.database_path = obter_caminho_banco_usuario(username)

    def conectar(self) -> Connection:
        inicializar_pastas_database()
        return criar_conexao(self.database_path)

    def inicializar_banco_usuario(self) -> None:
        with self.conectar() as conexao:
            cursor = conexao.cursor()

            cursor.executescript(GLOBAL_SCHEMA)

            conexao.commit()