from app.agent.router import QueryRouter
from app.agent.query_parser import FinancialQueryParser
from app.agent.comparison import FinancialComparison
from app.database.financial_queries import FinancialDatabase
from app.rag.pipeline import FinancialRAG
from app.agent.hybrid import HybridContextBuilder

class FinancialAgent:

    def __init__(self):
        self.router = QueryRouter()
        self.parser = FinancialQueryParser()
        self.comparison = FinancialComparison()
        self.database = FinancialDatabase()
        self.rag = FinancialRAG()
        self.hybrid_builder = HybridContextBuilder()

    def ask(self, question: str):

        route = self.router.classify(question)

        if route == "structured":
            return self._structured_query(question)

        if route == "rag":
            return self._rag_query(question)

        if route == "hybrid":
            return self._hybrid_query(question)

        return {
            "answer": "I could not determine how to answer this question.",
            "route": route,
            "sources": [],
        }

    def _structured_query(self, question: str):

        parsed = self.parser.parse(question)

        if not parsed["metric"]:
            return {
                "answer": "I could not determine the financial metric.",
                "route": "structured",
                "sources": [],
            }

        periods = parsed["periods"]

        # --------------------------------------------------
        # Single-period query
        # --------------------------------------------------

        if len(periods) == 1:

            period = periods[0]

            results = self.database.get_metric(
                metric=parsed["metric"],
                fiscal_year=period["fiscal_year"],
                quarter=period["quarter"],
            )

            if not results:
                return {
                    "answer": (
                        "I could not find the requested financial "
                        "data in the database."
                    ),
                    "route": "structured",
                    "sources": [],
                }

            result = results[0]

            answer = self._format_single_result(
                result,
                parsed["metric"],
            )

            return {
                "answer": answer,
                "route": "structured",
                "sources": [
                    {
                        "source_file": result["source_file"],
                        "source_sheet": result["source_sheet"],
                        "source_row": result["source_row"],
                    }
                ],
            }

        # --------------------------------------------------
        # Multi-period comparison
        # --------------------------------------------------

        if len(periods) == 2:

            records = []

            for period in periods:

                results = self.database.get_metric(
                    metric=parsed["metric"],
                    fiscal_year=period["fiscal_year"],
                    quarter=period["quarter"],
                )

                if not results:
                    return {
                        "answer": (
                            f"I could not find data for "
                            f"FY{str(period['fiscal_year'])[-2:]} "
                            f"{period['quarter']}."
                        ),
                        "route": "structured",
                        "sources": [],
                    }

                records.append(results[0])

            comparison = self.comparison.compare(records)

            answer = self._format_comparison(
                comparison,
                parsed["metric"],
            )

            sources = []

            for record in records:
                sources.append(
                    {
                        "source_file": record["source_file"],
                        "source_sheet": record["source_sheet"],
                        "source_row": record["source_row"],
                    }
                )

            return {
                "answer": answer,
                "route": "structured",
                "sources": sources,
            }

        return {
            "answer": (
                "I currently support comparisons between "
                "two financial periods."
            ),
            "route": "structured",
            "sources": [],
        }

    def _rag_query(self, question: str):

        result = self.rag.ask(question)

        return {
            "answer": result["answer"],
            "route": "rag",
            "sources": result["sources"],
        }

    def _hybrid_query(self, question: str):

        # Retrieve PDF context without generating an answer
        rag_results = self.rag.retrieve(
            question,
            top_k=5
        )

        # Build combined SQLite + PDF context
        context = self.hybrid_builder.build(
            question,
            rag_results
        )

        if not context:
            return {
                "answer": "I could not find relevant financial information.",
                "route": "hybrid",
                "sources": [],
            }

        # Generate final grounded answer
        answer = self.rag.generate_answer(
            question,
            context
        )

        # Collect sources
        sources = []

        for result in rag_results:

            sources.append(
                {
                    "source_file": result["source_file"],
                    "page_number": result["page_number"],
                    "score": result["hybrid_score"],
                }
            )

        return {
            "answer": answer,
            "route": "hybrid",
            "sources": sources,
        }

    @staticmethod
    def _format_single_result(result, metric):

        metric_name = FinancialAgent._metric_name(metric)

        value = result["value"]

        if result["unit"] == "USD_MILLIONS":
            formatted_value = f"${value:,.0f} million"
        else:
            formatted_value = f"{value:,.2f} {result['unit']}"

        fiscal_year = result["fiscal_year"]
        quarter = result["quarter"].split()[-1]

        verb = "was" if metric == "total_revenue" else "was"

        return (
            f"Apple's {quarter} FY{str(fiscal_year)[-2:]} "
            f"{metric_name} {verb} {formatted_value}."
        )

    @staticmethod
    def _format_comparison(comparison, metric):

        metric_name = FinancialAgent._metric_name(metric)

        first = comparison["first"]
        second = comparison["second"]

        first_value = first["value"]
        second_value = second["value"]

        absolute_change = comparison["absolute_change"]
        percentage_change = comparison["percentage_change"]

        first_period = (
            f"{first['quarter'].split()[-1]} "
            f"FY{str(first['fiscal_year'])[-2:]}"
        )

        second_period = (
            f"{second['quarter'].split()[-1]} "
            f"FY{str(second['fiscal_year'])[-2:]}"
        )

        direction = "increased" if absolute_change >= 0 else "decreased"

        return (
            f"Apple's {metric_name} was "
            f"${first_value:,.0f} million in {first_period} "
            f"and ${second_value:,.0f} million in {second_period}. "
            f"It {direction} by "
            f"${abs(absolute_change):,.0f} million "
            f"({abs(percentage_change):.2f}%) over the period."
        )

    @staticmethod
    def _metric_name(metric):

        names = {
            "total_revenue": "total net sales",
            "iphone_revenue": "iPhone revenue",
            "mac_revenue": "Mac revenue",
            "ipad_revenue": "iPad revenue",
            "services_revenue": "Services revenue",
            "wearables_home_accessories_revenue":
                "Wearables, Home and Accessories revenue",
        }

        return names.get(metric, metric)