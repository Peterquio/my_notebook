from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


SCOPES = [
    "https://www.googleapis.com/auth/drive.file",
]

BASE_DIR = Path(__file__).resolve().parent

CREDENTIALS_PATH = (
    BASE_DIR
    / "core"
    / "config"
    / "google"
    / "credentials.json"
)

TOKEN_PATH = (
    BASE_DIR
    / "core"
    / "config"
    / "google"
    / "token.json"
)


def autenticar_google_drive() -> Credentials:
    credenciais = None

    if TOKEN_PATH.exists():
        credenciais = Credentials.from_authorized_user_file(
            str(TOKEN_PATH),
            SCOPES,
        )

    if not credenciais or not credenciais.valid:
        if (
            credenciais
            and credenciais.expired
            and credenciais.refresh_token
        ):
            credenciais.refresh(Request())

        else:
            if not CREDENTIALS_PATH.exists():
                raise FileNotFoundError(
                    "credentials.json não encontrado em: "
                    f"{CREDENTIALS_PATH}"
                )

            fluxo = InstalledAppFlow.from_client_secrets_file(
                str(CREDENTIALS_PATH),
                SCOPES,
            )

            credenciais = fluxo.run_local_server(
                port=0,
                open_browser=True,
            )

        TOKEN_PATH.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        TOKEN_PATH.write_text(
            credenciais.to_json(),
            encoding="utf-8",
        )

    return credenciais


def main() -> None:
    credenciais = autenticar_google_drive()

    drive = build(
        "drive",
        "v3",
        credentials=credenciais,
    )

    resultado = drive.files().list(
        pageSize=10,
        fields="files(id, name, mimeType)",
    ).execute()

    arquivos = resultado.get("files", [])

    print("\nAutenticação concluída com sucesso!")

    if not arquivos:
        print(
            "Nenhum arquivo criado ou autorizado "
            "pelo My Notebook foi encontrado."
        )
        return

    print("\nArquivos acessíveis ao My Notebook:")

    for arquivo in arquivos:
        print(
            f"- {arquivo['name']} "
            f"({arquivo['id']})"
        )


if __name__ == "__main__":
    main()