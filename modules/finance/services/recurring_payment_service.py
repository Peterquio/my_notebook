from datetime import date

from modules.finance.repositories.recurring_payment_repository import (
    RecurringPaymentRepository,
)

from modules.finance.repositories.subscription_repository import (
    SubscriptionRepository,
)

from modules.finance.repositories.monthly_bill_repository import (
    MonthlyBillRepository,
)

from modules.finance.repositories.pix_repository import (
    PixRepository,
)

from modules.finance.repositories.credit_card_expense_repository import (
    CreditCardExpenseRepository,
)

class RecurringPaymentService:
    SOURCE_PIX = "pix"
    SOURCE_CREDIT_CARD = "credit_card"

    def __init__(
            self,
            username: str,
    ) -> None:

        self.repository = (
            RecurringPaymentRepository(
                username
            )
        )

        self.subscription_repository = (
            SubscriptionRepository(
                username
            )
        )

        self.monthly_bill_repository = (
            MonthlyBillRepository(
                username
            )
        )

        self.pix_repository = (
            PixRepository(
                username
            )
        )

        self.credit_card_expense_repository = (
            CreditCardExpenseRepository(
                username
            )
        )

    # =========================================================
    # ASSINATURA + PIX
    # =========================================================

    def marcar_assinatura_paga_por_pix(
            self,
            subscription_id: int,
            pix_transaction_id: int,
            reference_year: int | None = None,
            reference_month: int | None = None,
            notes: str | None = None,
    ) -> int:

        assinatura = (
            self.subscription_repository
            .buscar_assinatura_por_id(
                subscription_id
            )
        )

        if assinatura is None:
            raise ValueError(
                "Assinatura não encontrada."
            )

        pix = (
            self.pix_repository
            .buscar_transacao_por_id(
                pix_transaction_id
            )
        )

        if pix is None:
            raise ValueError(
                "PIX não encontrado."
            )

        if pix["transaction_type"] != "sent":
            raise ValueError(
                "Uma assinatura só pode ser "
                "marcada como paga por um PIX de saída."
            )

        year, month = self._resolver_referencia(
            paid_date=pix["transaction_date"],
            reference_year=reference_year,
            reference_month=reference_month,
        )

        self._garantir_assinatura_nao_paga(
            subscription_id=subscription_id,
            reference_year=year,
            reference_month=month,
        )

        self._garantir_pix_disponivel(
            pix_transaction_id
        )

        return self.repository.criar(
            subscription_id=subscription_id,
            monthly_bill_id=None,
            reference_year=year,
            reference_month=month,
            payment_source=self.SOURCE_PIX,
            pix_transaction_id=pix_transaction_id,
            credit_card_expense_id=None,
            paid_amount_cents=int(
                pix["amount_cents"]
            ),
            paid_date=pix["transaction_date"],
            notes=self._normalizar_texto(
                notes
            ),
        )

    # =========================================================
    # ASSINATURA + CARTÃO
    # =========================================================

    def marcar_assinatura_paga_por_cartao(
            self,
            subscription_id: int,
            credit_card_expense_id: int,
            reference_year: int,
            reference_month: int,
            notes: str | None = None,
    ) -> int:

        # -----------------------------------------------------
        # ASSINATURA
        # -----------------------------------------------------

        assinatura = (
            self.subscription_repository
            .buscar_assinatura_por_id(
                subscription_id
            )
        )

        if assinatura is None:
            raise ValueError(
                "Assinatura não encontrada."
            )

        # -----------------------------------------------------
        # LANÇAMENTO EXISTENTE
        # -----------------------------------------------------

        lancamento = (
            self.credit_card_expense_repository
            .buscar_por_id(
                credit_card_expense_id
            )
        )

        if lancamento is None:
            raise ValueError(
                "Lançamento do cartão não encontrado."
            )

        # -----------------------------------------------------
        # REFERÊNCIA
        # -----------------------------------------------------

        self._validar_referencia(
            reference_year,
            reference_month,
        )

        # -----------------------------------------------------
        # GARANTE QUE A ASSINATURA AINDA NÃO FOI PAGA
        # -----------------------------------------------------

        self._garantir_assinatura_nao_paga(
            subscription_id=subscription_id,
            reference_year=reference_year,
            reference_month=reference_month,
        )

        # -----------------------------------------------------
        # GARANTE QUE O LANÇAMENTO NÃO ESTÁ VINCULADO
        # -----------------------------------------------------

        self._garantir_lancamento_cartao_disponivel(
            credit_card_expense_id
        )

        # -----------------------------------------------------
        # CRIA SOMENTE O VÍNCULO
        # -----------------------------------------------------

        return self.repository.criar(
            subscription_id=subscription_id,
            monthly_bill_id=None,

            reference_year=reference_year,
            reference_month=reference_month,

            payment_source=(
                self.SOURCE_CREDIT_CARD
            ),

            pix_transaction_id=None,

            credit_card_expense_id=(
                credit_card_expense_id
            ),

            paid_amount_cents=int(
                lancamento["effective_amount_cents"]
            ),

            paid_date=(
                lancamento["effective_purchase_date"]
            ),

            notes=self._normalizar_texto(
                notes
            ),
        )

    # =========================================================
    # CONTA DO MÊS + CARTÃO
    # =========================================================

    def marcar_conta_mes_paga_por_cartao(
            self,
            monthly_bill_id: int,
            credit_card_expense_id: int,
            reference_year: int,
            reference_month: int,
            notes: str | None = None,
    ) -> int:

        conta = (
            self.monthly_bill_repository
            .buscar_por_id(
                monthly_bill_id
            )
        )

        if conta is None:
            raise ValueError(
                "Conta do mês não encontrada."
            )

        lancamento = (
            self.credit_card_expense_repository
            .buscar_por_id(
                credit_card_expense_id
            )
        )

        if lancamento is None:
            raise ValueError(
                "Lançamento do cartão não encontrado."
            )

        self._validar_referencia(
            reference_year,
            reference_month,
        )

        self._garantir_conta_mes_nao_paga(
            monthly_bill_id=monthly_bill_id,
            reference_year=reference_year,
            reference_month=reference_month,
        )

        self._garantir_lancamento_cartao_disponivel(
            credit_card_expense_id
        )

        return self.repository.criar(
            subscription_id=None,

            monthly_bill_id=monthly_bill_id,

            reference_year=reference_year,
            reference_month=reference_month,

            payment_source=(
                self.SOURCE_CREDIT_CARD
            ),

            pix_transaction_id=None,

            credit_card_expense_id=(
                credit_card_expense_id
            ),

            paid_amount_cents=int(
                lancamento[
                    "effective_amount_cents"
                ]
            ),

            paid_date=(
                lancamento[
                    "effective_purchase_date"
                ]
            ),

            notes=self._normalizar_texto(
                notes
            ),
        )

    def buscar_pagamento_por_lancamento_cartao(
            self,
            credit_card_expense_id: int,
    ) -> dict | None:

        return (
            self.repository
            .buscar_por_lancamento_cartao(
                credit_card_expense_id
            )
        )

    # =========================================================
    # CONTA DO MÊS + PIX
    # =========================================================

    def marcar_conta_mes_paga_por_pix(
            self,
            monthly_bill_id: int,
            pix_transaction_id: int,
            reference_year: int | None = None,
            reference_month: int | None = None,
            notes: str | None = None,
    ) -> int:

        conta = (
            self.monthly_bill_repository
            .buscar_por_id(
                monthly_bill_id
            )
        )

        if conta is None:
            raise ValueError(
                "Conta do mês não encontrada."
            )

        pix = (
            self.pix_repository
            .buscar_transacao_por_id(
                pix_transaction_id
            )
        )

        if pix is None:
            raise ValueError(
                "PIX não encontrado."
            )

        if pix["transaction_type"] != "sent":
            raise ValueError(
                "Uma conta do mês só pode ser "
                "marcada como paga por um PIX de saída."
            )

        year, month = self._resolver_referencia(
            paid_date=pix["transaction_date"],
            reference_year=reference_year,
            reference_month=reference_month,
        )

        self._garantir_conta_mes_nao_paga(
            monthly_bill_id=monthly_bill_id,
            reference_year=year,
            reference_month=month,
        )

        self._garantir_pix_disponivel(
            pix_transaction_id
        )

        return self.repository.criar(
            subscription_id=None,
            monthly_bill_id=monthly_bill_id,
            reference_year=year,
            reference_month=month,
            payment_source=self.SOURCE_PIX,
            pix_transaction_id=pix_transaction_id,
            credit_card_expense_id=None,
            paid_amount_cents=int(
                pix["amount_cents"]
            ),
            paid_date=pix["transaction_date"],
            notes=self._normalizar_texto(
                notes
            ),
        )

    # =========================================================
    # CONSULTA
    # =========================================================

    def buscar_pagamento_assinatura_mes(
            self,
            subscription_id: int,
            reference_year: int,
            reference_month: int,
    ) -> dict | None:

        return (
            self.repository
            .buscar_assinatura_mes(
                subscription_id=subscription_id,
                reference_year=reference_year,
                reference_month=reference_month,
            )
        )

    def buscar_pagamento_conta_mes(
            self,
            monthly_bill_id: int,
            reference_year: int,
            reference_month: int,
    ) -> dict | None:

        return (
            self.repository
            .buscar_conta_mes(
                monthly_bill_id=monthly_bill_id,
                reference_year=reference_year,
                reference_month=reference_month,
            )
        )

    def assinatura_foi_paga(
            self,
            subscription_id: int,
            reference_year: int,
            reference_month: int,
    ) -> bool:

        return (
            self.buscar_pagamento_assinatura_mes(
                subscription_id=subscription_id,
                reference_year=reference_year,
                reference_month=reference_month,
            )
            is not None
        )

    def conta_mes_foi_paga(
            self,
            monthly_bill_id: int,
            reference_year: int,
            reference_month: int,
    ) -> bool:

        return (
            self.buscar_pagamento_conta_mes(
                monthly_bill_id=monthly_bill_id,
                reference_year=reference_year,
                reference_month=reference_month,
            )
            is not None
        )

    def listar_pagamentos_mes(
            self,
            reference_year: int,
            reference_month: int,
    ) -> list[dict]:

        self._validar_referencia(
            reference_year,
            reference_month,
        )

        return self.repository.listar_mes(
            reference_year=reference_year,
            reference_month=reference_month,
        )

    # =========================================================
    # DESVINCULAR
    # =========================================================

    def desvincular_pix(
            self,
            pix_transaction_id: int,
    ) -> None:

        self.repository.excluir_por_pix(
            pix_transaction_id
        )

    def desvincular_lancamento_cartao(
            self,
            credit_card_expense_id: int,
    ) -> None:

        self.repository.excluir_por_lancamento_cartao(
            credit_card_expense_id
        )

    def desvincular_pagamento_assinatura(
            self,
            subscription_id: int,
            reference_year: int,
            reference_month: int,
    ) -> None:

        pagamento = (
            self.repository
            .buscar_assinatura_mes(
                subscription_id=subscription_id,
                reference_year=reference_year,
                reference_month=reference_month,
            )
        )

        if pagamento is None:
            raise ValueError(
                "Esta assinatura não possui pagamento "
                "vinculado neste mês."
            )

        self.repository.excluir(
            pagamento["id"]
        )

    # =========================================================
    # VALIDAÇÕES
    # =========================================================

    def _garantir_assinatura_nao_paga(
            self,
            subscription_id: int,
            reference_year: int,
            reference_month: int,
    ) -> None:

        pagamento = (
            self.repository
            .buscar_assinatura_mes(
                subscription_id=subscription_id,
                reference_year=reference_year,
                reference_month=reference_month,
            )
        )

        if pagamento is not None:
            raise ValueError(
                "Esta assinatura já está marcada "
                "como paga neste mês."
            )

    def _garantir_conta_mes_nao_paga(
            self,
            monthly_bill_id: int,
            reference_year: int,
            reference_month: int,
    ) -> None:

        pagamento = (
            self.repository
            .buscar_conta_mes(
                monthly_bill_id=monthly_bill_id,
                reference_year=reference_year,
                reference_month=reference_month,
            )
        )

        if pagamento is not None:
            raise ValueError(
                "Esta conta já está marcada "
                "como paga neste mês."
            )

    def _garantir_pix_disponivel(
            self,
            pix_transaction_id: int,
    ) -> None:

        pagamento = (
            self.repository
            .buscar_por_pix(
                pix_transaction_id
            )
        )

        if pagamento is not None:
            raise ValueError(
                "Este PIX já está vinculado "
                "a outra conta ou assinatura."
            )

    def _garantir_lancamento_cartao_disponivel(
            self,
            credit_card_expense_id: int,
    ) -> None:

        pagamento = (
            self.repository
            .buscar_por_lancamento_cartao(
                credit_card_expense_id
            )
        )

        if pagamento is not None:
            raise ValueError(
                "Este lançamento do cartão já está "
                "vinculado a outra conta ou assinatura."
            )

    def _resolver_referencia(
            self,
            paid_date: str,
            reference_year: int | None,
            reference_month: int | None,
    ) -> tuple[int, int]:

        data_pagamento = date.fromisoformat(
            paid_date
        )

        year = (
            reference_year
            if reference_year is not None
            else data_pagamento.year
        )

        month = (
            reference_month
            if reference_month is not None
            else data_pagamento.month
        )

        self._validar_referencia(
            year,
            month,
        )

        return year, month

    def _validar_referencia(
            self,
            reference_year: int,
            reference_month: int,
    ) -> None:

        if reference_year < 2000:
            raise ValueError(
                "Ano de referência inválido."
            )

        if not 1 <= reference_month <= 12:
            raise ValueError(
                "Mês de referência inválido."
            )

    def _normalizar_texto(
            self,
            value: str | None,
    ) -> str | None:

        if value is None:
            return None

        value = value.strip()

        return value or None