import importlib
import sys
from pathlib import Path

import pytest
from fastapi import HTTPException


def load_security_module():
    backend_root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(backend_root))
    sys.modules.pop("core.security", None)
    return importlib.import_module("core.security")


def test_require_api_key_rejects_missing_server_key(monkeypatch):
    security_module = load_security_module()
    monkeypatch.delenv("API_KEY", raising=False)

    with pytest.raises(HTTPException) as exc_info:
        security_module.require_api_key("some-key")

    assert exc_info.value.status_code == 500


@pytest.mark.parametrize("provided_key", [None, "wrong-key"])
def test_require_api_key_rejects_invalid_or_missing(monkeypatch, provided_key):
    security_module = load_security_module()
    monkeypatch.setenv("API_KEY", "expected-key")

    with pytest.raises(HTTPException) as exc_info:
        security_module.require_api_key(provided_key)

    assert exc_info.value.status_code == 401


def test_require_api_key_accepts_valid_key(monkeypatch):
    security_module = load_security_module()
    monkeypatch.setenv("API_KEY", "expected-key")

    security_module.require_api_key("expected-key")
