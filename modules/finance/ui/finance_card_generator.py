from ui.widgets.app_card import AppCard
from ui.widgets.card_slot import CardSlot


def gerar_card_financeiro(
    card_data: dict,
) -> CardSlot:

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