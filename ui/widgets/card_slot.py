from PySide6.QtCore import QEasingCurve, QPropertyAnimation, QRect
from PySide6.QtWidgets import QFrame


class CardSlot(QFrame):
    def __init__(
        self,
        card,
        width: int = 260,
        height: int = 180,
        scale: float = 1.04,
    ):
        super().__init__()

        self.card = card
        self.scale = scale
        self.edit_mode = False

        self.card.setParent(self)

        self.animation = QPropertyAnimation(
            self.card,
            b"geometry",
        )

        self.animation.setDuration(130)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)

        self.set_base_size(width, height)

    def set_base_size(
        self,
        width: int,
        height: int,
    ) -> None:
        self.default_width = width
        self.default_height = height

        self.hover_width = int(width * self.scale)
        self.hover_height = int(height * self.scale)

        self.setFixedSize(
            self.hover_width,
            self.hover_height,
        )

        self.card.setFixedSize(
            self.default_width,
            self.default_height,
        )

        self.card.setGeometry(
            self._default_geometry()
        )

    def _default_geometry(self) -> QRect:
        x = (self.hover_width - self.default_width) // 2
        y = (self.hover_height - self.default_height) // 2

        return QRect(
            x,
            y,
            self.default_width,
            self.default_height,
        )

    def _hover_geometry(self) -> QRect:
        return QRect(
            0,
            0,
            self.hover_width,
            self.hover_height,
        )

    def set_edit_mode(self, enabled: bool) -> None:
        self.edit_mode = enabled

        if not enabled:
            self.animation.stop()
            self.card.setGeometry(
                self._default_geometry()
            )

    def enterEvent(self, event) -> None:
        self.card.set_hovered(True)

        if not self.edit_mode:
            super().enterEvent(event)
            return

        self.animation.stop()
        self.animation.setStartValue(self.card.geometry())
        self.animation.setEndValue(self._hover_geometry())
        self.animation.start()

        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        self.card.set_hovered(False)

        if not self.edit_mode:
            super().leaveEvent(event)
            return

        self.animation.stop()
        self.animation.setStartValue(self.card.geometry())
        self.animation.setEndValue(self._default_geometry())
        self.animation.start()

        super().leaveEvent(event)