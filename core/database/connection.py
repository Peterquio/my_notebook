#abrir conexões com SQLite

import sqlite3
from pathlib import Path


def criar_conexao(caminho_banco: Path) -> sqlite3.Connection:
    conexao = sqlite3.connect(caminho_banco)
    conexao.row_factory = sqlite3.Row
    return conexao