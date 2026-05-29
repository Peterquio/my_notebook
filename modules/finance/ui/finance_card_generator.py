from ui.widgets.app_card import AppCard
from ui.widgets.card_slot import CardSlot

from modules.finance.ui.widget.credit_card_widget import CreditCardWidget
from modules.finance.services.balance_service import BalanceService

def gerar_card_financeiro(
    card_data: dict,
) -> CardSlot:

    if card_data.get("card_type") == "credit_card":
        card = CreditCardWidget(
            card_data
        )

    elif card_data.get("card_type") == "balance":
        cycle_id = card_data.get("config", {}).get("cycle_id", 1)

        service = BalanceService("default")
        resumo = service.obter_resumo_dashboard(cycle_id)

        saldo_atual = resumo["saldo_atual_cents"] / 100
        saldo_previsto = resumo["saldo_previsto_cents"] / 100

        card = AppCard(
            title="Saldo",
            value=f"Atual: R$ {saldo_atual:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            subtitle=f"Previsto: R$ {saldo_previsto:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            icon="💰",
        )

    elif card_data.get("card_type") == "account_balance":

        config = card_data.get("config", {})

        cycle_id = config.get("cycle_id", 1)
        account_id = config.get("account_id", 1)

        service = BalanceService("default")

        resumo = service.obter_resumo_conta_dashboard(
            cycle_id=cycle_id,
            account_id=account_id,
        )

        saldo_atual = resumo["saldo_atual_cents"] / 100
        saldo_previsto = resumo["saldo_previsto_cents"] / 100

        card = AppCard(
            title=f"Conta #{account_id}",
            value=f"Atual: R$ {saldo_atual:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            subtitle=f"Previsto: R$ {saldo_previsto:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            icon="🏦",
        )

    else:
        card = AppCard(
            title=card_data["title"],
            value="",
            subtitle=card_data.get("subtitle", ""),
            icon=card_data.get("icon", ""),
        )


    slot = CardSlot(
        card,
        size=card_data.get("size", "1x1"),
        card_id=card_data.get("id"),
    )

    slot.card_type = card_data.get("card_type")
    slot.card_config = card_data.get("config", {})

    return slot