# tests/test_config.py
import os
from pathlib import Path
from unittest.mock import patch

import pytest

from ghome.config import get_config_dir, get_client_secret_path, get_credentials_path


def test_get_config_dir_returns_path():
    with patch.dict(os.environ, {"HOME": "/home/testuser"}):
        result = get_config_dir()
        assert result == Path("/home/testuser/.config/ghome")


def test_get_client_secret_path():
    with patch.dict(os.environ, {"HOME": "/home/testuser"}):
        result = get_client_secret_path()
        assert result == Path("/home/testuser/.config/ghome/client_secret.json")


def test_get_credentials_path():
    with patch.dict(os.environ, {"HOME": "/home/testuser"}):
        result = get_credentials_path()
        assert result == Path("/home/testuser/.config/ghome/credentials.json")
