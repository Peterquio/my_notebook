from pathlib import Path

from core.cloud.google_drive.services.backup_service import (
    GoogleDriveBackupService,
)


PROJECT_ROOT = Path(__file__).resolve().parent

DATABASE_PATH = (
    PROJECT_ROOT
    / "user_data"
    / "users"
    / "default.db"
)


def main() -> None:
    service = GoogleDriveBackupService()

    resultado = service.fazer_backup(
        database_path=DATABASE_PATH,
    )

    print()
    print("Backup enviado com sucesso!")
    print(f"Nome: {resultado.file_name}")
    print(f"ID: {resultado.file_id}")
    print(f"Tamanho: {resultado.size_mb:.2f} MB")
    print(f"Modificado em: {resultado.modified_at}")


if __name__ == "__main__":
    main()