from core.database.database_manager import DatabaseManager


USERNAME = "default"


def apagar_ciclos_legados(
        username: str = USERNAME,
) -> None:

    database = DatabaseManager(
        username
    )

    conexao = database.get_connection()

    try:
        conexao.execute(
            "BEGIN"
        )

        # -------------------------------------------------
        # 1. Remove os saldos de abertura ligados a ciclos
        # -------------------------------------------------

        cursor = conexao.execute(
            """
            DELETE FROM finance_balance_cycle_account_openings
            """
        )

        print(
            "Aberturas de ciclo removidas:",
            cursor.rowcount,
        )

        # -------------------------------------------------
        # 2. Remove os ciclos
        # -------------------------------------------------

        cursor = conexao.execute(
            """
            DELETE FROM finance_balance_cycles
            """
        )

        print(
            "Ciclos removidos:",
            cursor.rowcount,
        )

        # -------------------------------------------------
        # 3. Validação
        # -------------------------------------------------

        cursor = conexao.execute(
            """
            SELECT COUNT(*) AS total
            FROM finance_balance_cycles
            """
        )

        total_ciclos = cursor.fetchone()["total"]

        cursor = conexao.execute(
            """
            SELECT COUNT(*) AS total
            FROM finance_balance_cycle_account_openings
            """
        )

        total_aberturas = cursor.fetchone()["total"]

        cursor = conexao.execute(
            """
            SELECT COUNT(*) AS total
            FROM finance_balance_income_entries
            WHERE cycle_id IS NOT NULL
            """
        )

        receitas_com_ciclo = cursor.fetchone()["total"]

        cursor = conexao.execute(
            """
            SELECT COUNT(*) AS total
            FROM finance_balance_commitments
            WHERE cycle_id IS NOT NULL
            """
        )

        compromissos_com_ciclo = cursor.fetchone()["total"]

        print()
        print("Validação:")
        print(
            f"finance_balance_cycles: {total_ciclos}"
        )
        print(
            "finance_balance_cycle_account_openings: "
            f"{total_aberturas}"
        )
        print(
            "Receitas com cycle_id: "
            f"{receitas_com_ciclo}"
        )
        print(
            "Compromissos com cycle_id: "
            f"{compromissos_com_ciclo}"
        )

        if (
                total_ciclos != 0
                or total_aberturas != 0
                or receitas_com_ciclo != 0
                or compromissos_com_ciclo != 0
        ):
            raise RuntimeError(
                "A limpeza de ciclos não ficou consistente."
            )

        conexao.commit()

        print()
        print(
            "Ciclos legados removidos com sucesso."
        )

    except Exception:
        conexao.rollback()

        print()
        print(
            "Erro encontrado. "
            "Nenhuma alteração foi mantida."
        )

        raise


if __name__ == "__main__":
    apagar_ciclos_legados()