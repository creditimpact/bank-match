"""Bank statement parser interface."""
from __future__ import annotations

from typing import Dict


def parse(pdf_bytes: bytes) -> Dict[str, str]:
    """Parse *pdf_bytes* and return structured data.

    TODO:
        * Integrate OCR/ML models to extract transactions and balances.
        * Support multiple bank formats and error handling.
    """
    # Placeholder implementation
    return {}
