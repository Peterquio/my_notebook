from PySide6.QtCore import (
    Qt,
    QSize,
)
from PySide6.QtGui import (
    QColor,
    QIcon,
    QPainter,
    QPixmap,
)
from PySide6.QtWidgets import (
    QComboBox,
)


class CategoryComboBox(QComboBox):
    def __init__(
            self,
            categories: list[dict] | None = None,
            width: int | None = None,
            height: int = 38,
            placeholder: str = "Escolha uma categoria",
            parent=None,
    ) -> None:
        super().__init__(parent)

        self.categories = (
            categories or []
        )

        self.placeholder = placeholder

        self.setFixedHeight(
            height
        )

        if width is not None:
            self.setFixedWidth(
                width
            )

        self.setIconSize(
            QSize(
                14,
                14,
            )
        )

        self._aplicar_estilo()
        self.set_categories(
            self.categories
        )

    # =========================================================
    # CATEGORIAS
    # =========================================================

    def set_categories(
            self,
            categories: list[dict],
    ) -> None:

        self.categories = (
            categories or []
        )

        current_id = (
            self.currentData()
        )

        self.blockSignals(
            True
        )

        self.clear()

        # -----------------------------------------------------
        # PLACEHOLDER
        # -----------------------------------------------------

        self.addItem(
            self.placeholder,
            None,
        )

        # -----------------------------------------------------
        # CATEGORIAS
        # -----------------------------------------------------

        for category in self.categories:

            category_id = (
                category.get("id")
            )

            name = (
                category.get("name")
                or "Sem nome"
            )

            color = (
                category.get("color")
                or "#94a3b8"
            )

            icon = (
                self._criar_icone_cor(
                    color
                )
            )

            self.addItem(
                icon,
                name,
                category_id,
            )

        # -----------------------------------------------------
        # TENTA RESTAURAR SELEÇÃO
        # -----------------------------------------------------

        if current_id is not None:

            index = self.findData(
                current_id
            )

            if index >= 0:
                self.setCurrentIndex(
                    index
                )

        self.blockSignals(
            False
        )

    # =========================================================
    # VALORES
    # =========================================================

    def category_id(
            self,
    ) -> int | None:

        return self.currentData()

    def selected_category(
            self,
    ) -> dict | None:

        category_id = (
            self.currentData()
        )

        if category_id is None:
            return None

        for category in self.categories:

            if (
                category.get("id")
                == category_id
            ):
                return category

        return None

    def select_category(
            self,
            category_id: int | None,
    ) -> None:

        if category_id is None:

            self.setCurrentIndex(
                0
            )

            return

        index = self.findData(
            category_id
        )

        if index >= 0:

            self.setCurrentIndex(
                index
            )

    # =========================================================
    # ÍCONE COLORIDO
    # =========================================================

    def _criar_icone_cor(
            self,
            color: str,
    ) -> QIcon:

        pixmap = QPixmap(
            16,
            16,
        )

        pixmap.fill(
            Qt.transparent
        )

        painter = QPainter(
            pixmap
        )

        painter.setRenderHint(
            QPainter.Antialiasing
        )

        cor = QColor(
            color
        )

        if not cor.isValid():
            cor = QColor(
                "#94a3b8"
            )

        painter.setPen(
            Qt.NoPen
        )

        painter.setBrush(
            cor
        )

        painter.drawEllipse(
            3,
            3,
            10,
            10,
        )

        painter.end()

        return QIcon(
            pixmap
        )

    # =========================================================
    # ESTILO
    # =========================================================

    def _aplicar_estilo(
            self,
    ) -> None:

        self.setStyleSheet(
            """
            QComboBox {
                background-color: #ffffff;
                color: #0f172a;

                border: 1px solid #dbe3ed;
                border-radius: 14px;

                padding-left: 12px;
                padding-right: 30px;

                font-family: Segoe UI;
                font-size: 12px;
            }

            QComboBox:hover {
                border: 1px solid #cbd5e1;
                background-color: #ffffff;
            }

            QComboBox:focus {
                border: 1px solid #60a5fa;
            }

            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;

                width: 28px;

                border: none;
                background-color: transparent;
            }

            QComboBox::down-arrow {
                image: none;

                width: 0px;
                height: 0px;

                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid #64748b;
            }

            QComboBox QAbstractItemView {
                background-color: #ffffff;
                color: #334155;

                border: 1px solid #dbe3ed;
                border-radius: 10px;

                padding: 5px;

                outline: none;

                selection-background-color: #eff6ff;
                selection-color: #1d4ed8;
            }

            QComboBox QAbstractItemView::item {
                min-height: 30px;
                padding: 4px 8px;
                border-radius: 6px;
            }

            QComboBox QAbstractItemView::item:hover {
                background-color: #f1f5f9;
            }

            QComboBox QAbstractItemView::item:selected {
                background-color: #eff6ff;
                color: #1d4ed8;
            }
            """
        )