import sqlite3
from pathlib import Path
from collections import defaultdict


DB_PATH = Path(
    r"C:\dev\Outros\my_notebook\user_data\users\default.db"
)


def carregar_duplicidades_projetadas(
        conn: sqlite3.Connection,
) -> dict[tuple[str, int], list[sqlite3.Row]]:

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            id,
            installment_group_id,
            installment_number,
            source_type,
            status
        FROM finance_credit_card_expenses
        WHERE installment_group_id IS NOT NULL
          AND status != 'cancelled'
        ORDER BY
            installment_group_id,
            installment_number,
            id
        """
    )

    grupos = defaultdict(list)

    for row in cursor.fetchall():
        chave = (
            row["installment_group_id"],
            int(row["installment_number"]),
        )

        grupos[chave].append(row)

    resultado = {}

    for chave, linhas in grupos.items():
        if len(linhas) <= 1:
            continue

        somente_projecoes = all(
            linha["source_type"] == "projected_installment"
            for linha in linhas
        )

        if not somente_projecoes:
            continue

        resultado[chave] = linhas

    return resultado


def normalizar(
        conn: sqlite3.Connection,
) -> None:

    grupos = carregar_duplicidades_projetadas(
        conn
    )

    if not grupos:
        print()
        print("Nenhuma duplicidade projetada encontrada.")
        return

    total_grupos = 0
    total_cancelados = 0

    cursor = conn.cursor()

    print()
    print("=" * 100)
    print("NORMALIZACAO DE PROJECOES DUPLICADAS")
    print("=" * 100)

    try:
        conn.execute("BEGIN")

        for (
                installment_group_id,
                installment_number,
        ), linhas in grupos.items():

            manter = max(
                linhas,
                key=lambda linha: int(linha["id"]),
            )

            ids_cancelar = [
                int(linha["id"])
                for linha in linhas
                if int(linha["id"]) != int(manter["id"])
            ]

            if not ids_cancelar:
                continue

            placeholders = ",".join(
                "?"
                for _ in ids_cancelar
            )

            cursor.execute(
                f"""
                UPDATE finance_credit_card_expenses
                SET
                    status = 'cancelled',
                    updated_at = CURRENT_TIMESTAMP
                WHERE id IN ({placeholders})
                  AND source_type = 'projected_installment'
                  AND status != 'cancelled'
                """,
                ids_cancelar,
            )

            afetados = cursor.rowcount

            total_grupos += 1
            total_cancelados += afetados

            print()
            print("-" * 100)
            print(
                f"Grupo   : {installment_group_id}"
            )
            print(
                f"Parcela : {installment_number}"
            )
            print(
                f"KEEP    : {manter['id']}"
            )
            print(
                f"CANCEL  : {ids_cancelar}"
            )
            print(
                f"Afetados: {afetados}"
            )

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    print()
    print("=" * 100)
    print("RESUMO")
    print("=" * 100)

    print(
        f"Grupos normalizados : {total_grupos}"
    )

    print(
        f"Projecoes canceladas: {total_cancelados}"
    )

    print()
    print("NORMALIZACAO CONCLUIDA.")
    print()


def verificar_resultado(
        conn: sqlite3.Connection,
) -> None:

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            installment_group_id,
            installment_number,
            COUNT(*) AS total_ativos,
            GROUP_CONCAT(source_type) AS source_types
        FROM finance_credit_card_expenses
        WHERE installment_group_id IS NOT NULL
          AND status != 'cancelled'
        GROUP BY
            installment_group_id,
            installment_number
        HAVING COUNT(*) > 1
        ORDER BY
            installment_group_id,
            installment_number
        """
    )

    problemas = cursor.fetchall()

    print()
    print("=" * 100)
    print("VERIFICACAO POS-NORMALIZACAO")
    print("=" * 100)

    print(
        f"Duplicidades ativas restantes: "
        f"{len(problemas)}"
    )

    for row in problemas:
        print()
        print(
            f"Grupo   : "
            f"{row['installment_group_id']}"
        )
        print(
            f"Parcela : "
            f"{row['installment_number']}"
        )
        print(
            f"Ativos  : "
            f"{row['total_ativos']}"
        )
        print(
            f"Sources : "
            f"{row['source_types']}"
        )

    print()


def main() -> None:

    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"Banco nao encontrado em:\n{DB_PATH}"
        )

    conn = sqlite3.connect(
        DB_PATH
    )

    conn.row_factory = sqlite3.Row

    try:
        normalizar(
            conn
        )

        verificar_resultado(
            conn
        )

    finally:
        conn.close()


if __name__ == "__main__":
    main()