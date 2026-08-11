from app.database.financial_queries import FinancialDatabase
from app.agent.comparison import FinancialComparison


def main():

    db = FinancialDatabase()

    results = []

    results.extend(
        db.get_metric(
            metric="total_revenue",
            fiscal_year=2023,
            quarter="Q1",
        )
    )

    results.extend(
        db.get_metric(
            metric="total_revenue",
            fiscal_year=2025,
            quarter="Q1",
        )
    )

    print("=" * 80)
    print("COMPARISON TEST")
    print("=" * 80)

    print(f"Records found: {len(results)}")

    comparison = FinancialComparison.compare(results)

    first = comparison["first"]
    second = comparison["second"]

    print()
    print(
        f"{first['quarter']}: "
        f"${first['value']:,.0f} million"
    )

    print(
        f"{second['quarter']}: "
        f"${second['value']:,.0f} million"
    )

    print()
    print(
        f"Absolute change: "
        f"${comparison['absolute_change']:,.0f} million"
    )

    print(
        f"Percentage change: "
        f"{comparison['percentage_change']:.2f}%"
    )


if __name__ == "__main__":
    main()