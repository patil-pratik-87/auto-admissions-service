"""Private configuration for the PDF-to-facts module."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class FactsSettings:
    """Versioned limits and provider settings owned by the facts extractor."""

    max_unique_pdfs: int = 10
    max_total_bytes: int = 50 * 1024 * 1024
    max_file_bytes: int = 50 * 1024 * 1024
    max_total_pages: int = 100
    default_model: str = "gpt-5.4-mini"
    extraction_prompt_version: str = "application-facts/2.0"
    initial_max_output_tokens: int = 8_000
    retry_max_output_tokens: int = 16_000
    full_time_weekly_hours: int = 40
