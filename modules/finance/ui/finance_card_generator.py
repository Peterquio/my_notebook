from datetime import date
from dateutil.relativedelta import relativedelta

from ui.widgets.app_card import AppCard
from ui.widgets.card_slot import CardSlot

from modules.finance.ui.widget.credit_card_widget import CreditCardWidget
from modules.finance.services.balance_service import BalanceService
from modules.finance.ui.widget.bank_account_widget import BankAccountWidget

from modules.finance.repositories.finance_settings_repository import (
    FinanceSettingsRepository,
)

def obter_periodo_financeiro_padrao(username: str = "default") -> tuple[str, str]:
    settings_repository = FinanceSettingsRepository(username)

    reference_day = settings_repository.obter_reference_day()
    hoje = date.today()

    if hoje.day >= reference_day:
        inicio = hoje.replace(day=reference_day)
    else:
        inicio = hoje.replace(day=1) + relativedelta(months=-1)

        ultimo_dia = (
            inicio
            + relativedelta(day=31)
        ).day

        inicio = inicio.replace(
            day=min(reference_day, ultimo_dia)
        )

    fim = (
        inicio
        + relativedelta(months=1)
        + relativedelta(days=-1)
    )

    return inicio.isoformat(), fim.isoformat()

def gerar_card_financeiro(
    card_data: dict,
) -> CardSlot:

    if card_data.get("card_type") == "credit_card":
        card = CreditCardWidget(
            card_data
        )


    elif card_data.get("card_type") == "balance":
        service = BalanceService("default")

        hoje = date.today().isoformat()
        _, end_date = obter_periodo_financeiro_padrao("default")

        saldo_atual = (
                service.calcular_saldo_global_na_data(hoje)
                / 100
        )

        saldo_previsto = (
                service.calcular_saldo_global_na_data(end_date)
                / 100
        )

        card = AppCard(
            title="Saldo",
            value=(
                f"Atual: R$ {saldo_atual:,.2f}"
                .replace(",", "X")
                .replace(".", ",")
                .replace("X", ".")
            ),

            subtitle=(
                f"Previsto: R$ {saldo_previsto:,.2f}"
                .replace(",", "X")
                .replace(".", ",")
                .replace("X", ".")
            ),
            icon="💰",
        )

    elif card_data.get("card_type") == "account_balance":
        card = BankAccountWidget(
            card_data
        )

    elif card_data.get("card_type") == "subscriptions":
        card = AppCard(
            title="Assinaturas",
            value="R$ 0,00 este mês",
            subtitle="Nenhuma assinatura ativa",
            icon="🔁",
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