from PySide6.QtCore import (
    QEasingCurve,
    QPropertyAnimation,
    QSize,
    QParallelAnimationGroup
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
        self.shadow = QGraphicsDropShadowEffect()

        self.shadow.setBlurRadius(8)
        self.shadow.setOffset(0, 2)
        self.shadow.setColor(QColor(0, 0, 0, 18))

        self.setGraphicsEffect(self.shadow)

    def set_hovered(self, hovered: bool) -> None:
        blur_target = 32 if hovered else 8
        offset_target = 8 if hovered else 2

        self.shadow_animation = QParallelAnimationGroup(self)

        blur_animation = QPropertyAnimation(
            self.shadow,
            b"blurRadius",
        )
        blur_animation.setDuration(160)
        blur_animation.setStartValue(self.shadow.blurRadius())
        blur_animation.setEndValue(blur_target)
        blur_animation.setEasingCurve(QEasingCurve.OutCubic)

        offset_animation = QPropertyAnimation(
            self.shadow,
            b"yOffset",
        )
        offset_animation.setDuration(160)
        offset_animation.setStartValue(self.shadow.yOffset())
        offset_animation.setEndValue(offset_target)
        offset_animation.setEasingCurve(QEasingCurve.OutCubic)

        self.shadow_animation.addAnimation(blur_animation)
        self.shadow_animation.addAnimation(offset_animation)
        self.shadow_animation.start()

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