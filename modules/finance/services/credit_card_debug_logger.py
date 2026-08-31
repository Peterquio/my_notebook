from __future__ import annotations

from datetime import datetime
from pathlib import Path
from pprint import pformat
from typing import Any


class CreditCardDebugLogger:
    """
    Logger do diagnóstico de cartões.

    Mantém o conteúdo em memória para exibição na interface
    e simultaneamente persiste cada entrada em arquivo.
    """

    def __init__(
            self,
            username: str,
    ) -> None:

        self.username = username

        self._entries: list[str] = []

        self._log_path = (
            self._criar_arquivo_log()
        )

        self._append(
            "INÍCIO DA SESSÃO",
            (
                f"Usuário: {self.username}\n"
                f"Arquivo: {self._log_path}"
            ),
        )

    # ============================================================
    # ARQUIVO
    # ============================================================

    def _criar_arquivo_log(self) -> Path:

        # credit_card_debug_logger.py
        # modules/finance/services/
        #
        # parents:
        # 0 -> services
        # 1 -> finance
        # 2 -> modules
        # 3 -> raiz do projeto

        project_root = (
            Path(__file__)
            .resolve()
            .parents[3]
        )

        logs_dir = (
            project_root
            / "user_data"
            / "logs"
        )

        logs_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        agora = datetime.now()

        nome_base = (
            f"{self.username}_"
            f"{agora:%y%m%d_%H-%M}"
        )

        caminho = (
            logs_dir
            / f"{nome_base}.txt"
        )

        # --------------------------------------------------------
        # EVITAR SOBRESCREVER SE ABRIR 2X NO MESMO MINUTO
        # --------------------------------------------------------

        contador = 2

        while caminho.exists():
            caminho = (
                logs_dir
                / (
                    f"{nome_base}_"
                    f"{contador}.txt"
                )
            )

            contador += 1

        caminho.touch()

        return caminho

    def _salvar_bloco(
            self,
            bloco: str,
    ) -> None:

        with self._log_path.open(
                "a",
                encoding="utf-8",
        ) as arquivo:

            arquivo.write(
                bloco
            )

            arquivo.write(
                "\n"
            )

            arquivo.flush()

    def obter_caminho_log(self) -> Path:
        return self._log_path

    # ============================================================
    # BASE
    # ============================================================

    def _timestamp(self) -> str:
        return datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S.%f"
        )[:-3]

    def _append(
            self,
            titulo: str,
            conteudo: str | None = None,
    ) -> None:

        bloco = [
            "",
            "=" * 80,
            f"[{self._timestamp()}] {titulo}",
            "=" * 80,
        ]

        if conteudo:
            bloco.append(
                conteudo
            )

        texto = "\n".join(
            bloco
        )

        # memória
        self._entries.append(
            texto
        )

        # disco
        self._salvar_bloco(
            texto
        )

    # ============================================================
    # LOG GENÉRICO
    # ============================================================

    def info(
            self,
            mensagem: str,
    ) -> None:

        self._append(
            "INFO",
            mensagem,
        )

    def warning(
            self,
            mensagem: str,
    ) -> None:

        self._append(
            "WARNING",
            mensagem,
        )

    def error(
            self,
            mensagem: str,
    ) -> None:

        self._append(
            "ERROR",
            mensagem,
        )

    # ============================================================
    # DADOS
    # ============================================================

    def dados(
            self,
            titulo: str,
            dados: Any,
    ) -> None:

        self._append(
            titulo,
            pformat(
                dados,
                width=120,
                sort_dicts=False,
            ),
        )

    # ============================================================
    # AUDITORIA
    # ============================================================

    def inicio_auditoria(
            self,
            tipo: str,
            identificador: str,
    ) -> None:

        self._append(
            "INÍCIO DE AUDITORIA",
            (
                f"Tipo: {tipo}\n"
                f"Identificador: {identificador}"
            ),
        )

    def fim_auditoria(
            self,
            tipo: str,
            identificador: str,
            problemas_encontrados: int,
    ) -> None:

        self._append(
            "FIM DE AUDITORIA",
            (
                f"Tipo: {tipo}\n"
                f"Identificador: {identificador}\n"
                f"Problemas encontrados: "
                f"{problemas_encontrados}"
            ),
        )

    # ============================================================
    # ALTERAÇÕES
    # ============================================================

    def alteracao(
            self,
            acao: str,
            entidade: str,
            identificador: Any,
            antes: Any,
            depois: Any,
    ) -> None:

        conteudo = (
            f"Ação: {acao}\n"
            f"Entidade: {entidade}\n"
            f"ID: {identificador}\n"
            "\n"
            "ANTES\n"
            + "-" * 80
            + "\n"
            + pformat(
                antes,
                width=120,
                sort_dicts=False,
            )
            + "\n\n"
            "DEPOIS\n"
            + "-" * 80
            + "\n"
            + pformat(
                depois,
                width=120,
                sort_dicts=False,
            )
        )

        self._append(
            "ALTERAÇÃO MANUAL",
            conteudo,
        )

    def exclusao(
            self,
            entidade: str,
            identificador: Any,
            registro: Any,
    ) -> None:

        conteudo = (
            f"Entidade: {entidade}\n"
            f"ID: {identificador}\n"
            "\n"
            "REGISTRO ANTES DA EXCLUSÃO\n"
            + "-" * 80
            + "\n"
            + pformat(
                registro,
                width=120,
                sort_dicts=False,
            )
        )

        self._append(
            "EXCLUSÃO",
            conteudo,
        )

    # ============================================================
    # PROBLEMAS
    # ============================================================

    def problema(
            self,
            codigo: str,
            descricao: str,
            dados: Any | None = None,
    ) -> None:

        conteudo = (
            f"Código: {codigo}\n"
            f"Descrição: {descricao}"
        )

        if dados is not None:
            conteudo += (
                "\n\n"
                "DADOS\n"
                + "-" * 80
                + "\n"
                + pformat(
                    dados,
                    width=120,
                    sort_dicts=False,
                )
            )

        self._append(
            "PROBLEMA DETECTADO",
            conteudo,
        )

    # ============================================================
    # SAÍDA
    # ============================================================

    def obter_texto(self) -> str:

        if not self._entries:
            return ""

        return "\n".join(
            self._entries
        ).strip()

    def limpar(self) -> None:

        self._entries.clear()

        # Limpar significa iniciar um log limpo,
        # mas não apagar o arquivo histórico anterior.

        self._log_path = (
            self._criar_arquivo_log()
        )

        self._append(
            "LOG REINICIADO",
            (
                f"Usuário: {self.username}\n"
                f"Arquivo: {self._log_path}"
            ),
        )

    def quantidade_entries(self) -> int:
        return len(
            self._entries
        )