from core.dashboard.repositories.dashboard_card_repository import (
    DashboardCardRepository,
)


class DashboardCardService:
    def __init__(
            self,
            username: str,
    ) -> None:

        self.repository = DashboardCardRepository(
            username
        )

    def criar_card(
            self,
            module_name: str,
            card_data: dict,
    ) -> None:

        self.repository.criar_card(
            module_name,
            card_data,
        )

    def listar_cards(
            self,
            module_name: str,
            active_only: bool = False,
    ) -> list[dict]:

        return self.repository.listar_cards(
            module_name,
            active_only,
        )

    def atualizar_status_card(
            self,
            card_id: str,
            is_active: bool,
    ) -> None:

        self.repository.atualizar_status_card(
            card_id,
            is_active,
        )

    def desativar_card(
            self,
            card_id: str,
    ) -> None:
        self.repository.atualizar_status_card(
            card_id,
            False,
        )

    def reativar_card(
            self,
            card_id: str,
    ) -> None:
        self.repository.atualizar_status_card(
            card_id,
            True,
        )

    def remover_ou_desativar_card(
            self,
            card_id: str,
            config: dict | None = None,
    ) -> None:
        if not config:
            self.repository.excluir_card(
                card_id
            )
            return

        self.repository.atualizar_status_card(
            card_id,
            False,
        )

    def listar_cards_removidos(
            self,
            module_name: str,
    ) -> list[dict]:
        return self.repository.listar_cards_removidos(
            module_name
        )

    def excluir_card_definitivamente(
            self,
            card_id: str,
    ) -> None:
        self.repository.excluir_card_definitivamente(
            card_id
        )