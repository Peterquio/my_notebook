import uuid
from PySide6.QtWidgets import QDialog
from datetime import date
from dateutil.relativedelta import relativedelta

from modules.finance.ui.dialogs.credit_card_setup_dialog import CreditCardSetupDialog
from modules.finance.ui.dialogs.bank_account_setup_dialog import BankAccountSetupDialog
from modules.finance.services.balance_service import BalanceService
from modules.finance.repositories.finance_settings_repository import FinanceSettingsRepository
from modules.finance.services.balance_account_service import BalanceAccountService
from modules.finance.services.pix_service import PixService

class GenericFinanceDashboardCardHandler:
    def __init__(
            self,
            card_generator,
    ) -> None:

        self.card_generator = card_generator

    def create_new_card_data(
            self,
            template_data: dict,
    ) -> dict:

        card_data = template_data.copy()

        template_id = card_data["id"]

        card_data["id"] = str(uuid.uuid4())
        card_data["card_type"] = template_id
        card_data["config"] = {}

        return card_data

    def hydrate_card_data(
            self,
            layout_item: dict,
            template_data: dict,
    ) -> dict:

        return {
            "id": layout_item["card_id"],
            "card_type": layout_item["card_type"],
            "config": layout_item.get("config", {}),

            "title": template_data.get("title", layout_item["card_type"]),
            "subtitle": template_data.get("subtitle", ""),
            "icon": template_data.get("icon", ""),
            "size": template_data.get(
                "size",
                f'{layout_item["width_units"]}x{layout_item["height_units"]}',
            ),
        }

    def generate_slot(
            self,
            card_data: dict,
    ):

        return self.card_generator(
            card_data
        )


class CreditCardFinanceDashboardCardHandler(GenericFinanceDashboardCardHandler):
    def __init__(
            self,
            card_generator,
            credit_card_service,
            username: str,
    ) -> None:

        super().__init__(
            card_generator
        )

        self.credit_card_service = credit_card_service
        self.account_service = BalanceAccountService(
            username
        )

    def hydrate_card_data(
            self,
            layout_item: dict,
            template_data: dict,
    ) -> dict:

        card_data = super().hydrate_card_data(
            layout_item,
            template_data,
        )

        credit_card = self.credit_card_service.buscar_por_dashboard_card_id(
            layout_item["card_id"]
        )

        if credit_card is None:
            return card_data

        card_data["config"].update(
            {
                "name": credit_card["name"],
                "asset_id": credit_card["asset_id"],
                "bank_name": credit_card["bank_name"],
                "asset_name": credit_card["asset_name"],
                "preset_key": credit_card["preset_key"],
                "limit_amount_cents": credit_card["limit_amount_cents"],
                "closing_day": credit_card["closing_day"],
                "due_day": credit_card["due_day"],
                "last_four_digits": credit_card["last_four_digits"],
                "current_invoice_amount_cents": self.credit_card_service.obter_total_fatura_atual(
                    credit_card_id=credit_card["id"],
                    closing_day=credit_card["closing_day"],
                ),
            }
        )

        return card_data

    def create_new_card_data(
            self,
            template_data: dict,
    ) -> dict | None:

        card_data = super().create_new_card_data(
            template_data
        )

        setup_dialog = CreditCardSetupDialog(
            assets=self.credit_card_service.listar_assets(),
            accounts=self.account_service.listar_contas(),
        )

        if setup_dialog.exec() != QDialog.Accepted:
            return None

        card_config = setup_dialog.get_data()

        card_data["config"] = card_config

        self.credit_card_service.criar_cartao(
            dashboard_card_id=card_data["id"],
            name=card_config["name"],
            asset_id=card_config["asset_id"],
            limit_amount_cents=card_config["limit_amount_cents"],
            closing_day=card_config["closing_day"],
            due_day=card_config["due_day"],
            last_four_digits=card_config["last_four_digits"],
            account_id=card_config["account_id"],
            sync_with_balance=card_config["sync_with_balance"],
        )

        return card_data

