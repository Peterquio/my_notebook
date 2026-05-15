from modules.finance.repositories.credit_card_repository import (
    CreditCardRepository,
)


class CreditCardService:
    def __init__(
            self,
            username: str,
    ) -> None:

        self.repository = CreditCardRepository(
            username
        )

    def listar_assets(self) -> list[dict]:
        return self.repository.listar_assets()

    def criar_cartao(
            self,
            dashboard_card_id: str,
            name: str,
            asset_id: str,
            limit_amount_cents: int,
            closing_day: int,
            due_day: int,
            last_four_digits: str | None = None,
    ) -> int:

        return self.repository.criar_cartao(
            dashboard_card_id=dashboard_card_id,
            name=name,
            asset_id=asset_id,
            limit_amount_cents=limit_amount_cents,
            closing_day=closing_day,
            due_day=due_day,
            last_four_digits=last_four_digits,
        )

    def buscar_por_dashboard_card_id(
            self,
            dashboard_card_id: str,
    ) -> dict | None:

        return self.repository.buscar_por_dashboard_card_id(
            dashboard_card_id
        )