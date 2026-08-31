import csv
import re
import sqlite3
import unicodedata
from collections import defaultdict
from datetime import date
from pathlib import Path


DB_PATH = Path(
    r"C:\dev\Outros\my_notebook\user_data\users\default.db"
)

CSV_PATH = Path(
    r"C:\dev\Outros\my_notebook\Nubank_2026-09-10.csv"
)

INVOICE_YEAR = 2026
INVOICE_MONTH = 9


# ======================================================================
# UTILITÁRIOS
# ======================================================================

def normalizar_texto(valor: str | None) -> str:
    if not valor:
        return ""

    valor = unicodedata.normalize("NFKC", valor)
    valor = valor.lower().strip()
    valor = re.sub(r"\s+", " ", valor)

    return valor


def valor_para_centavos(valor: str) -> int:
    valor = valor.strip()
    valor = valor.replace("R$", "")
    valor = valor.replace(" ", "")
    valor = valor.replace(".", "")
    valor = valor.replace(",", ".")

    return round(float(valor) * 100)


def extrair_parcela(titulo: str):
    padroes = [
        r"parcela\s+(\d+)\s*/\s*(\d+)",
        r"\s-\s*(\d+)\s*/\s*(\d+)$",
    ]

    titulo_norm = normalizar_texto(titulo)

    for padrao in padroes:
        match = re.search(
            padrao,
            titulo_norm,
            flags=re.IGNORECASE,
        )

        if match:
            return (
                int(match.group(1)),
                int(match.group(2)),
            )

    return None, None


def eh_ajuste(titulo: str) -> bool:
    titulo = normalizar_texto(titulo)

    return (
        titulo.startswith("pagamento recebido")
        or titulo.startswith("desconto antecip")
        or titulo.startswith(
            "desconto de antecipação"
        )
    )


def chave_csv(row: dict):
    titulo = row["title"]
    valor = valor_para_centavos(row["amount"])

    parcela_numero, parcela_total = (
        extrair_parcela(titulo)
    )

    return (
        normalizar_texto(titulo),
        valor,
        parcela_numero,
        parcela_total,
    )


def chave_db(row: sqlite3.Row):
    titulo = (
        row["original_description"]
        or row["source_reference"]
        or row["effective_description"]
    )

    return (
        normalizar_texto(titulo),
        int(row["original_amount_cents"]),
        (
            int(row["installment_number"])
            if row["installment_number"] is not None
            else None
        ),
        (
            int(row["installment_total"])
            if row["installment_total"] is not None
            else None
        ),
    )


# ======================================================================
# CSV
# ======================================================================

def carregar_csv():
    grupos = defaultdict(list)

    with CSV_PATH.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as arquivo:

        reader = csv.DictReader(arquivo)

        for row in reader:
            titulo = row["title"]

            if eh_ajuste(titulo):
                continue

            valor = valor_para_centavos(
                row["amount"]
            )

            if valor <= 0:
                continue

            grupos[chave_csv(row)].append(
                date.fromisoformat(row["date"])
            )

    return grupos


# ======================================================================
# BANCO
# ======================================================================

def carregar_lancamentos_db(conn):
    rows = conn.execute(
        """
        SELECT
            e.id,
            e.invoice_id,

            e.original_description,
            e.effective_description,
            e.source_reference,

            e.original_purchase_date,
            e.effective_purchase_date,

            e.original_amount_cents,
            e.effective_amount_cents,

            e.installment_number,
            e.installment_total,
            e.installment_group_id,

            e.source_type,
            e.status,

            i.invoice_year,
            i.invoice_month

        FROM finance_credit_card_expenses e

        INNER JOIN finance_credit_card_invoices i
            ON i.id = e.invoice_id

        WHERE i.invoice_year = ?
          AND i.invoice_month = ?
          AND e.status != 'cancelled'
          AND e.source_type = 'Nubank'

        ORDER BY e.id
        """,
        (
            INVOICE_YEAR,
            INVOICE_MONTH,
        ),
    ).fetchall()

    grupos = defaultdict(list)

    for row in rows:
        grupos[chave_db(row)].append(row)

    return grupos


# ======================================================================
# ESCOLHA DAS OCORRÊNCIAS QUE DEVEM PERMANECER
# ======================================================================

def distancia_dias(data_a: str, data_b: date):
    data_a = date.fromisoformat(data_a)

    return abs(
        (data_a - data_b).days
    )


def escolher_para_manter(
        db_rows,
        csv_dates,
):
    restantes = list(db_rows)
    manter = []

    #
    # Para cada ocorrência atual do CSV,
    # escolhemos a melhor linha existente.
    #
    # Prioridade:
    #
    # 1. data original exatamente igual
    # 2. menor distância de dias
    # 3. ID mais antigo
    #
    for csv_date in csv_dates:

        if not restantes:
            break

        escolhido = min(
            restantes,
            key=lambda row: (
                distancia_dias(
                    row["original_purchase_date"],
                    csv_date,
                ),
                row["id"],
            ),
        )

        manter.append(escolhido)
        restantes.remove(escolhido)

    return manter, restantes


