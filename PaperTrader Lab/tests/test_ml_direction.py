import pandas as pd
import numpy as np
from ml import train_direction_model, predict_direction


def test_train_and_predict_direction():
    dates = pd.date_range("2024-01-01", periods=60, freq="D")
    # synthetic price data with trend and noise
    prices = 100 + np.linspace(0, 5, len(dates)) + np.sin(np.linspace(0, 6, len(dates)))
    df = pd.DataFrame({"close": prices}, index=dates)
    model = train_direction_model(df)
    preds = predict_direction(model, df)
    # predictions should cover available feature rows and be binary
    assert set(preds.unique()) <= {0, 1}
    assert len(preds) == len(df) - 5  # due to lookback in feature engineering
