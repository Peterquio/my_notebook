from modules.finance.repositories.balance_repository import (
    BalanceRepository,
)


class PixBalanceSyncService:
    def __init__(
            self,
            username: str,
    ) -> None:

        self.repository = BalanceRepository(
            username
        )

    # =========================================================
    # SINCRONIZAÇÃO
    # =========================================================

    def sincronizar(
            self,
            pix: dict,
    ) -> None:

        pix_id = pix["id"]

        external_reference = (
            f"pix:{pix_id}"
        )

        transaction_type = (
            pix["transaction_type"]
        )

        if transaction_type == "received":
            self._sincronizar_recebido(
                pix=pix,
                external_reference=external_reference,
            )
            return

        if transaction_type == "sent":
            self._sincronizar_enviado(
                pix=pix,
                external_reference=external_reference,
            )
            return

        raise ValueError(
            "Tipo de PIX inválido."
        )

    # =========================================================
    # PIX RECEBIDO
    # =========================================================

    def _sincronizar_recebido(
            self,
            pix: dict,
            external_reference: str,
    ) -> None:

        # Se esse PIX anteriormente era enviado,
        # remove o compromisso correspondente.

        compromisso = (
            self.repository
            .buscar_compromisso_por_external_reference(
                external_reference
            )
        )

        if compromisso is not None:
            self.repository.excluir_compromisso(
                compromisso["id"]
            )

        receita = (
            self.repository
            .buscar_receita_por_external_reference(
                external_reference
            )
        )

        descricao = self._montar_descricao(
            pix
        )

        if receita is None:

            receita_id = (
                self.repository.criar_receita(
                    account_id=pix["account_id"],
                    description=descricao,
                    expected_amount_cents=pix["amount_cents"],
                    expected_date=pix["transaction_date"],
                    is_recurring=False,
                    notes=pix.get("notes"),
                    external_reference=external_reference,
                )
            )

        else:

            receita_id = receita["id"]

            self.repository.atualizar_receita(
                receita_id=receita_id,
                account_id=pix["account_id"],
                description=descricao,
                expected_amount_cents=pix["amount_cents"],
                expected_date=pix["transaction_date"],
                is_recurring=False,
                notes=pix.get("notes"),
            )

        # PIX recebido já aconteceu.
        # Portanto não é receita prevista.

        self.repository.confirmar_receita(
            receita_id=receita_id,
            valor_real_cents=pix["amount_cents"],
            received_date=pix["transaction_date"],
        )

    # =========================================================
    # PIX ENVIADO
    # =========================================================

    def _sincronizar_enviado(
            self,
            pix: dict,
            external_reference: str,
    ) -> None:

        # Se esse PIX anteriormente era recebido,
        # remove a receita correspondente.

        receita = (
            self.repository
            .buscar_receita_por_external_reference(
                external_reference
            )
        )

        if receita is not None:
            self.repository.excluir_receita(
                receita["id"]
            )

        compromisso = (
            self.repository
            .buscar_compromisso_por_external_reference(
                external_reference
            )
        )

        descricao = self._montar_descricao(
            pix
        )

        if compromisso is None:

            self.repository.criar_compromisso(
                account_id=pix["account_id"],
                description=descricao,
                expected_amount_cents=pix["amount_cents"],
                actual_amount_cents=pix["amount_cents"],
                due_date=pix["transaction_date"],
                paid_date=pix["transaction_date"],
                payment_type="bank_account",
                credit_card_id=None,
                is_recurring=False,
                notes=pix.get("notes"),
                external_reference=external_reference,
                status="paid",
                commitment_origin="pix",
                projection_type="real",
            )

            return

        self.repository.atualizar_compromisso(
            compromisso_id=compromisso["id"],
            account_id=pix["account_id"],
            description=descricao,
            expected_amount_cents=pix["amount_cents"],
            actual_amount_cents=pix["amount_cents"],
            due_date=pix["transaction_date"],
            paid_date=pix["transaction_date"],
            payment_type="bank_account",
            credit_card_id=None,
            is_recurring=False,
            notes=pix.get("notes"),
            external_reference=external_reference,
            status="paid",
            commitment_origin="pix",
            projection_type="real",
        )

    # =========================================================
    # EXCLUSÃO
    # =========================================================

    def remover(
            self,
            pix_id: int,
    ) -> None:

        external_reference = (
            f"pix:{pix_id}"
        )

        receita = (
            self.repository
            .buscar_receita_por_external_reference(
                external_reference
            )
        )

        if receita is not None:
            self.repository.excluir_receita(
                receita["id"]
            )

        compromisso = (
            self.repository
            .buscar_compromisso_por_external_reference(
                external_reference
            )
        )

        if compromisso is not None:
            self.repository.excluir_compromisso(
                compromisso["id"]
            )

    # =========================================================
    # DESCRIÇÃO
    # =========================================================

    def _montar_descricao(
            self,
            pix: dict,
    ) -> str:

        nome = (
            pix.get("contact_name")
            or pix.get("description")
        )

        if nome:
            return f"PIX - {nome}"

        return "PIX"