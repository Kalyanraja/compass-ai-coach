"""Settings loader (SYNTHETIC FIXTURE)."""

import configparser
from pathlib import Path

SETTINGS_PATH = Path(__file__).resolve().parent.parent / "config" / "settings.ini"


def load_settings(path=SETTINGS_PATH) -> dict:
    """Read config/settings.ini and return the [login] section as a dict."""
    parser = configparser.ConfigParser()
    parser.read(path, encoding="utf-8")
    return dict(parser["login"]) if parser.has_section("login") else {}
