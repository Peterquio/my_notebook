import sqlite3
import shutil
from pathlib import Path
from datetime import datetime


DB_PATH = Path("user_data/users/default.db")  # ajuste se seu banco estiver em outro caminho

GRUPOS_PARA_MESCLAR = [
    {
        "nome": "Meia Umbreon",
        "grupo_correto": "1|shopee *shpstecnologia|2549|10|2026-02|occurrence:1|occurrence:1",
        "grupo_errado": "1|shopee *shpstecnologia|2549|10|2026-02|occurrence:1",
    },
    {
        "nome": "Meia Espeon",
        "grupo_correto": "1|shopee *shpstecnologia|2549|10|2026-02|occurrence:1|occurrence:2",
        "grupo_errado": "1|shopee *shpstecnologia|2549|10|2026-02|occurrence:2",
    },
]


def backup_db():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = DB_PATH.with_name(f"{DB_PATH.stem}_backup_corrigir_parcelas_{timestamp}{DB_PATH.suffix}")
    shutil.copy2(DB_PATH, backup_path)
    print(f"Backup criado em: {backup_path}")


def listar(conn, grupo_id):
    return conn.execute(
        """
        SELECT id, effective_description, billing_date, installment_number,
               installment_total, effective_amount_cents, source_type,
               installment_group_id
        FROM finance_credit_card_expenses
        WHERE installment_group_id = ?
        ORDER BY installment_number, billing_date, id
        """,
        (grupo_id,),
    ).fetchall()


def corrigir_grupo(conn, nome, grupo_correto, grupo_errado):
    print("\n" + "=" * 80)
    print(f"Corrigindo: {nome}")

    corretos = listar(conn, grupo_correto)
    errados = listar(conn, grupo_errado)

    print(f"Registros no grupo correto: {len(corretos)}")
    print(f"Registros no grupo errado:  {len(errados)}")

    ids_para_deletar = []

    for errado in errados:
        (
            errado_id,
            _desc,
            billing_date,
            installment_number,
            installment_total,
            amount,
            source_type,
            _gid,
        ) = errado

        duplicado = conn.execute(
            """
            SELECT id
            FROM finance_credit_card_expenses
            WHERE installment_group_id = ?
              AND billing_date = ?
              AND installment_number = ?
              AND installment_total = ?
              AND effective_amount_cents = ?
            LIMIT 1
            """,
            (
                grupo_correto,
                billing_date,
                installment_number,
                installment_total,
                amount,
            ),
        ).fetchone()

        if duplicado and source_type == "projected_installment":
            ids_para_deletar.append(errado_id)

    print(f"Parcelas projetadas duplicadas para apagar: {ids_para_deletar}")

    if ids_para_deletar:
        placeholders = ",".join("?" for _ in ids_para_deletar)
        conn.execute(
            f"""
            DELETE FROM finance_credit_card_expenses
            WHERE id IN ({placeholders})
            """,
            ids_para_deletar,
        )

    conn.execute(
        """
        UPDATE finance_credit_card_expenses
        SET installment_group_id = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE installment_group_id = ?
        """,
        (grupo_correto, grupo_errado),
    )

    print("Grupo errado mesclado no grupo correto.")


def main():
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Banco não encontrado: {DB_PATH}")

    backup_db()

    conn = sqlite3.connect(DB_PATH)

    try:
        conn.execute("BEGIN")

        for item in GRUPOS_PARA_MESCLAR:
            corrigir_grupo(
                conn,
                item["nome"],
                item["grupo_correto"],
                item["grupo_errado"],
            )

        conn.commit()
        print("\nCorreção concluída com sucesso.")

    except Exception:
        conn.rollback()
        print("\nErro encontrado. Nada foi salvo.")
        raise

    finally:
        conn.close()


if __name__ == "__main__":
    main()