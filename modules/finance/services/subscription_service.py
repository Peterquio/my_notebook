from modules.finance.repositories.subscription_repository import (
    SubscriptionRepository,
)


class SubscriptionService:
    def __init__(
            self,
            username: str,
    ) -> None:

        self.repository = (
            SubscriptionRepository(
                username
            )
        )

    # =========================================================
    # CRIAR
    # =========================================================

    def criar_assinatura(
            self,
            name: str,
            amount_cents: int,
            charge_day: int,
            category_id: int,
            description: str | None = None,
            notes: str | None = None,
    ) -> int:

        dados = self._validar_dados(
            name=name,
            amount_cents=amount_cents,
            charge_day=charge_day,
            category_id=category_id,
            description=description,
            notes=notes,
        )

        return self.repository.criar_assinatura(
            **dados
        )

    # =========================================================
    # ATUALIZAR
    # =========================================================

    def atualizar_assinatura(
            self,
            subscription_id: int,
            name: str,
            amount_cents: int,
            charge_day: int,
            category_id: int,
            description: str | None = None,
            notes: str | None = None,
    ) -> None:

        self._garantir_existe(
            subscription_id
        )

        dados = self._validar_dados(
            name=name,
            amount_cents=amount_cents,
            charge_day=charge_day,
            category_id=category_id,
            description=description,
            notes=notes,
        )

        self.repository.atualizar_assinatura(
            subscription_id=subscription_id,
            **dados,
        )

    # =========================================================
    # CONSULTA
    # =========================================================

    def listar_assinaturas(
            self,
            include_inactive: bool = False,
    ) -> list[dict]:

        return (
            self.repository
            .listar_assinaturas(
                include_inactive=include_inactive
            )
        )

    def buscar_assinatura_por_id(
            self,
            subscription_id: int,
    ) -> dict | None:

        return (
            self.repository
            .buscar_assinatura_por_id(
                subscription_id
            )
        )

    # =========================================================
    # STATUS
    # =========================================================

    def desativar_assinatura(
            self,
            subscription_id: int,
    ) -> None:

        self._garantir_existe(
            subscription_id
        )

        self.repository.desativar_assinatura(
            subscription_id
        )

    def reativar_assinatura(
            self,
            subscription_id: int,
    ) -> None:

        self._garantir_existe(
            subscription_id
        )

        self.repository.reativar_assinatura(
            subscription_id
        )

    # =========================================================
    # ARQUIVAR
    # =========================================================

    def arquivar_assinatura(
            self,
            subscription_id: int,
            archive_reason: str | None = None,
    ) -> None:

        self._garantir_existe(
            subscription_id
        )

        self.repository.arquivar_assinatura(
            subscription_id=subscription_id,
            archive_reason=self._texto(
                archive_reason
            ),
        )

    # =========================================================
    # VALIDAÇÃO
    # =========================================================

    def _garantir_existe(
            self,
            subscription_id: int,
    ) -> None:

        if (
            self.repository
            .buscar_assinatura_por_id(
                subscription_id
            )
            is None
        ):
            raise ValueError(
                "Assinatura não encontrada."
            )

    def _validar_dados(
            self,
            name: str,
            amount_cents: int,
            charge_day: int,
            category_id: int,
            description: str | None,
            notes: str | None,
    ) -> dict:

        name = (
            name
            or ""
        ).strip()

        if not name:
            raise ValueError(
                "Informe o nome da assinatura."
            )

        try:
            amount_cents = int(
                amount_cents
            )
        except (TypeError, ValueError):
            raise ValueError(
                "Valor da assinatura inválido."
            )

        if amount_cents <= 0:
            raise ValueError(
                "O valor da assinatura precisa "
                "ser maior que zero."
            )

        try:
            charge_day = int(
                charge_day
            )
        except (TypeError, ValueError):
            raise ValueError(
                "Dia da cobrança inválido."
            )

        if not 1 <= charge_day <= 31:
            raise ValueError(
                "O dia da cobrança precisa "
                "estar entre 1 e 31."
            )

        try:
            category_id = int(
                category_id
            )
        except (TypeError, ValueError):
            raise ValueError(
                "Selecione uma categoria."
            )

        if category_id <= 0:
            raise ValueError(
                "Selecione uma categoria."
            )

        return {
            "name": name,
            "amount_cents": amount_cents,
            "charge_day": charge_day,
            "category_id": category_id,
            "description": self._texto(
                description
            ),
            "notes": self._texto(
                notes
            ),
        }

    def _texto(
            self,
            value: str | None,
    ) -> str | None:

        if value is None:
            return None

        value = value.strip()

        return value or None