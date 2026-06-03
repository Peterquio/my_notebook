from modules.finance.repositories.monthly_template_repository import (
    MonthlyTemplateRepository,
)


class MonthlyTemplateService:
    TIPOS_VALIDOS = {
        "income",
        "commitment",
    }

    TIPOS_PAGAMENTO_VALIDOS = {
        "bank_account",
        "credit_card",
    }

    def __init__(
            self,
            username: str,
    ) -> None:
        self.repository = MonthlyTemplateRepository(username)

    def criar_template(
            self,
            template_type: str,
            description: str,
            estimated_amount_cents: int,
            day_of_month: int,
            account_id: int | None = None,
            category_id: int | None = None,
            payment_type: str = "bank_account",
            credit_card_id: int | None = None,
            start_date: str | None = None,
            end_date: str | None = None,
            auto_materialize: bool = True,
            notes: str | None = None,
    ) -> int:
        template_type = self._validar_template_type(template_type)
        description = self._validar_description(description)
        estimated_amount_cents = self._validar_valor(estimated_amount_cents)
        day_of_month = self._validar_dia(day_of_month)
        payment_type = self._validar_payment_type(payment_type)

        self._validar_forma_pagamento(
            template_type=template_type,
            payment_type=payment_type,
            account_id=account_id,
            credit_card_id=credit_card_id,
        )

        return self.repository.criar_template(
            template_type=template_type,
            description=description,
            estimated_amount_cents=estimated_amount_cents,
            day_of_month=day_of_month,
            account_id=account_id,
            category_id=category_id,
            payment_type=payment_type,
            credit_card_id=credit_card_id,
            external_reference=None,
            start_date=start_date,
            end_date=end_date,
            auto_materialize=auto_materialize,
            notes=notes,
        )

    def atualizar_template(
            self,
            template_id: int,
            template_type: str,
            description: str,
            estimated_amount_cents: int,
            day_of_month: int,
            account_id: int | None = None,
            category_id: int | None = None,
            payment_type: str = "bank_account",
            credit_card_id: int | None = None,
            start_date: str | None = None,
            end_date: str | None = None,
            auto_materialize: bool = True,
            notes: str | None = None,
    ) -> None:
        template_existente = self.repository.buscar_por_id(template_id)

        if template_existente is None:
            raise ValueError(
                f"Template mensal não encontrado: {template_id}"
            )

        template_type = self._validar_template_type(template_type)
        description = self._validar_description(description)
        estimated_amount_cents = self._validar_valor(estimated_amount_cents)
        day_of_month = self._validar_dia(day_of_month)
        payment_type = self._validar_payment_type(payment_type)

        self._validar_forma_pagamento(
            template_type=template_type,
            payment_type=payment_type,
            account_id=account_id,
            credit_card_id=credit_card_id,
        )

        self.repository.atualizar_template(
            template_id=template_id,
            template_type=template_type,
            description=description,
            estimated_amount_cents=estimated_amount_cents,
            day_of_month=day_of_month,
            account_id=account_id,
            category_id=category_id,
            payment_type=payment_type,
            credit_card_id=credit_card_id,
            external_reference=template_existente.get("external_reference"),
            start_date=start_date,
            end_date=end_date,
            auto_materialize=auto_materialize,
            notes=notes,
        )

    def listar_todos(self) -> list[dict]:
        return self.repository.listar_todos()

    def listar_ativos(self) -> list[dict]:
        return self.repository.listar_ativos()

    def listar_receitas(self) -> list[dict]:
        return self.repository.listar_por_tipo("income")

    def listar_compromissos(self) -> list[dict]:
        return self.repository.listar_por_tipo("commitment")

    def buscar_por_id(
            self,
            template_id: int,
    ) -> dict | None:
        return self.repository.buscar_por_id(template_id)

    def desativar_template(
            self,
            template_id: int,
    ) -> None:
        if self.repository.buscar_por_id(template_id) is None:
            raise ValueError(
                f"Template mensal não encontrado: {template_id}"
            )

        self.repository.desativar_template(template_id)

    def reativar_template(
            self,
            template_id: int,
    ) -> None:
        if self.repository.buscar_por_id(template_id) is None:
            raise ValueError(
                f"Template mensal não encontrado: {template_id}"
            )

        self.repository.reativar_template(template_id)

    def _validar_template_type(
            self,
            template_type: str,
    ) -> str:
        template_type = str(template_type or "").strip().lower()

        if template_type not in self.TIPOS_VALIDOS:
            raise ValueError(
                "Tipo de template inválido. Use 'income' ou 'commitment'."
            )

        return template_type

    def _validar_description(
            self,
            description: str,
    ) -> str:
        description = str(description or "").strip()

        if not description:
            raise ValueError(
                "A descrição do template é obrigatória."
            )

        return description

    def _validar_valor(
            self,
            estimated_amount_cents: int,
    ) -> int:
        try:
            valor = int(estimated_amount_cents)
        except Exception:
            raise ValueError(
                "O valor estimado precisa ser um número inteiro em centavos."
            )

        if valor <= 0:
            raise ValueError(
                "O valor estimado precisa ser maior que zero."
            )

        return valor

    def _validar_dia(
            self,
            day_of_month: int,
    ) -> int:
        try:
            dia = int(day_of_month)
        except Exception:
            raise ValueError(
                "O dia do mês precisa ser um número inteiro."
            )

        if dia < 1 or dia > 31:
            raise ValueError(
                "O dia do mês precisa estar entre 1 e 31."
            )

        return dia

    def _validar_payment_type(
            self,
            payment_type: str,
    ) -> str:
        payment_type = str(payment_type or "").strip().lower()

        if payment_type not in self.TIPOS_PAGAMENTO_VALIDOS:
            raise ValueError(
                "Forma de pagamento inválida. Use 'bank_account' ou 'credit_card'."
            )

        return payment_type

    def _validar_forma_pagamento(
            self,
            template_type: str,
            payment_type: str,
            account_id: int | None,
            credit_card_id: int | None,
    ) -> None:
        if template_type == "income" and payment_type != "bank_account":
            raise ValueError(
                "Receitas mensais só podem entrar em conta financeira."
            )

        if template_type == "income" and account_id is None:
            raise ValueError(
                "Receitas mensais precisam de uma conta financeira."
            )

        if payment_type == "credit_card" and credit_card_id is None:
            raise ValueError(
                "Templates pagos com cartão precisam de um cartão vinculado."
            )

        if payment_type == "bank_account" and credit_card_id is not None:
            raise ValueError(
                "Templates pagos por conta não devem ter cartão vinculado."
            )