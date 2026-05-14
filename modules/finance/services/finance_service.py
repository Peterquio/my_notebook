from modules.finance.cards.finance_card_catalog import FINANCE_CARD_CATALOG


class FinanceService:
    def listar_cards_disponiveis(self) -> list[dict]:
        return FINANCE_CARD_CATALOG