import sqlite3
from pathlib import Path


class SQLiteBackup:
    @staticmethod
    def criar(
        source_path: Path,
        destination_path: Path,
    ) -> Path:
        if not source_path.exists():
            raise FileNotFoundError(
                "Banco SQLite não encontrado em: "
                f"{source_path}"
            )

        destination_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        if destination_path.exists():
            destination_path.unlink()

        source_connection = sqlite3.connect(
            str(source_path),
            timeout=30,
        )

        destination_connection = sqlite3.connect(
            str(destination_path),
            timeout=30,
        )

        try:
            source_connection.backup(
                destination_connection,
                pages=100,
                sleep=0.05,
            )

            destination_connection.commit()

        finally:
            destination_connection.close()
            source_connection.close()

        SQLiteBackup.validar(destination_path)

        return destination_path

    @staticmethod
    def validar(
        database_path: Path,
    ) -> None:
        if not database_path.exists():
            raise FileNotFoundError(
                f"Backup não encontrado: {database_path}"
            )

        connection = sqlite3.connect(
            str(database_path),
            timeout=30,
        )

        try:
            resultado = connection.execute(
                "PRAGMA quick_check;"
            ).fetchone()

        finally:
            connection.close()

        if not resultado or resultado[0] != "ok":
            detalhe = (
                resultado[0]
                if resultado
                else "sem resultado"
            )

            raise RuntimeError(
                "O arquivo SQLite não passou pela "
                f"verificação de integridade: {detalhe}"
            )