# ======================================================================
# LIMPEZA DA FATURA
# ======================================================================

def normalizar_fatura(
        conn,
        grupos_csv,
        grupos_db,
):
    deletados = []

    todas_chaves = set(grupos_db.keys())

    for chave in sorted(
        todas_chaves,
        key=str,
    ):
        db_rows = grupos_db[chave]
        csv_dates = grupos_csv.get(chave, [])

        quantidade_db = len(db_rows)
        quantidade_csv = len(csv_dates)

        #
        # CSV não conhece esse lançamento.
        #
        # NÃO apagamos automaticamente.
        #
        # Pode ser descrição antiga/editada,
        # lançamento manual ou alguma situação
        # que merece análise.
        #
        if quantidade_csv == 0:
            continue

        #
        # Banco possui quantidade compatível.
        #
        if quantidade_db <= quantidade_csv:
            continue

        manter, apagar = escolher_para_manter(
            db_rows=db_rows,
            csv_dates=csv_dates,
        )

        print()
        print("-" * 100)

        exemplo = db_rows[0]

        print(
            exemplo["original_description"]
        )

        print(
            f"CSV   : {quantidade_csv}"
        )

        print(
            f"Banco : {quantidade_db}"
        )

        print()

        for row in manter:
            print(
                f"MANTÉM  ID {row['id']} | "
                f"{row['original_purchase_date']} | "
                f"R$ {row['original_amount_cents'] / 100:.2f}"
            )

        for row in apagar:

            print(
                f"DELETE  ID {row['id']} | "
                f"{row['original_purchase_date']} | "
                f"R$ {row['original_amount_cents'] / 100:.2f}"
            )

            conn.execute(
                """
                DELETE
                FROM finance_credit_card_expenses
                WHERE id = ?
                """,
                (row["id"],),
            )

            deletados.append(row["id"])

    return deletados


# ======================================================================
# LIMPEZA FÍSICA DOS PARCELAMENTOS CANCELADOS REDUNDANTES
# ======================================================================

def limpar_projecoes_canceladas_redundantes(
        conn,
):
    rows = conn.execute(
        """
        SELECT
            cancelada.id,
            cancelada.installment_group_id,
            cancelada.installment_number,
            cancelada.source_type

        FROM finance_credit_card_expenses cancelada

        WHERE cancelada.status = 'cancelled'

          AND cancelada.installment_group_id IS NOT NULL

          AND EXISTS (
              SELECT 1
              FROM finance_credit_card_expenses ativa

              WHERE ativa.installment_group_id =
                    cancelada.installment_group_id

                AND ativa.installment_number =
                    cancelada.installment_number

                AND ativa.status != 'cancelled'
          )

        ORDER BY
            cancelada.installment_group_id,
            cancelada.installment_number,
            cancelada.id
        """
    ).fetchall()

    print()
    print("=" * 100)
    print(
        "CANCELADOS REDUNDANTES DE INSTALLMENT GROUPS"
    )
    print("=" * 100)

    for row in rows:
        print(
            f"DELETE ID {row['id']} | "
            f"{row['installment_group_id']} | "
            f"parcela {row['installment_number']} | "
            f"{row['source_type']}"
        )

        conn.execute(
            """
            DELETE
            FROM finance_credit_card_expenses
            WHERE id = ?
            """,
            (row["id"],),
        )

    return len(rows)


# ======================================================================
# MAIN
# ======================================================================

def main():
    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"Banco não encontrado:\n{DB_PATH}"
        )

    if not CSV_PATH.exists():
        raise FileNotFoundError(
            f"CSV não encontrado:\n{CSV_PATH}"
        )

    print("=" * 100)
    print("NORMALIZAÇÃO DA FATURA")
    print("=" * 100)

    print()
    print(f"Banco : {DB_PATH}")
    print(f"CSV   : {CSV_PATH}")

    grupos_csv = carregar_csv()

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    try:
        grupos_db = carregar_lancamentos_db(
            conn
        )

        conn.execute("BEGIN")

        deletados_fatura = normalizar_fatura(
            conn=conn,
            grupos_csv=grupos_csv,
            grupos_db=grupos_db,
        )

        total_cancelados = (
            limpar_projecoes_canceladas_redundantes(
                conn
            )
        )

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()

    print()
    print("=" * 100)
    print("NORMALIZAÇÃO CONCLUÍDA")
    print("=" * 100)

    print(
        f"Lançamentos redundantes da fatura deletados: "
        f"{len(deletados_fatura)}"
    )

    print(
        f"Registros cancelados redundantes deletados: "
        f"{total_cancelados}"
    )

    if deletados_fatura:
        print(
            "IDs removidos da fatura:",
            ", ".join(
                str(x)
                for x in deletados_fatura
            ),
        )


if __name__ == "__main__":
    main()