import sqlite3


DB_PATH = "data/processed/financial.db"


def main():
    db = sqlite3.connect(DB_PATH)
    cursor = db.cursor()

    tables = cursor.execute(
        "SELECT name FROM sqlite_master "
        "WHERE type='table' ORDER BY name"
    ).fetchall()

    print("TABLES:")
    for table in tables:
        print(f"- {table[0]}")

    print("\nSCHEMAS:")

    for table in tables:
        table_name = table[0]

        print(f"\n[{table_name}]")

        columns = cursor.execute(
            f'PRAGMA table_info("{table_name}")'
        ).fetchall()

        for column in columns:
            print(column)

    db.close()


if __name__ == "__main__":
    main()