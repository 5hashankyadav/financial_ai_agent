from app.database.financial_queries import FinancialDatabase


def main():

    db = FinancialDatabase()

    results = db.get_period_metrics(
        fiscal_year=2025,
        quarter="Q3",
    )

    print("=" * 80)
    print("PERIOD METRICS TEST")
    print("=" * 80)

    print(f"Records found: {len(results)}")

    for result in results:

        print(
            f"{result['metric']}: "
            f"{result['value']:,.0f} "
            f"{result['unit']}"
        )


if __name__ == "__main__":
    main()