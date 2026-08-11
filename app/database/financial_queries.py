import sqlite3
from pathlib import Path

from app.config import settings
from app.security.rbac import can_access_metric


DB_PATH = settings.DATABASE_PATH


class FinancialDatabase:

    def __init__(self, db_path=DB_PATH):
        self.db_path = Path(db_path)

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def get_metric(
        self,
        metric,
        fiscal_year=None,
        quarter=None,
        category=None,
        company="Apple",
        role="CEO",
    ):
        """
        Retrieve financial metric data while enforcing
        role-based access control.
        """

        # --------------------------------------------------
        # RBAC
        # --------------------------------------------------

        if not can_access_metric(role, metric):
            return []

        # --------------------------------------------------
        # Base query
        # --------------------------------------------------

        query = """
            SELECT
                company,
                fiscal_year,
                quarter,
                metric,
                category,
                value,
                unit,
                source_file,
                source_sheet,
                source_row
            FROM financial_facts
            WHERE company = ?
              AND metric = ?
        """

        params = [
            company,
            metric,
        ]

        # --------------------------------------------------
        # Fiscal year
        # --------------------------------------------------

        if fiscal_year is not None:

            db_year = int(fiscal_year)

            query += """
                AND fiscal_year = ?
            """

            params.append(db_year)

        # --------------------------------------------------
        # Quarter
        # --------------------------------------------------

        if quarter is not None:

            if fiscal_year is not None:
                db_quarter = f"{db_year} {quarter}"
            else:
                db_quarter = quarter

            query += """
                AND quarter = ?
            """

            params.append(db_quarter)

        # --------------------------------------------------
        # Category
        # --------------------------------------------------

        if category is not None:

            query += """
                AND category = ?
            """

            params.append(category)

        # --------------------------------------------------
        # Chronological ordering
        # --------------------------------------------------

        query += """
            ORDER BY fiscal_year, quarter
        """

        with self._connect() as conn:

            rows = conn.execute(
                query,
                tuple(params)
            ).fetchall()

        columns = [
            "company",
            "fiscal_year",
            "quarter",
            "metric",
            "category",
            "value",
            "unit",
            "source_file",
            "source_sheet",
            "source_row",
        ]

        return [
            dict(zip(columns, row))
            for row in rows
        ]

    def get_period_metrics(
        self,
        fiscal_year,
        quarter,
        company="Apple",
        role="CEO",
    ):
        """
        Get all financial metrics for a specific fiscal
        period while enforcing role-based access control.
        """

        db_year = int(fiscal_year)

        db_quarter = f"{db_year} {quarter}"

        query = """
            SELECT
                company,
                fiscal_year,
                quarter,
                metric,
                category,
                value,
                unit,
                source_file,
                source_sheet,
                source_row
            FROM financial_facts
            WHERE company = ?
              AND fiscal_year = ?
              AND quarter = ?
        """

        params = [
            company,
            db_year,
            db_quarter,
        ]

        with self._connect() as conn:

            rows = conn.execute(
                query,
                tuple(params)
            ).fetchall()

        columns = [
            "company",
            "fiscal_year",
            "quarter",
            "metric",
            "category",
            "value",
            "unit",
            "source_file",
            "source_sheet",
            "source_row",
        ]

        results = [
            dict(zip(columns, row))
            for row in rows
        ]

        # --------------------------------------------------
        # RBAC filtering
        # --------------------------------------------------

        return [
            result
            for result in results
            if can_access_metric(
                role,
                result["metric"],
            )
        ]