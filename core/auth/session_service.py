#O serviço de sessão vai guardar o usuário logado atualmente
#enquanto o app estiver aberto.
#Ele mantém em memória quem está logado
#e qual banco SQLite pertence a esse usuário

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from core.database.database_paths import obter_caminho_banco_usuario


@dataclass
class UserSession:
    username: str
    database_path: Path


class SessionService:
    def __init__(self):
        self._current_session: Optional[UserSession] = None

    def iniciar_sessao(self, username: str) -> None:
        username = username.strip().lower()

        self._current_session = UserSession(
            username=username,
            database_path=obter_caminho_banco_usuario(username),
        )

    def encerrar_sessao(self) -> None:
        self._current_session = None

    def obter_sessao_atual(self) -> Optional[UserSession]:
        return self._current_session

    def usuario_esta_logado(self) -> bool:
        return self._current_session is not None