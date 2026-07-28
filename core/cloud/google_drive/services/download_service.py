from pathlib import Path

from googleapiclient.http import MediaIoBaseDownload

from core.cloud.google_drive.services.drive_service import (
    GoogleDriveService,
)


class GoogleDriveDownloadService:
    def __init__(
        self,
        drive_service: GoogleDriveService,
    ) -> None:
        self.drive_service = drive_service

    def baixar_backup(
        self,
        file_id: str,
        destination_path: Path,
    ) -> Path:
        destination_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        temporary_path = destination_path.with_suffix(
            destination_path.suffix + ".download"
        )

        if temporary_path.exists():
            temporary_path.unlink()

        request = (
            self.drive_service
            .criar_requisicao_download(file_id)
        )

        try:
            with temporary_path.open("wb") as file_handle:
                downloader = MediaIoBaseDownload(
                    file_handle,
                    request,
                    chunksize=1024 * 1024,
                )

                concluido = False

                while not concluido:
                    _, concluido = (
                        downloader.next_chunk()
                    )

            temporary_path.replace(
                destination_path
            )

        except Exception:
            if temporary_path.exists():
                temporary_path.unlink()

            raise

        return destination_path