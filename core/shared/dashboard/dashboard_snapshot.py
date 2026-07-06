class DashboardSnapshot:
    def __init__(self) -> None:
        self._snapshot = None

    def create(
            self,
            items: list,
            card_positions: dict,
            add_button,
    ) -> None:

        self._snapshot = {
            "items": [
                item.copy()
                for item in items
                if item["widget"] != add_button
            ],
            "card_positions": {
                widget: position.copy()
                for widget, position
                in card_positions.items()
                if widget != add_button
            },
        }

    def has_snapshot(self) -> bool:
        return self._snapshot is not None

    def get_items(self) -> list:
        if self._snapshot is None:
            return []

        return [
            item.copy()
            for item in self._snapshot["items"]
        ]

    def get_positions(self) -> dict:
        if self._snapshot is None:
            return {}

        return {
            widget: position.copy()
            for widget, position
            in self._snapshot["card_positions"].items()
        }

    def clear(self) -> None:
        self._snapshot = None