from modules.finance.repositories.monthly_bill_repository import (
    MonthlyBillRepository,
)


class MonthlyBillService:
    VALID_PAYMENT_METHODS = {
        "pix",
        "credit_card",
        "bank_account",
    }

    def __init__(
            self,
            username: str,
    ) -> None:

        self.repository = (
            MonthlyBillRepository(
                username
            )
        )

    # =========================================================
    # CRIAR
    # =========================================================

    def criar(
            self,
            name: str,
            estimated_amount_cents: int,
            due_day: int,
            preferred_payment_method: str | None = None,
            account_id: int | None = None,
            credit_card_id: int | None = None,
            category_id: int | None = None,
            description: str | None = None,
            start_date: str | None = None,
            end_date: str | None = None,
            notes: str | None = None,
    ) -> int:

        name = self._validar_nome(
            name
        )

        estimated_amount_cents = (
            self._validar_valor(
                estimated_amount_cents
            )
        )

        due_day = self._validar_dia(
            due_day
        )

        preferred_payment_method = (
            self._validar_metodo(
                preferred_payment_method
            )
        )

        return self.repository.criar(
            name=name,
            estimated_amount_cents=(
                estimated_amount_cents
            ),
            due_day=due_day,
            preferred_payment_method=(
                preferred_payment_method
            ),
            account_id=account_id,
            credit_card_id=credit_card_id,
            category_id=category_id,
            description=self._texto(
                description
            ),
            start_date=start_date,
            end_date=end_date,
            notes=self._texto(
                notes
            ),
        )

    # =========================================================
    # ATUALIZAR
    # =========================================================

    def atualizar(
            self,
            monthly_bill_id: int,
            **dados,
    ) -> None:

        if (
            self.repository
            .buscar_por_id(monthly_bill_id)
            is None
        ):
            raise ValueError(
                "Conta do mês não encontrada."
            )

        name = self._validar_nome(
            dados["name"]
        )

        valor = self._validar_valor(
            dados["estimated_amount_cents"]
        )

        due_day = self._validar_dia(
            dados["due_day"]
        )

        metodo = self._validar_metodo(
            dados.get(
                "preferred_payment_method"
            )
        )

        self.repository.atualizar(
            monthly_bill_id=monthly_bill_id,
            name=name,
            estimated_amount_cents=valor,
            due_day=due_day,
            preferred_payment_method=metodo,
            account_id=dados.get(
                "account_id"
            ),
            credit_card_id=dados.get(
                "credit_card_id"
            ),
            category_id=dados.get(
                "category_id"
            ),
            description=self._texto(
                dados.get("description")
            ),
            start_date=dados.get(
                "start_date"
            ),
            end_date=dados.get(
                "end_date"
            ),
            notes=self._texto(
                dados.get("notes")
            ),
        )

    # =========================================================
    # CONSULTA
    # =========================================================

    def listar(
            self,
            include_inactive: bool = False,
    ) -> list[dict]:

        return self.repository.listar(
            include_inactive=include_inactive
        )

    def listar_ativas(
            self,
    ) -> list[dict]:

        return self.repository.listar(
            include_inactive=False
        )

    def buscar_por_id(
            self,
            monthly_bill_id: int,
    ) -> dict | None:

        return self.repository.buscar_por_id(
            monthly_bill_id
        )

    # =========================================================
    # STATUS
    # =========================================================

    def desativar(
            self,
            monthly_bill_id: int,
    ) -> None:

        self._garantir_existe(
            monthly_bill_id
        )

        self.repository.desativar(
            monthly_bill_id
        )

    def reativar(
            self,
            monthly_bill_id: int,
    ) -> None:

        self._garantir_existe(
            monthly_bill_id
        )

        self.repository.reativar(
            monthly_bill_id
        )

    def arquivar(
            self,
            monthly_bill_id: int,
            archive_reason: str | None = None,
    ) -> None:

        self._garantir_existe(
            monthly_bill_id
        )

        self.repository.arquivar(
            monthly_bill_id=monthly_bill_id,
            archive_reason=self._texto(
                archive_reason
            ),
        )

    # =========================================================
    # VALIDAÇÕES
    # =========================================================

    def _garantir_existe(
            self,
            monthly_bill_id: int,
    ) -> None:

        if (
            self.repository
            .buscar_por_id(monthly_bill_id)
            is None
        ):
            raise ValueError(
                "Conta do mês não encontrada."
            )

    def _validar_nome(
            self,
            name: str,
    ) -> str:

        name = (
            name
            or ""
        ).strip()

        if not name:
            raise ValueError(
                "Informe o nome da conta."
            )

        return name

    def _validar_valor(
            self,
            value: int,
    ) -> int:

        try:
            value = int(value)
        except (TypeError, ValueError):
            raise ValueError(
                "Valor médio inválido."
            )

        if value < 0:
            raise ValueError(
                "O valor médio não pode "
                "ser negativo."
            )

        return value

    def _validar_dia(
            self,
            due_day: int,
    ) -> int:

        try:
            due_day = int(
                due_day
            )
        except (TypeError, ValueError):
            raise ValueError(
                "Dia de vencimento inválido."
            )

        if not 1 <= due_day <= 31:
            raise ValueError(
                "O dia de vencimento deve "
                "estar entre 1 e 31."
            )

        return due_day

    def _validar_metodo(
            self,
            metodo: str | None,
    ) -> str | None:

        if metodo is None:
            return None

        metodo = (
            metodo
            .strip()
            .lower()
        )

        if not metodo:
            return None

        if (
            metodo
            not in self.VALID_PAYMENT_METHODS
        ):
            raise ValueError(
                "Forma de pagamento inválida."
            )

        return metodo

    def _texto(
            self,
            value: str | None,
    ) -> str | None:

        if value is None:
            return None

        value = value.strip()

        return value or None