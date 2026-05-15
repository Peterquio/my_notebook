from modules.finance.dashboard.finance_dashboard_card_handlers import (
    GenericFinanceDashboardCardHandler,
    CreditCardFinanceDashboardCardHandler,
)


class FinanceDashboardCardRegistry:
    def __init__(
            self,
            card_generator,
            credit_card_service=None,
    ) -> None:

        self.generic_handler = GenericFinanceDashboardCardHandler(
            card_generator
        )

        self.handlers = {}

        if credit_card_service is not None:
            self.handlers["credit_card"] = CreditCardFinanceDashboardCardHandler(
                card_generator=card_generator,
                credit_card_service=credit_card_service,
            )

    def get_handler(
            self,
            card_type: str,
    ):

        return self.handlers.get(
            card_type,
            self.generic_handler,
        )

    def create_new_card_data(
            self,
            template_data: dict,
    ) -> dict:

        card_type = template_data["id"]

        handler = self.get_handler(
            card_type
        )

        return handler.create_new_card_data(
            template_data
        )

    def hydrate_card_data(
            self,
            layout_item: dict,
            template_data: dict,
    ) -> dict:

        handler = self.get_handler(
            layout_item["card_type"]
        )

        return handler.hydrate_card_data(
            layout_item,
            template_data,
        )

    def generate_slot(
            self,
            card_data: dict,
    ):

        handler = self.get_handler(
            card_data["card_type"]
        )

        return handler.generate_slot(
            card_data
        )