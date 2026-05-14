from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QVBoxLayout, QWidget

from ui.widgets.dashboard_grid import DashboardGrid
from ui.widgets.dashboard_toolbar import DashboardToolbar


class EditableDashboardArea(QWidget):
    add_card_requested = Signal()
    edit_mode_changed = Signal(bool)

    def __init__(
        self,
        spacing: int = 20,
    ):
        super().__init__()

        self.card_slots = []

        self.toolbar = DashboardToolbar()
        self.dashboard_grid = DashboardGrid(
            spacing=spacing,
        )

        self._criar_layout()
        self._conectar_eventos()

    def _criar_layout(self) -> None:
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.layout.addWidget(self.dashboard_grid)
        self.layout.setAlignment(Qt.AlignTop)

    def _conectar_eventos(self) -> None:
        self.toolbar.edit_mode_changed.connect(
            self.set_edit_mode
        )

        self.toolbar.refresh_requested.connect(
            self.compact_empty_rows
        )

        self.toolbar.cancel_requested.connect(
            self.cancel_edit_mode
        )

        self.dashboard_grid.add_card_requested.connect(
            self.add_card_requested.emit
        )

    def add_card(
        self,
        slot,
        size: str = "1x1",
    ) -> None:
        self.card_slots.append(slot)

        self.dashboard_grid.add_card(
            slot,
            size=size,
        )

    def set_edit_mode(
            self,
            enabled: bool,
    ) -> None:

        if enabled:
            self.dashboard_grid.create_layout_snapshot()
        else:
            self.dashboard_grid.confirm_layout_changes()

        self.dashboard_grid.set_edit_mode(enabled)

        for slot in self.card_slots:
            slot.set_edit_mode(enabled)

        self.edit_mode_changed.emit(enabled)

    def cancel_edit_mode(self) -> None:
        self.dashboard_grid.restore_layout_snapshot()
        self.dashboard_grid.set_edit_mode(False)

        for slot in self.card_slots:
            slot.set_edit_mode(False)

        self.edit_mode_changed.emit(False)

    def compact_empty_rows(self) -> None:
        print("[AREA] Botão refresh clicado -> compact_empty_rows chamado")
        self.dashboard_grid.compact_empty_rows()