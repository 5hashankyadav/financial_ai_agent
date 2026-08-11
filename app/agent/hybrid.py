from app.agent.query_parser import FinancialQueryParser
from app.database.financial_queries import FinancialDatabase
from app.agent.analysis import FinancialAnalysis


class HybridContextBuilder:

    def __init__(self):
        self.parser = FinancialQueryParser()
        self.database = FinancialDatabase()
        self.analysis = FinancialAnalysis()

    def _get_periods_from_sources(self, rag_results):
        """
        Infer fiscal periods from retrieved PDF filenames.

        Example:
        FY25_Q3.pdf -> 2025 Q3
        FY24_Q2.pdf -> 2024 Q2
        """

        periods = set()

        for result in rag_results or []:

            source = result.get("source_file", "")

            # Expected format:
            # FY25_Q3.pdf

            name = source.upper()

            import re

            match = re.search(
                r"FY(\d{2,4})[_\s-]?Q([1-4])",
                name
            )

            if not match:
                continue

            year = int(match.group(1))

            if year < 100:
                year += 2000

            quarter = f"Q{match.group(2)}"

            periods.add(
                (year, quarter)
            )

        return sorted(periods)

    def _build_driver_analysis(
        self,
        first_period,
        second_period,
    ):
        """
        Build revenue driver analysis between two periods.
        """

        previous_records = (
            self.database.get_period_metrics(
                fiscal_year=first_period["fiscal_year"],
                quarter=first_period["quarter"],
            )
        )

        current_records = (
            self.database.get_period_metrics(
                fiscal_year=second_period["fiscal_year"],
                quarter=second_period["quarter"],
            )
        )

        if not previous_records or not current_records:
            return None

        previous_total = next(
            (
                r for r in previous_records
                if r["metric"] == "total_revenue"
            ),
            None,
        )

        current_total = next(
            (
                r for r in current_records
                if r["metric"] == "total_revenue"
            ),
            None,
        )

        if not previous_total or not current_total:
            return None

        drivers = (
            self.analysis.analyze_revenue_drivers(
                previous_records,
                current_records,
            )
        )

        total_change = (
            current_total["value"]
            - previous_total["value"]
        )

        drivers = (
            self.analysis.calculate_contributions(
                drivers,
                total_change,
            )
        )

        return {
            "from_period": previous_total["quarter"],
            "to_period": current_total["quarter"],
            "previous_total": previous_total["value"],
            "current_total": current_total["value"],
            "total_change": total_change,
            "drivers": drivers,
        }

    def build(self, question: str, rag_results=None):

        parsed = self.parser.parse(question)

        structured_data = []
        analysis_data = []

        # --------------------------------------------------
        # Case 1: Explicit periods
        # --------------------------------------------------

        if parsed["metric"] and parsed["periods"]:

            for period in parsed["periods"]:

                results = self.database.get_metric(
                    metric=parsed["metric"],
                    fiscal_year=period["fiscal_year"],
                    quarter=period["quarter"],
                )

                structured_data.extend(results)

            # Revenue comparison / driver analysis
            if (
                parsed["metric"] == "total_revenue"
                and len(parsed["periods"]) >= 2
            ):

                analysis = self._build_driver_analysis(
                    parsed["periods"][0],
                    parsed["periods"][1],
                )

                if analysis:
                    analysis_data.append(analysis)

        # --------------------------------------------------
        # Case 2: No explicit period
        # Use RAG sources to identify periods.
        # --------------------------------------------------

        elif parsed["metric"] and rag_results:

            source_files = {
                result["source_file"]
                for result in rag_results
            }

            all_results = self.database.get_metric(
                metric=parsed["metric"]
            )

            for result in all_results:

                if result["source_file"] in source_files:
                    structured_data.append(result)

            # --------------------------------------------------
            # Infer periods from retrieved documents
            # --------------------------------------------------

            if parsed["metric"] == "total_revenue":

                inferred_periods = (
                    self._get_periods_from_sources(
                        rag_results
                    )
                )

                # We need at least two periods.
                if len(inferred_periods) >= 2:

                    # Use the latest two periods represented
                    # by the retrieved documents.
                    inferred_periods = (
                        inferred_periods[-2:]
                    )

                    first_period = {
                        "fiscal_year":
                            inferred_periods[0][0],
                        "quarter":
                            inferred_periods[0][1],
                    }

                    second_period = {
                        "fiscal_year":
                            inferred_periods[1][0],
                        "quarter":
                            inferred_periods[1][1],
                    }

                    analysis = self._build_driver_analysis(
                        first_period,
                        second_period,
                    )

                    if analysis:
                        analysis_data.append(
                            analysis
                        )

        context_parts = []

        # --------------------------------------------------
        # Structured financial data
        # --------------------------------------------------

        if structured_data:

            context_parts.append(
                "STRUCTURED FINANCIAL DATA:"
            )

            for result in structured_data:

                context_parts.append(
                    f"""
Period: {result['quarter']}
Metric: {result['metric']}
Category: {result['category']}
Value: {result['value']}
Unit: {result['unit']}
Source: {result['source_file']}
"""
                )

        # --------------------------------------------------
        # Revenue driver analysis
        # --------------------------------------------------

        if analysis_data:

            context_parts.append(
                "\nREVENUE DRIVER ANALYSIS:"
            )

            for analysis in analysis_data:

                context_parts.append(
                    f"""
Period: {analysis['from_period']}
to: {analysis['to_period']}

Previous total revenue:
{analysis['previous_total']} USD_MILLIONS

Current total revenue:
{analysis['current_total']} USD_MILLIONS

Total change:
{analysis['total_change']} USD_MILLIONS
"""
                )

                for driver in analysis["drivers"]:

                    context_parts.append(
                        f"""
Metric: {driver['metric']}
Previous value: {driver['previous_value']} USD_MILLIONS
Current value: {driver['current_value']} USD_MILLIONS
Absolute change: {driver['absolute_change']} USD_MILLIONS
Percentage change: {driver['percentage_change']:.2f}%
Contribution to total change: {driver['contribution_percentage']:.2f}%
Direction: {driver['direction']}
"""
                    )

        # --------------------------------------------------
        # RAG document context
        # --------------------------------------------------

        if rag_results:

            context_parts.append(
                "\nDOCUMENT CONTEXT:"
            )

            for result in rag_results:

                context_parts.append(
                    f"""
Source: {result['source_file']}
Page: {result['page_number']}

{result['text']}
"""
                )

        return "\n".join(context_parts)