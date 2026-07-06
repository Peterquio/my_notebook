from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QScrollArea


class DashboardAutoScroll:
    def __init__(
            self,
            owner,
            speed: int = 18,
            margin: int = 80,
            interval: int = 30,
    ) -> None:

        self.owner = owner
        self.speed = speed
        self.margin = margin

        self.active = False
        self.direction = 0

        self.timer = QTimer(owner)
        self.timer.setInterval(interval)
        self.timer.timeout.connect(self.perform)

    def start(self) -> None:
        self.active = True

    def stop(self) -> None:
        self.active = False
        self._stop_timer()

    def update(
            self,
            global_pos,
    ) -> None:

        if not self.active:
            self._stop_timer()
            return

        scroll_area = self._get_scroll_area_parent()

        if scroll_area is None:
            self._stop_timer()
            return

        viewport_pos = scroll_area.viewport().mapFromGlobal(
            global_pos
        )

        viewport_height = scroll_area.viewport().height()

        if viewport_pos.y() < self.margin:
            self.direction = -1
        elif viewport_pos.y() > viewport_height - self.margin:
            self.direction = 1
        else:
            self._stop_timer()
            return

        if not self.timer.isActive():
            self.timer.start()

    def perform(self) -> None:
        scroll_area = self._get_scroll_area_parent()

        if scroll_area is None:
            self._stop_timer()
            return

        scroll_bar = scroll_area.verticalScrollBar()

        scroll_bar.setValue(
            scroll_bar.value()
            + self.direction * self.speed
        )

    def _stop_timer(self) -> None:
        self.direction = 0

        if self.timer.isActive():
            self.timer.stop()

    def _get_scroll_area_parent(self) -> QScrollArea | None:
        parent = self.owner.parentWidget()

        while parent is not None:
            if isinstance(parent, QScrollArea):
                return parent

            parent = parent.parentWidget()

        return None