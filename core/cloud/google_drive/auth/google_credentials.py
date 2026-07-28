from dataclasses import dataclass
from pathlib import Path


GOOGLE_DRIVE_SCOPES = [
    "https://www.googleapis.com/auth/drive.file",
]


@dataclass(frozen=True)
class GoogleCredentialsPaths:
    credentials_path: Path
    token_path: Path


def obter_caminhos_google() -> GoogleCredentialsPaths:
    project_root = Path(__file__).resolve().parents[4]

    google_config_dir = (
        project_root
        / "core"
        / "config"
        / "google"
    )

    return GoogleCredentialsPaths(
        credentials_path=google_config_dir / "credentials.json",
        token_path=google_config_dir / "token.json",
    )