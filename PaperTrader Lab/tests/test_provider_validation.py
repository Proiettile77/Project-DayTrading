import httpx
import pytest

from utils.config import test_credentials as _test_credentials


@pytest.mark.parametrize("provider", ["alpaca", "oanda", "binance"])
def test_validate_success(monkeypatch, provider):
    def fake_get(url, headers=None, timeout=None):
        return httpx.Response(200, request=httpx.Request("GET", url), text="ok")
    monkeypatch.setattr(httpx, "get", fake_get)
    ok, err = _test_credentials(provider, "k", "s", "https://api.test")
    assert ok and err == ""


@pytest.mark.parametrize("provider", ["alpaca", "oanda", "binance"])
def test_validate_invalid(monkeypatch, provider):
    def fake_get(url, headers=None, timeout=None):
        return httpx.Response(401, request=httpx.Request("GET", url), text="bad creds")
    monkeypatch.setattr(httpx, "get", fake_get)
    ok, err = _test_credentials(provider, "k", "s", "https://api.test")
    assert not ok
    assert "bad creds" in err


@pytest.mark.parametrize("provider", ["alpaca", "oanda", "binance"])
def test_validate_network_failure(monkeypatch, provider):
    def fake_get(url, headers=None, timeout=None):
        raise httpx.ConnectError("boom", request=httpx.Request("GET", url))
    monkeypatch.setattr(httpx, "get", fake_get)
    ok, err = _test_credentials(provider, "k", "s", "https://api.test")
    assert not ok
    assert "boom" in err
