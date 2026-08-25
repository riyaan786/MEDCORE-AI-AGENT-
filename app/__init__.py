"""MedCore AI - Hospital Operations Assistant."""

import logging
import logging.config
from pathlib import Path


def _setup_logging():
    """Configure logging from logging.toml on first import."""
    config_path = (
        Path(__file__).parent.parent
        / "logging.toml"
    )
    try:
        logging.config.fileConfig(
            config_path,
            disable_existing_loggers=False,
        )
    except (FileNotFoundError, Exception):
        logging.basicConfig(
            level=logging.INFO,
            format=(
                "%(asctime)s | %(levelname)-8s "
                "| %(name)s | %(message)s"
            ),
        )


_setup_logging()
