import importlib


def test_env_merge_backup(tmp_path, monkeypatch):
    monkeypatch.setenv("APP_ROOT", str(tmp_path))
    secure_store = importlib.reload(importlib.import_module("utils.secure_store"))
    config = importlib.reload(importlib.import_module("utils.config"))

    (tmp_path / ".env").write_text("OTHER=1\n")
    secure_store.save("alpaca", "env_file", "K1", "S1", "https://paper-api.alpaca.markets")
    content = (tmp_path / ".env").read_text()
    assert "OTHER=1" in content
    assert (tmp_path / ".env.bak").exists()


def test_migrate_env_to_keyring(tmp_path, monkeypatch):
    monkeypatch.setenv("APP_ROOT", str(tmp_path))
    secure_store = importlib.reload(importlib.import_module("utils.secure_store"))
    config = importlib.reload(importlib.import_module("utils.config"))

    secure_store.save("alpaca", "env_file", "K1", "S1", "https://paper-api.alpaca.markets")
    creds = config.load_credentials("alpaca")
    assert creds["key"] == "K1"
    assert config.current_storage_backend("alpaca") == "env_file"

    store = {}
    monkeypatch.setattr(secure_store.keyring, "set_password", lambda s, u, p: store.__setitem__((s, u), p))
    monkeypatch.setattr(secure_store.keyring, "get_password", lambda s, u: store.get((s, u)))

    secure_store.save("alpaca", "keyring", "K2", "S2", "https://paper-api.alpaca.markets")
    secure_store.delete("alpaca", "env_file")

    creds2 = config.load_credentials("alpaca")
    assert creds2["key"] == "K2"
    assert config.current_storage_backend("alpaca") == "keyring"


def test_test_credentials(monkeypatch):
    import httpx
    import utils.config as config

    def fake_get(url, headers=None, timeout=None):
        return httpx.Response(200, request=httpx.Request("GET", url), text="ok")

    monkeypatch.setattr(httpx, "get", fake_get)

    ok, err = config.test_credentials("alpaca", "k", "s", "https://paper-api.alpaca.markets")
    assert ok and err == ""

