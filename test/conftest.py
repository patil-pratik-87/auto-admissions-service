"""Test-wide isolation from developer-local configuration."""

from collections.abc import Iterator

import pytest

from app.bootstrap import AdmissionsSettings


@pytest.fixture(autouse=True)
def isolate_dotenv(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """Keep a developer's local .env out of every test run."""
    monkeypatch.setitem(AdmissionsSettings.model_config, "env_file", None)
    yield
