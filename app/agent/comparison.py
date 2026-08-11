class FinancialComparison:

    @staticmethod
    def compare(results):
        """
        Compare two financial records.

        Returns absolute and percentage change.
        """

        if len(results) != 2:
            raise ValueError(
                "Comparison requires exactly two financial records."
            )

        first = results[0]
        second = results[1]

        first_value = first["value"]
        second_value = second["value"]

        absolute_change = second_value - first_value

        if first_value != 0:
            percentage_change = (
                absolute_change / first_value
            ) * 100
        else:
            percentage_change = None

        return {
            "first": first,
            "second": second,
            "absolute_change": absolute_change,
            "percentage_change": percentage_change,
        }