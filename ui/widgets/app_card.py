from PySide6.QtCore import (
    QEasingCurve,
    Property,
    QPropertyAnimation,
    QSize,
)

from PySide6.QtGui import QColor

from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QGraphicsDropShadowEffect,
)


class AppCard(QFrame):
    def __init__(
        self,
        title: str,
        value: str = "",
        subtitle: str = "",
        icon: str = "",
        width: int = 260,
        height: int = 180,
    ):
        super().__init__()

        self.default_size = QSize(width, height)
        self.hover_size = QSize(
            int(width * 1.04),
            int(height * 1.04),
        )

        self.setFixedSize(self.default_size)

        self.setObjectName("AppCard")

        self._criar_shadow()
        self._criar_layout(
            title,
            value,
            subtitle,
            icon,
        )

    def _criar_shadow(self) -> None:
        shadow = QGraphicsDropShadowEffect()

        shadow.setBlurRadius(25)
        shadow.setOffset(0, 6)

        shadow.setColor(QColor(0, 0, 0, 40))

        self.setGraphicsEffect(shadow)

    def _criar_layout(
        self,
        title: str,
        value: str,
        subtitle: str,
        icon: str,
    ) -> None:

        layout = QVBoxLayout(self)

        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        top_layout = QHBoxLayout()

        title_label = QLabel(title)
        title_label.setObjectName("CardTitle")

        top_layout.addWidget(title_label)
        top_layout.addStretch()

        if icon:
            icon_label = QLabel(icon)
            icon_label.setObjectName("CardIcon")

            top_layout.addWidget(icon_label)

        layout.addLayout(top_layout)

        value_label = QLabel(value)
        value_label.setObjectName("CardValue")

        layout.addWidget(value_label)

        if subtitle:
            subtitle_label = QLabel(subtitle)
            subtitle_label.setObjectName("CardSubtitle")

            layout.addWidget(subtitle_label)

        layout.addStretch()