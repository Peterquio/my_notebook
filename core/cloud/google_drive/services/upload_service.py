from pathlib import Path

from core.cloud.google_drive.models.backup_info import BackupInfo
from core.cloud.google_drive.services.drive_service import (
    GoogleDriveService,
)


class GoogleDriveUploadService:
    def __init__(
        self,
        drive_service: GoogleDriveService,
    ) -> None:
        self.drive_service = drive_service

    def enviar_backup(
        self,
        local_path: Path,
        remote_name: str,
    ) -> BackupInfo:
        return self.drive_service.criar_ou_atualizar_backup(
            local_path=local_path,
            remote_name=remote_name,
        )