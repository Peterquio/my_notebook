import csv

from modules.finance.services.importers.credit_card_csv_converters import (
    NubankCsvConverter,
    ImportedCreditCardExpense,
)


class CreditCardCsvImportHandler:
    def __init__(self) -> None:
        self.converters = [
            NubankCsvConverter(),
        ]

    def import_preview(
            self,
            csv_path: str,
    ) -> list[ImportedCreditCardExpense]:

        headers, sample_rows = self._read_csv_signature(
            csv_path
        )

        converter = self._detect_converter(
            headers,
            sample_rows,
        )

        if converter is None:
            raise ValueError(
                "Não foi possível identificar o formato do CSV."
            )

        return converter.convert(
            csv_path
        )

    def _detect_converter(
            self,
            headers: list[str],
            sample_rows: list[dict],
    ):

        for converter in self.converters:
            if converter.can_handle(
                    headers,
                    sample_rows,
            ):
                return converter

        return None

    def _read_csv_signature(
            self,
            csv_path: str,
    ) -> tuple[list[str], list[dict]]:

        with open(
                csv_path,
                mode="r",
                encoding="utf-8",
                newline="",
        ) as arquivo:
            reader = csv.DictReader(arquivo)
            headers = [
                h.strip().lower()
                for h in (reader.fieldnames or [])
            ]

            sample_rows = []

            for index, row in enumerate(reader):
                if index >= 5:
                    break

                sample_rows.append(row)

        return headers, sample_rows

    def import_adjustments(
            self,
            csv_path: str,
    ):
        headers, sample_rows = self._read_csv_signature(
            csv_path
        )

        converter = self._detect_converter(
            headers,
            sample_rows,
        )

        if converter is None:
            raise ValueError(
                "Não foi possível identificar o formato do CSV."
            )

        if not hasattr(converter, "convert_adjustments"):
            return []

        return converter.convert_adjustments(
            csv_path
        )