import re


class FinancialQueryParser:

    METRIC_MAP = {
        "total net sales": "total_revenue",
        "net sales": "total_revenue",
        "total revenue": "total_revenue",
        "revenue": "total_revenue",
        "sales": "total_revenue",

        "iphone revenue": "iphone_revenue",
        "iphone": "iphone_revenue",

        "mac revenue": "mac_revenue",
        "mac": "mac_revenue",

        "ipad revenue": "ipad_revenue",
        "ipad": "ipad_revenue",

        "services revenue": "services_revenue",
        "services": "services_revenue",

        "wearables revenue": "wearables_home_accessories_revenue",
        "wearables": "wearables_home_accessories_revenue",
    }

    def parse(self, question: str) -> dict:
        text = question.lower()

        metric = self._extract_metric(text)
        periods = self._extract_periods(text)

        # Preserve the existing single-period interface
        fiscal_year = periods[0]["fiscal_year"] if periods else None
        quarter = periods[0]["quarter"] if periods else None

        return {
            "metric": metric,
            "fiscal_year": fiscal_year,
            "quarter": quarter,
            "periods": periods,
        }

    def _extract_metric(self, text: str):
        metrics = sorted(
            self.METRIC_MAP.keys(),
            key=len,
            reverse=True,
        )

        for keyword in metrics:
            if keyword in text:
                return self.METRIC_MAP[keyword]

        return None

    def _extract_periods(self, text: str):
        periods = []

        # Match:
        # Q1 FY23
        # Q2 FY24
        # FY23 Q3
        # Q1 FY2025
        # FY2025 Q1

        patterns = [
            r"\bq([1-4])\s*fy\s*(20\d{2}|\d{2})\b",
            r"\bfy\s*(20\d{2}|\d{2})\s*q([1-4])\b",
        ]

        for pattern_index, pattern in enumerate(patterns):

            for match in re.finditer(pattern, text):

                if pattern_index == 0:
                    quarter_number = int(match.group(1))
                    year_text = match.group(2)
                else:
                    year_text = match.group(1)
                    quarter_number = int(match.group(2))

                fiscal_year = int(year_text)

                if fiscal_year < 100:
                    fiscal_year += 2000

                period = {
                    "fiscal_year": fiscal_year,
                    "quarter": f"Q{quarter_number}",
                }

                if period not in periods:
                    periods.append(period)

        return periods