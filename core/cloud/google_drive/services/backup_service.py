import os
import shutil
import tempfile
from pathlib import Path

from core.cloud.google_drive.auth.google_auth_service import (
    GoogleAuthService,
)
from core.cloud.google_drive.models.backup_info import BackupInfo
from core.cloud.google_drive.services.download_service import (
    GoogleDriveDownloadService,
)
from core.cloud.google_drive.services.drive_service import (
    GoogleDriveService,
)
from core.cloud.google_drive.services.upload_service import (
    GoogleDriveUploadService,
)
from core.cloud.google_drive.utils.sqlite_backup import (
    SQLiteBackup,
)


class GoogleDriveBackupService:
    DEFAULT_REMOTE_NAME = "my_notebook_backup.db"

    def __init__(
        self,
        auth_service: GoogleAuthService | None = None,
    ) -> None:
        self.auth_service = (
            auth_service
            or GoogleAuthService()
        )

    def fazer_backup(
        self,
        database_path: Path,
        remote_name: str | None = None,
    ) -> BackupInfo:
        database_path = Path(database_path)

        credentials = (
            self.auth_service.autenticar()
        )

        drive_service = GoogleDriveService(
            credentials
        )

        upload_service = GoogleDriveUploadService(
            drive_service
        )

        nome_remoto = (
            remote_name
            or self.DEFAULT_REMOTE_NAME
        )

        with tempfile.TemporaryDirectory(
            prefix="my_notebook_backup_"
        ) as temporary_directory:
            backup_path = (
                Path(temporary_directory)
                / nome_remoto
            )

            SQLiteBackup.criar(
                source_path=database_path,
                destination_path=backup_path,
            )

            return upload_service.enviar_backup(
                local_path=backup_path,
                remote_name=nome_remoto,
            )

    def buscar_backup(
        self,
        remote_name: str | None = None,
    ) -> BackupInfo | None:
        credentials = (
            self.auth_service.autenticar()
        )

        drive_service = GoogleDriveService(
            credentials
        )

        return drive_service.buscar_backup(
            remote_name
            or self.DEFAULT_REMOTE_NAME
        )

    def baixar_para_restauracao(
        self,
        destination_path: Path,
        remote_name: str | None = None,
    ) -> Path:
        credentials = (
            self.auth_service.autenticar()
        )

        drive_service = GoogleDriveService(
            credentials
        )

        nome_remoto = (
            remote_name
            or self.DEFAULT_REMOTE_NAME
        )

        backup_info = drive_service.buscar_backup(
            nome_remoto
        )

        if not backup_info:
            raise FileNotFoundError(
                "Nenhum backup do My Notebook "
                "foi encontrado no Google Drive."
            )

        download_service = (
            GoogleDriveDownloadService(
                drive_service
            )
        )

        destination_path = Path(
            destination_path
        )

        downloaded_path = (
            download_service.baixar_backup(
                file_id=backup_info.file_id,
                destination_path=destination_path,
            )
        )

        SQLiteBackup.validar(downloaded_path)

        return downloaded_path

    def restaurar_banco(
        self,
        database_path: Path,
        remote_name: str | None = None,
    ) -> Path:
        database_path = Path(database_path)

        restore_path = database_path.with_suffix(
            database_path.suffix + ".restore"
        )

        self.baixar_para_restauracao(
            destination_path=restore_path,
            remote_name=remote_name,
        )

        current_backup_path = (
            database_path.with_suffix(
                database_path.suffix + ".before_restore"
            )
        )

        if current_backup_path.exists():
            current_backup_path.unlink()

        try:
            if database_path.exists():
                shutil.copy2(
                    database_path,
                    current_backup_path,
                )

            os.replace(
                restore_path,
                database_path,
            )

            SQLiteBackup.validar(database_path)

        except Exception:
            if restore_path.exists():
                restore_path.unlink()

            if current_backup_path.exists():
                shutil.copy2(
                    current_backup_path,
                    database_path,
                )

            raise

        return database_path