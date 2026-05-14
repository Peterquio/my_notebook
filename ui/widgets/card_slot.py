from PySide6.QtCore import QEasingCurve, QPropertyAnimation, QRect, Qt, QPoint
from PySide6.QtWidgets import QFrame, QPushButton
from PySide6.QtGui import QRegion, QPainterPath

class CardSlot(QFrame):
    def __init__(
            self,
            card,
            width: int = 260,
            height: int = 180,
            scale: float = 1.04,
            size: str = "1x1",
    ):
        super().__init__()

        self.card = card
        self.size = size
        width_units, height_units = (size.lower().split("x"))
        self.width_units = int(width_units)
        self.height_units = int(height_units)
        self.edit_mode = False
        self.pressed = False
        self.drag_start_position = QPoint()
        self.dragging = False
        self.drag_ghost = None
        self.scale = scale
        self.selected = False
        self.setObjectName("CardSlot")
        self.default_style = """
            #CardSlot {
                border: none;
                background-color: transparent;
            }
        """

        self.selected_style = """
            #CardSlot {
                border: 2px solid rgba(37, 99, 235, 120);
                border-radius: 24px;
                background-color: transparent;
            }
        """

        self.setStyleSheet(self.default_style)

        self.card.setParent(self)

        self.delete_button = QPushButton("×", self)
        self.delete_button.setObjectName("DeleteCardButton")
        self.delete_button.setFixedSize(24, 24)
        self.delete_button.setCursor(Qt.PointingHandCursor)

        self.delete_button.hide()

        self.delete_button.clicked.connect(
            self._delete_card
        )

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
        self._position_delete_button()

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

        if enabled:
            self.setCursor(Qt.OpenHandCursor)
            self.card.setCursor(Qt.OpenHandCursor)

            self.delete_button.show()
            self.delete_button.raise_()

        else:
            self.setCursor(Qt.PointingHandCursor)
            self.card.setCursor(Qt.PointingHandCursor)

            self.delete_button.hide()
            self.animation.stop()
            self.card.setGeometry(
                self._default_geometry()
            )

    def mousePressEvent(self, event) -> None:
        if self.edit_mode:
            self.setCursor(Qt.ClosedHandCursor)
            self.card.setCursor(Qt.ClosedHandCursor)
            self.delete_button.setCursor(Qt.PointingHandCursor)
            self.card.set_pressed(True)
            self.drag_start_position = event.position().toPoint()
            self.dragging = False

        self.animation.stop()
        self.animation.setStartValue(self.card.geometry())
        self.animation.setEndValue(self._default_geometry())
        self.animation.start()

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:
        if not self.edit_mode:
            super().mouseMoveEvent(event)
            return

        distance = (
                event.position().toPoint()
                - self.drag_start_position
        ).manhattanLength()

        if distance > 8 and not self.dragging:
            self.dragging = True
            self.card.set_dragging(True)
            self.setCursor(Qt.ClosedHandCursor)
            self.card.setCursor(Qt.ClosedHandCursor)
            self._create_drag_ghost()
            self._move_drag_ghost(event.globalPosition().toPoint())

            dashboard_grid = self._find_dashboard_grid()

            if dashboard_grid is not None:
                dashboard_grid.start_drag_auto_scroll()

        if self.dragging:
            global_pos = event.globalPosition().toPoint()

            self._move_drag_ghost(global_pos)

            dashboard_grid = self._find_dashboard_grid()

            if dashboard_grid is not None:
                dashboard_grid.update_drag_auto_scroll(global_pos)

            if dashboard_grid is not None:
                cell = dashboard_grid.get_cell_from_global_position(
                    global_pos
                )

                if cell is not None:
                    row, column = cell

                    can_drop = dashboard_grid.can_drop_card_at(
                        row=row,
                        column=column,
                        width_units=self.width_units,
                        height_units=self.height_units,
                    )

                    dashboard_grid.show_drop_preview(
                        row=row,
                        column=column,
                        width_units=self.width_units,
                        height_units=self.height_units,
                        valid=can_drop,
                    )

                    conflicts = dashboard_grid.get_cards_in_area(
                        row=row,
                        column=column,
                        width_units=self.width_units,
                        height_units=self.height_units,
                    )

                    print(
                        f"Hover célula -> row={row}, column={column}, "
                        f"pode={can_drop}, conflitos={len(conflicts)}"
                    )

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        if self.edit_mode:
            self.setCursor(Qt.OpenHandCursor)
            self.card.setCursor(Qt.OpenHandCursor)
            self.delete_button.setCursor(Qt.PointingHandCursor)
            self.card.set_pressed(False)

        if self.underMouse():
            self.animation.stop()
            self.animation.setStartValue(self.card.geometry())
            self.animation.setEndValue(self._hover_geometry())
            self.animation.start()


        self.card.set_dragging(False)
        dashboard_grid = self._find_dashboard_grid()

        if dashboard_grid is not None:
            dashboard_grid.hide_drop_preview()

        dashboard_grid = self._find_dashboard_grid()

        if dashboard_grid is not None and self.dragging:
            global_pos = event.globalPosition().toPoint()

            cell = dashboard_grid.get_cell_from_global_position(global_pos)

            if cell is not None:
                row, column = cell

                can_drop = dashboard_grid.can_drop_card_at(
                    row=row,
                    column=column,
                    width_units=self.width_units,
                    height_units=self.height_units,
                )

                conflicts = dashboard_grid.get_cards_in_area(
                    row=row,
                    column=column,
                    width_units=self.width_units,
                    height_units=self.height_units,
                )

                if can_drop:
                    dashboard_grid.move_card_to(
                        self,
                        row=row,
                        column=column,
                    )

                print(
                    f"Soltou em -> row={row}, column={column}, "
                    f"pode={can_drop}, conflitos={len(conflicts)}"
                )

        if dashboard_grid is not None:
            dashboard_grid.stop_drag_auto_scroll()

        self._destroy_drag_ghost()
        self.dragging = False
        super().mouseReleaseEvent(event)

    def set_pressed(self, pressed: bool) -> None:
        self.pressed = pressed

        if pressed:
            self.setStyleSheet(self.selected_style)
        else:
            self.setStyleSheet(self.default_style)

    def enterEvent(self, event) -> None:
        self.animation.stop()
        self.animation.setStartValue(self.card.geometry())
        self.animation.setEndValue(self._hover_geometry())
        self.animation.start()

        if not self.edit_mode:
            self.card.set_hovered(True)

        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        self.animation.stop()
        self.animation.setStartValue(self.card.geometry())
        self.animation.setEndValue(self._default_geometry())
        self.animation.start()

        if not self.edit_mode:
            self.card.set_hovered(False)

        super().leaveEvent(event)

    def _position_delete_button(self) -> None:
        margin = 8

        self.delete_button.move(
            self.width() - self.delete_button.width() - margin,
            margin,
        )

    def _delete_card(self) -> None:
        dashboard_grid = self._find_dashboard_grid()

        if dashboard_grid is None:
            return

        dashboard_grid.remove_card(self)

    def _create_drag_ghost(self) -> None:
        if self.drag_ghost is not None:
            return

        self.drag_ghost = QFrame()
        self.drag_ghost.setFixedSize(self.card.size())

        path = QPainterPath()

        path.addRoundedRect(
            QRect(0, 0, self.drag_ghost.width(), self.drag_ghost.height(),), 22, 22,
        )
        region = QRegion(path.toFillPolygon().toPolygon())
        self.drag_ghost.setMask(region)

        self.drag_ghost.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 255);
                border: 1px solid rgba(148, 163, 184, 120);
                border-radius: 22px;
            }
        """)

        self.drag_ghost.setWindowOpacity(0.72)
        self.drag_ghost.setWindowFlags(
            Qt.FramelessWindowHint
            | Qt.Tool
            | Qt.WindowStaysOnTopHint
        )

        self.drag_ghost.show()

    def _move_drag_ghost(self, global_pos) -> None:
        if self.drag_ghost is None:
            return

        x = global_pos.x() - self.drag_ghost.width() // 2
        y = global_pos.y() - self.drag_ghost.height() // 2

        self.drag_ghost.move(x, y)
        self.drag_ghost.raise_()

    def _destroy_drag_ghost(self) -> None:
        if self.drag_ghost is not None:
            self.drag_ghost.close()
            self.drag_ghost = None

    def _find_dashboard_grid(self):
        parent = self.parent()

        while parent is not None:
            if parent.__class__.__name__ == "DashboardGrid":
                return parent

            parent = parent.parent()

        return None