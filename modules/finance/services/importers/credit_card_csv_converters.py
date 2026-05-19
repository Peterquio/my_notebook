import csv
import re
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, ROUND_HALF_UP


@dataclass
class ImportedCreditCardExpense:
    purchase_date: date
    description: str
    amount_cents: int
    installment_number: int
    installment_total: int
    raw_title: str
    source: str


class NubankCsvConverter:
    source_name = "Nubank"

    PARCELA_PATTERNS = [
        re.compile(r"\s*-\s*Parcela\s+(\d+)\s*/\s*(\d+)", re.IGNORECASE),
        re.compile(r"\s*-\s*(\d+)\s*/\s*(\d+)", re.IGNORECASE),
    ]

    def can_handle(
            self,
            headers: list[str],
            sample_rows: list[dict],
    ) -> bool:

        return set(headers) == {
            "date",
            "title",
            "amount",
        }

    def convert(
            self,
            csv_path: str,
    ) -> list[ImportedCreditCardExpense]:

        expenses = []

        with open(
                csv_path,
                mode="r",
                encoding="utf-8",
                newline="",
        ) as arquivo:
            reader = csv.DictReader(arquivo)

            for row in reader:
                amount_cents = self._converter_valor_para_centavos(
                    row["amount"]
                )

                if amount_cents <= 0:
                    continue

                raw_title = row["title"].strip()

                description, installment_number, installment_total = (
                    self._extrair_parcelamento(raw_title)
                )

                expenses.append(
                    ImportedCreditCardExpense(
                        purchase_date=date.fromisoformat(row["date"]),
                        description=description,
                        amount_cents=amount_cents,
                        installment_number=installment_number,
                        installment_total=installment_total,
                        raw_title=raw_title,
                        source=self.source_name,
                    )
                )

        return expenses

    def _extrair_parcelamento(
            self,
            title: str,
    ) -> tuple[str, int, int]:

        for pattern in self.PARCELA_PATTERNS:
            match = pattern.search(title)

            if match:
                installment_number = int(match.group(1))
                installment_total = int(match.group(2))

                description = pattern.sub(
                    "",
                    title,
                ).strip()

                return (
                    description,
                    installment_number,
                    installment_total,
                )

        return (
            title,
            1,
            1,
        )

    def _converter_valor_para_centavos(
            self,
            amount_text: str,
    ) -> int:

        valor = Decimal(amount_text).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )

        return int(valor * 100)