from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from core.cloud.google_drive.auth.google_credentials import (
    GOOGLE_DRIVE_SCOPES,
    GoogleCredentialsPaths,
    obter_caminhos_google,
)


class GoogleAuthService:
    def __init__(
        self,
        paths: GoogleCredentialsPaths | None = None,
    ) -> None:
        self.paths = paths or obter_caminhos_google()

    def autenticar(self) -> Credentials:
        credenciais = self._carregar_token_existente()

        if credenciais and credenciais.valid:
            return credenciais

        if (
            credenciais
            and credenciais.expired
            and credenciais.refresh_token
        ):
            try:
                credenciais.refresh(Request())
                self._salvar_token(credenciais)
                return credenciais
            except Exception:
                self.desconectar()

        return self._executar_fluxo_oauth()

    def esta_conectado(self) -> bool:
        credenciais = self._carregar_token_existente()

        if not credenciais:
            return False

        if credenciais.valid:
            return True

        if credenciais.expired and credenciais.refresh_token:
            try:
                credenciais.refresh(Request())
                self._salvar_token(credenciais)
                return True
            except Exception:
                return False

        return False

    def desconectar(self) -> None:
        if self.paths.token_path.exists():
            self.paths.token_path.unlink()

    def _carregar_token_existente(
        self,
    ) -> Credentials | None:
        if not self.paths.token_path.exists():
            return None

        try:
            return Credentials.from_authorized_user_file(
                str(self.paths.token_path),
                GOOGLE_DRIVE_SCOPES,
            )
        except Exception:
            return None

    def _executar_fluxo_oauth(self) -> Credentials:
        if not self.paths.credentials_path.exists():
            raise FileNotFoundError(
                "credentials.json não encontrado em: "
                f"{self.paths.credentials_path}"
            )

        fluxo = InstalledAppFlow.from_client_secrets_file(
            str(self.paths.credentials_path),
            GOOGLE_DRIVE_SCOPES,
        )

        credenciais = fluxo.run_local_server(
            port=0,
            open_browser=True,
            authorization_prompt_message=(
                "Abrindo o navegador para conectar "
                "o My Notebook ao Google Drive..."
            ),
            success_message=(
                "O My Notebook foi conectado ao Google Drive. "
                "Você já pode fechar esta janela."
            ),
        )

        self._salvar_token(credenciais)

        return credenciais

    def _salvar_token(
        self,
        credenciais: Credentials,
    ) -> None:
        self.paths.token_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.paths.token_path.write_text(
            credenciais.to_json(),
            encoding="utf-8",
        )