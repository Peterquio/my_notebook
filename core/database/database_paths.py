#1. Centralização
#Sem isso, você acabaria com:
#sqlite3.connect("user_data/users/admin.db")
#espalhado em 200 arquivos. Isso destrói manutenção.
#2. Segurança arquitetural
#Se no futuro mudar de SQLite local → PostgreSQL cloud ou:
#local → Google Drive sync
#você altera o núcleo do sistema.
#3. Preparação para multiusuário
#Cada usuário terá:
#user_data/users/diego.db
#user_data/users/alecio.db
#user_data/users/admin.db
#Isso combina perfeitamente com sua visão de “sistema operacional pessoal”.

from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]

USER_DATA_DIR = BASE_DIR / "user_data"
USERS_DIR = USER_DATA_DIR / "users"


def inicializar_pastas_database() -> None:
    """
    Cria automaticamente as pastas necessárias
    para armazenamento dos bancos dos usuários.
    """

    USER_DATA_DIR.mkdir(parents=True, exist_ok=True)
    USERS_DIR.mkdir(parents=True, exist_ok=True)


def obter_caminho_banco_usuario(username: str) -> Path:
    """
    Retorna o caminho do banco SQLite do usuário.
    """

    nome_seguro = username.strip().lower().replace(" ", "_")

    return USERS_DIR / f"{nome_seguro}.db"