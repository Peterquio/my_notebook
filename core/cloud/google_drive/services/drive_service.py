from datetime import datetime
from pathlib import Path
from typing import Any

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import Resource, build
from googleapiclient.http import MediaFileUpload

from core.cloud.google_drive.models.backup_info import BackupInfo


class GoogleDriveService:
    BACKUP_APP_PROPERTY = "my_notebook_database_backup"

    def __init__(
        self,
        credentials: Credentials,
    ) -> None:
        self._service: Resource = build(
            "drive",
            "v3",
            credentials=credentials,
            cache_discovery=False,
        )

    def buscar_backup(
        self,
        file_name: str,
    ) -> BackupInfo | None:
        nome_seguro = file_name.replace("'", "\\'")

        query = (
            f"name = '{nome_seguro}' "
            "and trashed = false "
            f"and appProperties has "
            f"{{ key='backup_type' and "
            f"value='{self.BACKUP_APP_PROPERTY}' }}"
        )

        resposta = (
            self._service.files()
            .list(
                q=query,
                spaces="drive",
                pageSize=10,
                fields=(
                    "files("
                    "id,"
                    "name,"
                    "size,"
                    "modifiedTime,"
                    "md5Checksum"
                    ")"
                ),
            )
            .execute()
        )

        arquivos = resposta.get("files", [])

        if not arquivos:
            return None

        arquivos.sort(
            key=lambda item: item.get(
                "modifiedTime",
                "",
            ),
            reverse=True,
        )

        return self._converter_backup_info(
            arquivos[0],
        )

    def obter_backup_por_id(
        self,
        file_id: str,
    ) -> BackupInfo:
        arquivo = (
            self._service.files()
            .get(
                fileId=file_id,
                fields=(
                    "id,"
                    "name,"
                    "size,"
                    "modifiedTime,"
                    "md5Checksum"
                ),
            )
            .execute()
        )

        return self._converter_backup_info(arquivo)

    def criar_backup(
        self,
        local_path: Path,
        remote_name: str,
    ) -> BackupInfo:
        self._validar_arquivo_local(local_path)

        metadata = {
            "name": remote_name,
            "appProperties": {
                "backup_type": self.BACKUP_APP_PROPERTY,
            },
        }

        media = MediaFileUpload(
            str(local_path),
            mimetype="application/x-sqlite3",
            resumable=True,
        )

        arquivo = (
            self._service.files()
            .create(
                body=metadata,
                media_body=media,
                fields=(
                    "id,"
                    "name,"
                    "size,"
                    "modifiedTime,"
                    "md5Checksum"
                ),
            )
            .execute()
        )

        return self._converter_backup_info(arquivo)

    def atualizar_backup(
        self,
        file_id: str,
        local_path: Path,
        remote_name: str | None = None,
    ) -> BackupInfo:
        self._validar_arquivo_local(local_path)

        metadata: dict[str, Any] = {
            "appProperties": {
                "backup_type": self.BACKUP_APP_PROPERTY,
            },
        }

        if remote_name:
            metadata["name"] = remote_name

        media = MediaFileUpload(
            str(local_path),
            mimetype="application/x-sqlite3",
            resumable=True,
        )

        arquivo = (
            self._service.files()
            .update(
                fileId=file_id,
                body=metadata,
                media_body=media,
                fields=(
                    "id,"
                    "name,"
                    "size,"
                    "modifiedTime,"
                    "md5Checksum"
                ),
            )
            .execute()
        )

        return self._converter_backup_info(arquivo)

    def criar_ou_atualizar_backup(
        self,
        local_path: Path,
        remote_name: str,
    ) -> BackupInfo:
        backup_existente = self.buscar_backup(
            remote_name,
        )

        if backup_existente:
            return self.atualizar_backup(
                file_id=backup_existente.file_id,
                local_path=local_path,
                remote_name=remote_name,
            )

        return self.criar_backup(
            local_path=local_path,
            remote_name=remote_name,
        )

    def criar_requisicao_download(
        self,
        file_id: str,
    ):
        return (
            self._service.files()
            .get_media(fileId=file_id)
        )

    def excluir_backup(
        self,
        file_id: str,
    ) -> None:
        (
            self._service.files()
            .delete(fileId=file_id)
            .execute()
        )

    @staticmethod
    def _validar_arquivo_local(
        local_path: Path,
    ) -> None:
        if not local_path.exists():
            raise FileNotFoundError(
                f"Arquivo não encontrado: {local_path}"
            )

        if not local_path.is_file():
            raise ValueError(
                f"O caminho não é um arquivo: {local_path}"
            )

    @staticmethod
    def _converter_backup_info(
        arquivo: dict,
    ) -> BackupInfo:
        modified_at = None
        modified_raw = arquivo.get("modifiedTime")

        if modified_raw:
            modified_at = datetime.fromisoformat(
                modified_raw.replace(
                    "Z",
                    "+00:00",
                )
            )

        return BackupInfo(
            file_id=str(arquivo["id"]),
            file_name=str(arquivo["name"]),
            size_bytes=int(
                arquivo.get("size") or 0
            ),
            modified_at=modified_at,
            md5_checksum=arquivo.get(
                "md5Checksum"
            ),
        )