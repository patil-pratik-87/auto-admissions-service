"""Run the admissions CLI with ``python -m app``."""

from app.cli import app


def main() -> None:
    """Invoke the shared Typer application."""
    app()


if __name__ == "__main__":
    main()
