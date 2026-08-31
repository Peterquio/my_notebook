from pathlib import Path
import sqlite3
from datetime import datetime


DB_PATH = Path(
    r"C:\dev\Outros\my_notebook\user_data\users\default.db"
)

OUTPUT_PATH = DB_PATH.with_name(
    f"dump_banco_{datetime.now():%Y%m%d_%H%M%S}.txt"
)


def linha(tamanho=100):
    return "=" * tamanho


def escrever_tabela(
        arquivo,
        conexao,
        tabela: str,
) -> None:

    cursor = conexao.cursor()

    arquivo.write("\n")
    arquivo.write(linha())
    arquivo.write(f"\nTABELA: {tabela}\n")
    arquivo.write(linha())
    arquivo.write("\n")

    # =========================================================
    # ESTRUTURA
    # =========================================================

    arquivo.write("\nESTRUTURA\n")
    arquivo.write("-" * 100)
    arquivo.write("\n")

    cursor.execute(
        f'PRAGMA table_info("{tabela}")'
    )

    colunas = cursor.fetchall()

    for coluna in colunas:
        arquivo.write(
            f"{coluna['name']:<35} "
            f"{coluna['type']:<20} "
            f"nullable={'NO' if coluna['notnull'] else 'YES'} "
            f"default={coluna['dflt_value']} "
            f"pk={coluna['pk']}\n"
        )

    # =========================================================
    # ÍNDICES
    # =========================================================

    arquivo.write("\nÍNDICES\n")
    arquivo.write("-" * 100)
    arquivo.write("\n")

    cursor.execute(
        f'PRAGMA index_list("{tabela}")'
    )

    indices = cursor.fetchall()

    if not indices:
        arquivo.write("Nenhum índice.\n")

    for indice in indices:
        arquivo.write(
            f"{indice['name']} | "
            f"unique={indice['unique']} | "
            f"origin={indice['origin']}\n"
        )

        cursor.execute(
            f'PRAGMA index_info("{indice["name"]}")'
        )

        for coluna_indice in cursor.fetchall():
            arquivo.write(
                f"    - {coluna_indice['name']}\n"
            )

    # =========================================================
    # DADOS
    # =========================================================

    arquivo.write("\nDADOS\n")
    arquivo.write("-" * 100)
    arquivo.write("\n")

    cursor.execute(
        f'SELECT COUNT(*) AS total FROM "{tabela}"'
    )

    total = cursor.fetchone()["total"]

    arquivo.write(
        f"TOTAL DE REGISTROS: {total}\n\n"
    )

    if total == 0:
        return

    cursor.execute(
        f'SELECT * FROM "{tabela}"'
    )

    registros = cursor.fetchall()

    nomes_colunas = [
        descricao[0]
        for descricao in cursor.description
    ]

    for numero, registro in enumerate(
        registros,
        start=1,
    ):

        arquivo.write(
            f"\n--- REGISTRO {numero} ---\n"
        )

        for nome in nomes_colunas:

            valor = registro[nome]

            arquivo.write(
                f"{nome:<35}: {valor}\n"
            )


def escrever_resumo_cartoes(
        arquivo,
        conexao,
) -> None:

    cursor = conexao.cursor()

    arquivo.write("\n\n")
    arquivo.write(linha())
    arquivo.write("\nRESUMO DE FATURAS DE CARTÃO\n")
    arquivo.write(linha())
    arquivo.write("\n")

    cursor.execute(
        """
        SELECT
            c.id AS credit_card_id,
            c.name AS credit_card_name,
            i.id AS invoice_id,
            i.invoice_year,
            i.invoice_month,

            COUNT(e.id) AS total_lancamentos,

            COALESCE(
                SUM(
                    CASE
                        WHEN e.status != 'cancelled'
                        THEN e.effective_amount_cents
                        ELSE 0
                    END
                ),
                0
            ) AS total_expenses_cents

        FROM finance_credit_cards c

        LEFT JOIN finance_credit_card_invoices i
            ON i.credit_card_id = c.id

        LEFT JOIN finance_credit_card_expenses e
            ON e.invoice_id = i.id

        GROUP BY
            c.id,
            c.name,
            i.id,
            i.invoice_year,
            i.invoice_month

        ORDER BY
            c.id,
            i.invoice_year,
            i.invoice_month
        """
    )

    for row in cursor.fetchall():

        valor = (
            row["total_expenses_cents"]
            or 0
        ) / 100

        arquivo.write(
            f"Cartão {row['credit_card_id']} "
            f"| {row['credit_card_name']} "
            f"| Fatura {row['invoice_month']:02d}/"
            f"{row['invoice_year']} "
            f"| invoice_id={row['invoice_id']} "
            f"| lançamentos={row['total_lancamentos']} "
            f"| despesas=R$ {valor:.2f}\n"
        )


