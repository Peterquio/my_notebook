from PySide6.QtCore import Signal
from PySide6.QtWidgets import QPushButton, QHBoxLayout, QWidget


class DashboardToolbar(QWidget):

    edit_mode_changed = Signal(bool)

    def __init__(self):
        super().__init__()

        self.edit_mode = False

        self._criar_layout()
        self._criar_widgets()

    def _criar_layout(self) -> None:
        self.layout = QHBoxLayout(self)

        self.layout.setContentsMargins(0, 0, 0, 0)

    def _criar_widgets(self) -> None:
        self.edit_button = QPushButton("⚙")

        self.edit_button.setObjectName("EditButton")

        self.edit_button.clicked.connect(
            self._toggle_edit_mode
        )

        self.layout.addWidget(self.edit_button)

    def _toggle_edit_mode(self) -> None:
        self.edit_mode = not self.edit_mode

        if self.edit_mode:
            self.edit_button.setText("✔")
        else:
            self.edit_button.setText("⚙")

        self.edit_mode_changed.emit(
            self.edit_mode
        )