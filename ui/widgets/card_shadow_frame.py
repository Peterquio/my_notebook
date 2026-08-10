from PySide6.QtCore import (
    QEasingCurve,
    QParallelAnimationGroup,
    QPropertyAnimation,
)

from PySide6.QtGui import QColor

from PySide6.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
)


class CardShadowFrame(QFrame):
    def __init__(
            self,
            parent=None,
    ) -> None:
        super().__init__(parent)

        self._criar_shadow()

    def _criar_shadow(self) -> None:
        self.shadow = QGraphicsDropShadowEffect(self)

        self.shadow.setBlurRadius(8)
        self.shadow.setOffset(0, 2)
        self.shadow.setColor(
            QColor(0, 0, 0, 18)
        )

        self.setGraphicsEffect(
            self.shadow
        )

    def set_hovered(
            self,
            hovered: bool,
    ) -> None:
        blur_target = (
            32
            if hovered
            else 8
        )

        offset_target = (
            8
            if hovered
            else 2
        )

        self.shadow_animation = QParallelAnimationGroup(
            self
        )

        blur_animation = QPropertyAnimation(
            self.shadow,
            b"blurRadius",
        )

        blur_animation.setDuration(160)
        blur_animation.setStartValue(
            self.shadow.blurRadius()
        )
        blur_animation.setEndValue(
            blur_target
        )
        blur_animation.setEasingCurve(
            QEasingCurve.OutCubic
        )

        offset_animation = QPropertyAnimation(
            self.shadow,
            b"yOffset",
        )

        offset_animation.setDuration(160)
        offset_animation.setStartValue(
            self.shadow.yOffset()
        )
        offset_animation.setEndValue(
            offset_target
        )
        offset_animation.setEasingCurve(
            QEasingCurve.OutCubic
        )

        self.shadow_animation.addAnimation(
            blur_animation
        )

        self.shadow_animation.addAnimation(
            offset_animation
        )

        self.shadow_animation.start()

    def set_pressed(
            self,
            pressed: bool,
    ) -> None:
        pass

    def set_dragging(
            self,
            dragging: bool,
    ) -> None:
        pass