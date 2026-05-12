#O AuthGuard serve para impedir que uma tela/módulo seja aberto sem login.

from core.auth.session_service import SessionService


class AuthGuard:
    def __init__(self, session_service: SessionService):
        self.session_service = session_service

    def verificar_acesso(self) -> bool:
        return self.session_service.usuario_esta_logado()

    def exigir_login(self) -> None:
        if not self.verificar_acesso():
            raise PermissionError("Usuário não autenticado.")