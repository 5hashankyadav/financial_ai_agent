from app.database.financial_queries import FinancialDatabase
from app.agent.analysis import FinancialAnalysis


def main():

    db = FinancialDatabase()

    records = db.get_metric(
        metric="total_revenue"
    )

    print("=" * 80)
    print("FINANCIAL ANALYSIS TEST")
    print("=" * 80)

    print(f"Records found: {len(records)}")

    analyses = FinancialAnalysis.analyze(records)

    for analysis in analyses:

        print()
        print(
            f"{analysis['from_period']} → "
            f"{analysis['to_period']}"
        )

        print(
            f"Revenue: "
            f"${analysis['from_value']:,.0f}M → "
            f"${analysis['to_value']:,.0f}M"
        )

        print(
            f"Change: "
            f"${analysis['absolute_change']:,.0f}M"
        )

        if analysis["percentage_change"] is not None:

            print(
                f"Percentage change: "
                f"{analysis['percentage_change']:.2f}%"
            )

        print(
            f"Direction: "
            f"{analysis['direction']}"
        )


if __name__ == "__main__":
    main()