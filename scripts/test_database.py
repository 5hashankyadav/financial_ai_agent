from app.database.financial_queries import FinancialDatabase


def main():

    db = FinancialDatabase()

    results = db.get_metric(
        metric="total_revenue",
        fiscal_year=2023,
        quarter="Q1",
    )

    print("=" * 70)
    print("DATABASE QUERY TEST")
    print("=" * 70)

    print(f"Records found: {len(results)}")

    for result in results:
        print()
        print(result)


if __name__ == "__main__":
    main()