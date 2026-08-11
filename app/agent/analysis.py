class FinancialAnalysis:

    @staticmethod
    def _period_key(record):
        quarter = record["quarter"].split()[-1]

        quarter_number = int(
            quarter.replace("Q", "")
        )

        return (
            record["fiscal_year"],
            quarter_number,
        )

    @staticmethod
    def analyze(records):

        if len(records) < 2:
            return []

        records = sorted(
            records,
            key=FinancialAnalysis._period_key
        )

        analyses = []

        for previous, current in zip(records, records[1:]):

            previous_year = previous["fiscal_year"]
            current_year = current["fiscal_year"]

            previous_quarter = int(
                previous["quarter"]
                .split()[-1]
                .replace("Q", "")
            )

            current_quarter = int(
                current["quarter"]
                .split()[-1]
                .replace("Q", "")
            )

            is_consecutive = (
                current_year == previous_year
                and current_quarter == previous_quarter + 1
            )

            if not is_consecutive:
                continue

            previous_value = previous["value"]
            current_value = current["value"]

            absolute_change = (
                current_value - previous_value
            )

            percentage_change = (
                (absolute_change / previous_value) * 100
                if previous_value != 0
                else None
            )

            if absolute_change > 0:
                direction = "increased"
            elif absolute_change < 0:
                direction = "decreased"
            else:
                direction = "unchanged"

            analyses.append(
                {
                    "from_period": previous["quarter"],
                    "to_period": current["quarter"],
                    "from_value": previous_value,
                    "to_value": current_value,
                    "absolute_change": absolute_change,
                    "percentage_change": percentage_change,
                    "direction": direction,
                    "from_source": previous["source_file"],
                    "to_source": current["source_file"],
                }
            )

        return analyses

    @staticmethod
    def analyze_revenue_drivers(
        previous_records,
        current_records
    ):
        """
        Calculate how each revenue category changed
        between two periods.
        """

        previous = {
            record["metric"]: record
            for record in previous_records
        }

        current = {
            record["metric"]: record
            for record in current_records
        }

        drivers = []

        for metric in current:

            if metric == "total_revenue":
                continue

            if metric not in previous:
                continue

            previous_value = previous[metric]["value"]
            current_value = current[metric]["value"]

            change = current_value - previous_value

            percentage_change = (
                (change / previous_value) * 100
                if previous_value != 0
                else None
            )

            drivers.append(
                {
                    "metric": metric,
                    "previous_value": previous_value,
                    "current_value": current_value,
                    "absolute_change": change,
                    "percentage_change": percentage_change,
                    "direction": (
                        "increased"
                        if change > 0
                        else "decreased"
                        if change < 0
                        else "unchanged"
                    ),
                }
            )

        drivers.sort(
            key=lambda x: abs(x["absolute_change"]),
            reverse=True
        )

        return drivers

    @staticmethod
    def calculate_contributions(drivers, total_change):
        """
        Calculate each revenue category's contribution
        to the total revenue change.
        """

        if total_change == 0:
            for driver in drivers:
                driver["contribution_percentage"] = 0
            return drivers

        for driver in drivers:

            driver["contribution_percentage"] = (
                driver["absolute_change"]
                / total_change
            ) * 100

        return drivers

    