from PySide6.QtCore import QDate
from PySide6.QtWidgets import QLineEdit


class DateLineEdit(QLineEdit):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self._formatando = False
        self.setPlaceholderText("dd/mm/aaaa")
        self.setMaxLength(10)

        self.textChanged.connect(self._formatar_texto)

    def _formatar_texto(self, texto: str) -> None:
        if self._formatando:
            return

        somente_numeros = "".join(
            char for char in texto
            if char.isdigit()
        )[:8]

        partes = []

        if len(somente_numeros) <= 2:
            partes.append(somente_numeros)
        else:
            partes.append(somente_numeros[:2])
            partes.append(somente_numeros[2:4])

            if len(somente_numeros) > 4:
                partes.append(somente_numeros[4:8])

        texto_formatado = "/".join(
            parte for parte in partes
            if parte
        )

        self._formatando = True
        self.setText(texto_formatado)
        self.setCursorPosition(len(texto_formatado))
        self._formatando = False

    def set_date(self, date: QDate) -> None:
        self.setText(date.toString("dd/MM/yyyy"))

    def to_qdate(self, fallback_year: int | None = None) -> QDate:
        partes = self.text().split("/")

        if len(partes) == 2 and fallback_year is not None:
            dia, mes = partes
            ano = str(fallback_year)
        elif len(partes) == 3:
            dia, mes, ano = partes
        else:
            return QDate.currentDate()

        date = QDate(
            int(ano),
            int(mes),
            int(dia),
        )

        if not date.isValid():
            return QDate.currentDate()

        return date

    def to_iso_date(self, fallback_year: int | None = None) -> str:
        return self.to_qdate(fallback_year).toString("yyyy-MM-dd")