"""Celery application for Scorpius Reporting System.

Heavy operations (e.g., PDF generation) are delegated here so HTTP threads aren't blocked.
"""

from __future__ import annotations

import logging
import os

from celery import Celery

logger = logging.getLogger(__name__)

BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
BACKEND_URL = os.getenv("CELERY_RESULT_BACKEND", BROKER_URL)

celery_app = Celery("scorpius_reporting", broker=BROKER_URL, backend=BACKEND_URL)

# --- Task definitions --------------------------------------------------------


@celery_app.task(bind=True, name="reports.generate_pdf")
def generate_pdf(self, job_id: str, scan_id: str, output_path: str) -> str:  # type: ignore
    """Generate PDF report via PDFReporter.

    Args:
        job_id: Report job identifier.
        scan_id: Associated scan identifier.
        output_path: Absolute path where PDF should be stored.

    Returns: output path (string)
    """
    try:
        from datetime import datetime
        from pathlib import Path

        from reporting.models import ReportFormat  # noqa: WPS433

        # Lazy import heavy deps to avoid importing in web workers
        from reporting.reporters.pdf_writer import PDFReporter  # noqa: WPS433

        reporter = PDFReporter()
        reporter.register_filters()  # ensure Jinja filters

        context = {
            "report_id": job_id,
            "scan_id": scan_id,
            "generated_at": datetime.utcnow().isoformat(),
            "findings": [],
        }

        path_obj = Path(output_path)
        path_obj.parent.mkdir(parents=True, exist_ok=True)

        # Generate PDF (sync function, could be async but Celery task is sync)
        reporter.generate_pdf(
            context=context,
            output_path=path_obj,
            include_charts=True,
            watermark="SCORPIUS CONFIDENTIAL",
            sign_pdf=False,
        )

        logger.info("PDF report generated at %s", output_path)
        return str(path_obj)
    except Exception as exc:  # pragma: no cover – want to see full trace in worker logs
        logger.exception("PDF generation failed: %s", exc)
        raise
