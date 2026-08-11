import sqlite3

from app.database.financial_queries import FinancialDatabase


DB_PATH = "data/processed/financial.db"


def main():

    print("=" * 80)
    print("DATABASE COMPARISON TEST")
    print("=" * 80)

    # ---------------------------------------------
    # Direct SQL
    # ---------------------------------------------

    db = sqlite3.connect(DB_PATH)

    direct = db.execute(
        """
        SELECT
            company,
            fiscal_year,
            quarter,
            metric,
            value
        FROM financial_facts
        WHERE company = ?
          AND fiscal_year = ?
          AND quarter = ?
          AND metric = ?
        """,
        (
            "Apple",
            2003,
            "2003 Q1",
            "total_revenue",
        ),
    ).fetchall()

    db.close()

    print("\nDIRECT SQL:")
    print(f"Records: {len(direct)}")

    for row in direct:
        print(row)

    # ---------------------------------------------
    # FinancialDatabase class
    # ---------------------------------------------

    database = FinancialDatabase()

    print("\nFINANCIAL DATABASE CLASS:")
    print(f"Database path: {database.db_path}")

    results = database.get_metric(
        metric="total_revenue",
        fiscal_year=2023,
        quarter="Q1",
    )

    print(f"Records: {len(results)}")

    for result in results:
        print(result)


if __name__ == "__main__":
    main()