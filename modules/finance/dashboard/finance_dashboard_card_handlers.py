import uuid
from PySide6.QtWidgets import QDialog
from modules.finance.ui.credit_card_setup_dialog import CreditCardSetupDialog

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
    ) -> None:

        super().__init__(
            card_generator
        )

        self.credit_card_service = credit_card_service

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
                "background_type": credit_card["background_type"],
                "background_value": credit_card["background_value"],
                "text_color": credit_card["text_color"],
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
        )

        return card_data