import sqlite3
from pathlib import Path
from collections import defaultdict


DB_PATH = Path(
    r"C:\dev\Outros\my_notebook\user_data\users\default.db"
)


def carregar_duplicidades(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            e.installment_group_id,
            e.installment_number,
            e.id,
            e.credit_card_id,
            e.invoice_id,
            e.source_type,
            e.created_by,
            e.status,
            e.effective_description,
            e.effective_purchase_date,
            e.effective_amount_cents,
            e.installment_total,

            i.invoice_year,
            i.invoice_month

        FROM finance_credit_card_expenses e

        LEFT JOIN finance_credit_card_invoices i
            ON i.id = e.invoice_id

        WHERE e.installment_group_id IS NOT NULL
          AND e.status != 'cancelled'

        ORDER BY
            e.installment_group_id,
            e.installment_number,
            e.id
        """
    )

    rows = cursor.fetchall()

    grupos = defaultdict(list)

    for row in rows:
        chave = (
            row["installment_group_id"],
            row["installment_number"],
        )

        grupos[chave].append(row)

    duplicidades = []

    for linhas in grupos.values():
        if len(linhas) > 1:
            duplicidades.extend(linhas)

    return duplicidades


def classificar_grupo(rows: list[sqlite3.Row]) -> str:
    tipos = {
        row["source_type"]
        for row in rows
    }

    somente_projecoes = tipos == {
        "projected_installment"
    }

    possui_projecao = (
        "projected_installment" in tipos
    )

    possui_real = any(
        tipo != "projected_installment"
        for tipo in tipos
    )

    if somente_projecoes:
        return "SOMENTE PROJECOES"

    if possui_projecao and possui_real:
        return "REAL + PROJECAO"

    return "SOMENTE REAIS"


def formatar_valor(cents: int | None) -> str:
    cents = cents or 0
    return f"R$ {cents / 100:.2f}"


def main() -> None:
    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"Banco nao encontrado em:\n{DB_PATH}"
        )

    conn = sqlite3.connect(DB_PATH)

    conn.row_factory = sqlite3.Row

    rows = carregar_duplicidades(conn)

    grupos = defaultdict(list)

    for row in rows:
        chave = (
            row["installment_group_id"],
            row["installment_number"],
        )

        grupos[chave].append(row)

    totais = {
        "SOMENTE PROJECOES": 0,
        "REAL + PROJECAO": 0,
        "SOMENTE REAIS": 0,
    }

    print()
    print("=" * 100)
    print("AUDITORIA DE DUPLICIDADES DE PARCELAS")
    print("=" * 100)

    print(
        f"\nBanco: {DB_PATH}"
    )

    print(
        f"Grupos/parcela duplicados encontrados: "
        f"{len(grupos)}"
    )

    for numero, (chave, linhas) in enumerate(
            grupos.items(),
            start=1,
    ):
        group_id, installment_number = chave

        classificacao = classificar_grupo(
            linhas
        )

        totais[classificacao] += 1

        print()
        print("-" * 100)

        print(
            f"[{numero}] {classificacao}"
        )

        print(
            f"Grupo   : {group_id}"
        )

        print(
            f"Parcela : {installment_number}"
        )

        print(
            f"Ativos  : {len(linhas)}"
        )

        for row in linhas:
            competencia = "-"

            if (
                    row["invoice_year"] is not None
                    and row["invoice_month"] is not None
            ):
                competencia = (
                    f"{row['invoice_month']:02d}/"
                    f"{row['invoice_year']}"
                )

            print(
                "\n"
                f"    ID..............: {row['id']}\n"
                f"    Fatura..........: {competencia}\n"
                f"    Invoice ID......: {row['invoice_id']}\n"
                f"    Source Type.....: {row['source_type']}\n"
                f"    Created By......: {row['created_by']}\n"
                f"    Descricao.......: {row['effective_description']}\n"
                f"    Data.............: {row['effective_purchase_date']}\n"
                f"    Valor............: "
                f"{formatar_valor(row['effective_amount_cents'])}\n"
                f"    Parcela..........: "
                f"{row['installment_number']}/"
                f"{row['installment_total']}"
            )

        if classificacao == "SOMENTE PROJECOES":
            manter = max(
                linhas,
                key=lambda row: row["id"],
            )

            cancelar = [
                row["id"]
                for row in linhas
                if row["id"] != manter["id"]
            ]

            print()
            print(
                f"    SUGESTAO KEEP...: {manter['id']}"
            )

            print(
                f"    SUGESTAO CANCEL.: {cancelar}"
            )

        elif classificacao == "REAL + PROJECAO":
            reais = [
                row["id"]
                for row in linhas
                if row["source_type"]
                != "projected_installment"
            ]

            projecoes = [
                row["id"]
                for row in linhas
                if row["source_type"]
                == "projected_installment"
            ]

            print()
            print(
                f"    REAIS...........: {reais}"
            )

            print(
                f"    PROJECOES.......: {projecoes}"
            )

        else:
            ids = [
                row["id"]
                for row in linhas
            ]

            print()
            print(
                f"    REAIS DUPLICADOS: {ids}"
            )

    print()
    print("=" * 100)
    print("RESUMO")
    print("=" * 100)

    print(
        f"Somente projecoes : "
        f"{totais['SOMENTE PROJECOES']}"
    )

    print(
        f"Real + projecao   : "
        f"{totais['REAL + PROJECAO']}"
    )

    print(
        f"Somente reais     : "
        f"{totais['SOMENTE REAIS']}"
    )

    print()
    print(
        "NENHUMA ALTERACAO FOI REALIZADA."
    )
    print()

    conn.close()


if __name__ == "__main__":
    main()