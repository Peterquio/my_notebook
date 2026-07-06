from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout

from ui.widgets.base_screen import BaseScreen
from ui.widgets.editable_dashboard_area import EditableDashboardArea


class DashboardHomeBase(BaseScreen):
    def __init__(
            self,
            title: str,
            subtitle: str = "",
            spacing: int = 20,
            grid_strategy: str = "free",
    ) -> None:

        super().__init__(
            title=title,
            subtitle=subtitle,
        )

        self.dashboard_area = EditableDashboardArea(
            spacing=spacing,
            on_save_layout=self._salvar_layout_dashboard,
            grid_strategy=grid_strategy,
        )

        self.dashboard_area.edit_mode_changed.connect(
            self.set_edit_mode
        )

        self.header_actions.addWidget(
            self.dashboard_area.toolbar
        )

        content_layout = QVBoxLayout(self.content_area)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.addWidget(self.dashboard_area)
        content_layout.setAlignment(Qt.AlignTop)

    def _salvar_layout_dashboard(
            self,
            layout_items: list[dict],
    ) -> None:

        pass

    def limpar_dashboard(self) -> None:
        for slot in list(self.dashboard_area.card_slots):
            self.dashboard_area.dashboard_grid.remove_card(slot)

        self.dashboard_area.card_slots.clear()