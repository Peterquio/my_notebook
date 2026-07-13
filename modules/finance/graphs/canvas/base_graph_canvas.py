from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget

from modules.finance.graphs.canvas.graph_slice import (
    GraphSlice,
)


class BaseGraphCanvas(QWidget):
    slice_hovered = Signal(object)
    slice_clicked = Signal(object)

    def __init__(
            self,
            parent=None,
    ) -> None:

        super().__init__(parent)

        self._data: list[GraphSlice] = []
        self._hover_index = -1

        self.setMouseTracking(True)
        self.setMinimumSize(
            200,
            200,
        )

    def set_data(
            self,
            data: list[GraphSlice],
    ) -> None:

        self._data = list(data)
        self._hover_index = -1

        self.update()

    @property
    def data(
            self,
    ) -> list[GraphSlice]:

        return self._data

    def clear(
            self,
    ) -> None:

        self._data.clear()
        self._hover_index = -1

        self.update()