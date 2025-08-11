import importlib


def test_migrate_env_to_keyring(tmp_path, monkeypatch):
    monkeypatch.setenv("APP_ROOT", str(tmp_path))
    secure_store = importlib.reload(importlib.import_module("utils.secure_store"))
    config = importlib.reload(importlib.import_module("utils.config"))

    secure_store.write_to_env_file("K1", "S1", "https://paper-api.alpaca.markets")
    creds = config.load_credentials()
    assert creds["key"] == "K1"
    assert config.current_storage_backend() == "env_file"

    store = {}
    monkeypatch.setattr(secure_store.keyring, "set_password", lambda s, u, p: store.__setitem__((s, u), p))
    monkeypatch.setattr(secure_store.keyring, "get_password", lambda s, u: store.get((s, u)))
    monkeypatch.setattr(secure_store.keyring, "delete_password", lambda s, u: store.pop((s, u), None))

    config.save_credentials("keyring", "K2", "S2", "https://paper-api.alpaca.markets")
    secure_store.delete_env_file()

    creds2 = config.load_credentials()
    assert creds2["key"] == "K2"
    assert config.current_storage_backend() == "keyring"


def test_test_alpaca_credentials(monkeypatch):
    import utils.config as config

    class DummyClient:
        def get_account(self):
            return True

    def fake_client(key, secret, base_url=None):
        assert key == "k" and secret == "s"
        return DummyClient()

    monkeypatch.setattr("alpaca.trading.client.TradingClient", fake_client)
    ok, err = config.test_alpaca_credentials("k", "s", "https://paper-api.alpaca.markets")
    assert ok and err == ""