def escrever_resumo_parcelamentos(
        arquivo,
        conexao,
) -> None:

    cursor = conexao.cursor()

    arquivo.write("\n\n")
    arquivo.write(linha())
    arquivo.write("\nRESUMO DE INSTALLMENT GROUPS\n")
    arquivo.write(linha())
    arquivo.write("\n")

    cursor.execute(
        """
        SELECT
            installment_group_id,
            COUNT(*) AS total_registros,
            COUNT(
                CASE
                    WHEN status != 'cancelled'
                    THEN 1
                END
            ) AS ativos,

            MIN(installment_number) AS menor_parcela,
            MAX(installment_number) AS maior_parcela,
            MAX(installment_total) AS total_parcelas

        FROM finance_credit_card_expenses

        WHERE installment_group_id IS NOT NULL

        GROUP BY installment_group_id

        ORDER BY installment_group_id
        """
    )

    grupos = cursor.fetchall()

    for grupo in grupos:

        arquivo.write("\n")
        arquivo.write("-" * 100)
        arquivo.write("\n")

        arquivo.write(
            f"GROUP ID: "
            f"{grupo['installment_group_id']}\n"
        )

        arquivo.write(
            f"Registros: {grupo['total_registros']} "
            f"| Ativos: {grupo['ativos']} "
            f"| Parcelas: "
            f"{grupo['menor_parcela']}.."
            f"{grupo['maior_parcela']}"
            f"/{grupo['total_parcelas']}\n\n"
        )

        cursor.execute(
            """
            SELECT
                e.id,
                e.installment_number,
                e.installment_total,
                e.original_description,
                e.effective_description,
                e.original_purchase_date,
                e.effective_purchase_date,
                e.original_amount_cents,
                e.effective_amount_cents,
                e.source_type,
                e.source_reference,
                e.import_batch_id,
                e.created_by,
                e.status,
                e.notes,
                i.invoice_year,
                i.invoice_month

            FROM finance_credit_card_expenses e

            INNER JOIN finance_credit_card_invoices i
                ON i.id = e.invoice_id

            WHERE e.installment_group_id = ?

            ORDER BY
                e.installment_number,
                i.invoice_year,
                i.invoice_month,
                e.id
            """,
            (
                grupo["installment_group_id"],
            ),
        )

        for parcela in cursor.fetchall():

            valor = (
                parcela["effective_amount_cents"]
                or 0
            ) / 100

            arquivo.write(
                f"ID {parcela['id']:<5} "
                f"| {parcela['installment_number']:02d}/"
                f"{parcela['installment_total']:02d} "
                f"| FATURA "
                f"{parcela['invoice_month']:02d}/"
                f"{parcela['invoice_year']} "
                f"| DATA "
                f"{parcela['effective_purchase_date']} "
                f"| R$ {valor:.2f} "
                f"| source={parcela['source_type']} "
                f"| status={parcela['status']}\n"
            )

            arquivo.write(
                f"    original_desc : "
                f"{parcela['original_description']}\n"
            )

            arquivo.write(
                f"    effective_desc: "
                f"{parcela['effective_description']}\n"
            )

            arquivo.write(
                f"    original_date : "
                f"{parcela['original_purchase_date']}\n"
            )

            arquivo.write(
                f"    source_ref    : "
                f"{parcela['source_reference']}\n"
            )

            arquivo.write(
                f"    import_batch  : "
                f"{parcela['import_batch_id']}\n"
            )

            arquivo.write(
                f"    created_by    : "
                f"{parcela['created_by']}\n"
            )

            arquivo.write(
                f"    notes         : "
                f"{parcela['notes']}\n"
            )


def main():

    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"Banco não encontrado: {DB_PATH}"
        )

    conexao = sqlite3.connect(
        DB_PATH
    )

    conexao.row_factory = sqlite3.Row

    try:

        with OUTPUT_PATH.open(
            "w",
            encoding="utf-8",
        ) as arquivo:

            arquivo.write(
                "DUMP DIAGNÓSTICO DO MY NOTEBOOK\n"
            )

            arquivo.write(
                f"Banco: {DB_PATH}\n"
            )

            arquivo.write(
                f"Gerado em: "
                f"{datetime.now():%d/%m/%Y %H:%M:%S}\n"
            )

            cursor = conexao.cursor()

            cursor.execute(
                """
                SELECT name
                FROM sqlite_master
                WHERE type = 'table'
                  AND name NOT LIKE 'sqlite_%'
                ORDER BY name
                """
            )

            tabelas = [
                row["name"]
                for row in cursor.fetchall()
            ]

            arquivo.write(
                f"Tabelas encontradas: "
                f"{len(tabelas)}\n"
            )

            for tabela in tabelas:
                escrever_tabela(
                    arquivo=arquivo,
                    conexao=conexao,
                    tabela=tabela,
                )

            # =================================================
            # RESUMOS ESPECÍFICOS DO FINANCEIRO
            # =================================================

            if (
                "finance_credit_card_expenses"
                in tabelas
            ):

                escrever_resumo_parcelamentos(
                    arquivo=arquivo,
                    conexao=conexao,
                )

            if (
                "finance_credit_cards"
                in tabelas
                and
                "finance_credit_card_invoices"
                in tabelas
            ):

                escrever_resumo_cartoes(
                    arquivo=arquivo,
                    conexao=conexao,
                )

        print()
        print("=" * 80)
        print("DUMP GERADO COM SUCESSO")
        print("=" * 80)
        print(OUTPUT_PATH)

    finally:
        conexao.close()


if __name__ == "__main__":
    main()