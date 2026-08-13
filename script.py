from core.database.database_manager import DatabaseManager


USERNAME = "default"


def migrar() -> None:
    database = DatabaseManager(USERNAME)
    conexao = database.get_connection()
    cursor = conexao.cursor()

    print("=" * 70)
    print("MIGRATION - REMOÇÃO DOS CICLOS FINANCEIROS")
    print("=" * 70)

    cursor.execute("PRAGMA foreign_keys = OFF")

    try:
        conexao.execute("BEGIN")

        # =====================================================
        # PRESERVA SEQUÊNCIAS AUTOINCREMENT
        # =====================================================

        cursor.execute(
            """
            SELECT seq
            FROM sqlite_sequence
            WHERE name = 'finance_balance_income_entries'
            """
        )
        row = cursor.fetchone()
        income_sequence = row["seq"] if row else None

        cursor.execute(
            """
            SELECT seq
            FROM sqlite_sequence
            WHERE name = 'finance_balance_commitments'
            """
        )
        row = cursor.fetchone()
        commitment_sequence = row["seq"] if row else None

        # =====================================================
        # RECEITAS
        # =====================================================

        print("Migrando finance_balance_income_entries...")

        cursor.execute(
            """
            ALTER TABLE finance_balance_income_entries
            RENAME TO finance_balance_income_entries_old
            """
        )

        cursor.execute(
            """
            CREATE TABLE finance_balance_income_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                account_id INTEGER,
                category_id INTEGER,
                external_reference TEXT,
                description TEXT NOT NULL,

                expected_amount_cents INTEGER NOT NULL DEFAULT 0,
                actual_amount_cents INTEGER,

                expected_date TEXT NOT NULL,
                received_date TEXT,

                status TEXT NOT NULL DEFAULT 'expected',

                commitment_origin TEXT NOT NULL DEFAULT 'manual',
                projection_type TEXT NOT NULL DEFAULT 'real',

                is_recurring INTEGER NOT NULL DEFAULT 0,
                notes TEXT,

                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (account_id)
                    REFERENCES finance_balance_accounts(id),

                FOREIGN KEY (category_id)
                    REFERENCES finance_categories(id)
            )
            """
        )

        cursor.execute(
            """
            INSERT INTO finance_balance_income_entries (
                id,
                account_id,
                category_id,
                external_reference,
                description,
                expected_amount_cents,
                actual_amount_cents,
                expected_date,
                received_date,
                status,
                commitment_origin,
                projection_type,
                is_recurring,
                notes,
                created_at,
                updated_at
            )
            SELECT
                id,
                account_id,
                category_id,
                external_reference,
                description,
                expected_amount_cents,
                actual_amount_cents,
                expected_date,
                received_date,
                status,
                commitment_origin,
                projection_type,
                is_recurring,
                notes,
                created_at,
                updated_at
            FROM finance_balance_income_entries_old
            """
        )

        cursor.execute(
            """
            DROP TABLE finance_balance_income_entries_old
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_finance_balance_income_entries_category_id
            ON finance_balance_income_entries(category_id)
            """
        )

        # =====================================================
        # COMPROMISSOS
        # =====================================================

        print("Migrando finance_balance_commitments...")

        cursor.execute(
            """
            ALTER TABLE finance_balance_commitments
            RENAME TO finance_balance_commitments_old
            """
        )

        cursor.execute(
            """
            CREATE TABLE finance_balance_commitments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                description TEXT NOT NULL,

                expected_amount_cents INTEGER NOT NULL DEFAULT 0,
                actual_amount_cents INTEGER,

                due_date TEXT NOT NULL,
                paid_date TEXT,

                payment_type TEXT NOT NULL DEFAULT 'bank_account',

                account_id INTEGER,
                credit_card_id INTEGER,
                category_id INTEGER,

                external_reference TEXT,

                status TEXT NOT NULL DEFAULT 'expected',

                commitment_origin TEXT NOT NULL DEFAULT 'manual',
                projection_type TEXT NOT NULL DEFAULT 'real',

                is_recurring INTEGER NOT NULL DEFAULT 0,
                notes TEXT,

                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (account_id)
                    REFERENCES finance_balance_accounts(id),

                FOREIGN KEY (credit_card_id)
                    REFERENCES finance_credit_cards(id),

                FOREIGN KEY (category_id)
                    REFERENCES finance_categories(id)
            )
            """
        )

        cursor.execute(
            """
            INSERT INTO finance_balance_commitments (
                id,
                description,
                expected_amount_cents,
                actual_amount_cents,
                due_date,
                paid_date,
                payment_type,
                account_id,
                credit_card_id,
                category_id,
                external_reference,
                status,
                commitment_origin,
                projection_type,
                is_recurring,
                notes,
                created_at,
                updated_at
            )
            SELECT
                id,
                description,
                expected_amount_cents,
                actual_amount_cents,
                due_date,
                paid_date,
                payment_type,
                account_id,
                credit_card_id,
                category_id,
                external_reference,
                status,
                commitment_origin,
                projection_type,
                is_recurring,
                notes,
                created_at,
                updated_at
            FROM finance_balance_commitments_old
            """
        )

        cursor.execute(
            """
            DROP TABLE finance_balance_commitments_old
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_finance_balance_commitments_category_id
            ON finance_balance_commitments(category_id)
            """
        )

        # =====================================================
        # RESTAURA SEQUÊNCIAS
        # =====================================================

        if income_sequence is not None:
            cursor.execute(
                """
                UPDATE sqlite_sequence
                SET seq = ?
                WHERE name = 'finance_balance_income_entries'
                """,
                (income_sequence,),
            )

        if commitment_sequence is not None:
            cursor.execute(
                """
                UPDATE sqlite_sequence
                SET seq = ?
                WHERE name = 'finance_balance_commitments'
                """,
                (commitment_sequence,),
            )

        # =====================================================
        # EXTERMINA CICLOS
        # =====================================================

        print("Removendo finance_balance_cycle_account_openings...")

        cursor.execute(
            """
            DROP TABLE IF EXISTS finance_balance_cycle_account_openings
            """
        )

        print("Removendo finance_balance_cycles...")

        cursor.execute(
            """
            DROP TABLE IF EXISTS finance_balance_cycles
            """
        )

        conexao.commit()

        print()
        print("=" * 70)
        print("CICLOCÍDIO DO BANCO CONCLUÍDO COM SUCESSO 👹")
        print("=" * 70)

    except Exception:
        conexao.rollback()

        print()
        print("=" * 70)
        print("ERRO NA MIGRATION - ALTERAÇÕES REVERTIDAS")
        print("=" * 70)

        raise

    finally:
        cursor.execute("PRAGMA foreign_keys = ON")


if __name__ == "__main__":
    migrar()