class AccountBalanceFinanceDashboardCardHandler(GenericFinanceDashboardCardHandler):
    def __init__(
            self,
            card_generator,
            username: str,
    ) -> None:

        super().__init__(
            card_generator
        )

        self.username = username
        self.account_service = BalanceAccountService(
            username
        )
        self.balance_service = BalanceService(
            username
        )

    def create_new_card_data(
            self,
            template_data: dict,
    ) -> dict | None:

        card_data = super().create_new_card_data(
            template_data
        )

        dialog = BankAccountSetupDialog()

        if dialog.exec() != QDialog.Accepted:
            return None

        dados = dialog.obter_dados()

        self.account_service.criar_conta(
            dashboard_card_id=card_data["id"],
            name=dados["name"],
            account_type=dados["account_type"],
            institution_name=dados["institution_name"],
            bank_preset_key=dados["bank_preset_key"],
            agency=dados["agency"],
            account_number=dados["account_number"],
            account_kind=dados["account_kind"],
            include_in_global_balance=dados["include_in_global_balance"],
            is_investment=dados["is_investment"],
            opening_balance_cents=dados["opening_balance_cents"],
        )

        card_data["config"] = {
            "name": dados["name"],
            "account_type": dados["account_type"],
            "institution_name": dados["institution_name"],
            "bank_preset_key": dados["bank_preset_key"],
            "agency": dados["agency"],
            "account_number": dados["account_number"],
            "account_kind": dados["account_kind"],
            "current_balance_cents": dados["opening_balance_cents"],
            "projected_balance_cents": dados["opening_balance_cents"],
            "projected_date": "",
            "pix_scheduled_count": 0,
        }

        return card_data

    def hydrate_card_data(
            self,
            layout_item: dict,
            template_data: dict,
    ) -> dict:

        card_data = super().hydrate_card_data(
            layout_item,
            template_data,
        )

        conta = self.account_service.buscar_por_dashboard_card_id(
            layout_item["card_id"]
        )

        if conta is None:
            return card_data

        hoje = date.today().isoformat()
        _, end_date = self._obter_periodo_financeiro_padrao()

        card_data["config"].update(
            {
                "account_id": conta["id"],
                "name": conta["name"],
                "account_type": conta["account_type"],
                "institution_name": conta["institution_name"],
                "bank_preset_key": conta["bank_preset_key"],
                "agency": conta["agency"],
                "account_number": conta["account_number"],
                "account_kind": conta["account_kind"],
                "current_balance_cents": self.balance_service.calcular_saldo_conta_na_data(
                    account_id=conta["id"],
                    data_iso=hoje,
                ),
                "projected_balance_cents": self.balance_service.calcular_saldo_conta_na_data(
                    account_id=conta["id"],
                    data_iso=end_date,
                ),
                "projected_date": end_date,
                "pix_scheduled_count": 0,
            }
        )

        return card_data

    def _obter_periodo_financeiro_padrao(self) -> tuple[str, str]:
        reference_day = FinanceSettingsRepository(
            self.username
        ).obter_reference_day()

        hoje = date.today()

        if hoje.day >= reference_day:
            inicio = hoje.replace(day=reference_day)
        else:
            inicio = hoje.replace(day=1) + relativedelta(months=-1)
            ultimo_dia = (inicio + relativedelta(day=31)).day
            inicio = inicio.replace(day=min(reference_day, ultimo_dia))

        fim = inicio + relativedelta(months=1) - relativedelta(days=1)

        return inicio.isoformat(), fim.isoformat()

class PixFinanceDashboardCardHandler(
    GenericFinanceDashboardCardHandler
):
    def __init__(
            self,
            card_generator,
            username: str,
    ) -> None:

        super().__init__(
            card_generator
        )

        self.username = username

        self.pix_service = PixService(
            username
        )

    def create_new_card_data(
            self,
            template_data: dict,
    ) -> dict:

        card_data = super().create_new_card_data(
            template_data
        )

        card_data["config"].update(
            self._obter_config_resumo()
        )

        return card_data

    def hydrate_card_data(
            self,
            layout_item: dict,
            template_data: dict,
    ) -> dict:

        card_data = super().hydrate_card_data(
            layout_item,
            template_data,
        )

        card_data["config"].update(
            self._obter_config_resumo()
        )

        return card_data

    def _obter_config_resumo(
            self,
    ) -> dict:

        resumo = (
            self.pix_service
            .obter_resumo_periodo_atual()
        )

        return {
            "start_date": resumo["start_date"],
            "end_date": resumo["end_date"],
            "sent_cents": resumo["sent_cents"],
            "received_cents": resumo["received_cents"],
            "total_transactions": resumo[
                "total_transactions"
            ],
        }