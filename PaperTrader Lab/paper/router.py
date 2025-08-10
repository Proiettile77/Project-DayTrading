from utils.config import SETTINGS
from paper import alpaca as alp

def provider_name():
    return "alpaca" if SETTINGS.enable_alpaca else "none"

def connect_info():
    if SETTINGS.enable_alpaca:
        return dict(provider="Alpaca Paper", account=alp.account())
    return dict(provider="none")
