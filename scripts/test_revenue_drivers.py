from app.database.financial_queries import FinancialDatabase
from app.agent.analysis import FinancialAnalysis


def main():

    db = FinancialDatabase()

    previous = db.get_period_metrics(
        fiscal_year=2025,
        quarter="Q2",
    )

    current = db.get_period_metrics(
        fiscal_year=2025,
        quarter="Q3",
    )

    print("=" * 80)
    print("REVENUE DRIVER ANALYSIS")
    print("=" * 80)

    print()
    print("FY2025 Q2 → FY2025 Q3")

    total_previous = next(
        r for r in previous
        if r["metric"] == "total_revenue"
    )

    total_current = next(
        r for r in current
        if r["metric"] == "total_revenue"
    )

    total_change = (
        total_current["value"]
        - total_previous["value"]
    )

    total_percentage = (
        total_change
        / total_previous["value"]
    ) * 100

    print(
        f"\nTotal revenue:"
        f" ${total_previous['value']:,.0f}M"
        f" → ${total_current['value']:,.0f}M"
    )

    print(
        f"Change: ${total_change:,.0f}M"
        f" ({total_percentage:.2f}%)"
    )

    print("\nRevenue drivers:")

    drivers = FinancialAnalysis.analyze_revenue_drivers(
        previous,
        current
    )

    drivers = FinancialAnalysis.calculate_contributions(
        drivers,
        total_change
        )

    for driver in drivers:

        print()

        print(
            f"{driver['metric']}"
        )

        print(
            f"  "
            f"${driver['previous_value']:,.0f}M"
            f" → "
            f"${driver['current_value']:,.0f}M"
        )

        print(
            f"  Change: "
            f"${driver['absolute_change']:,.0f}M"
        )

        if driver["percentage_change"] is not None:

            print(
                f"  Percentage: "
                f"{driver['percentage_change']:.2f}%"
            )

        print(
            f" Contribution to total change: "
            f"{driver['contribution_percentage']:.2f}%"
        )

        print(
            f"  Direction: "
            f"{driver['direction']}"
        )


if __name__ == "__main__":
    main()