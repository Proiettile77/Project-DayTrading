import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline


def _build_features(df: pd.DataFrame) -> pd.DataFrame:
    """Generate basic technical features from price data.

    Parameters
    ----------
    df : pandas.DataFrame
        Must contain a ``close`` column with prices indexed by date.

    Returns
    -------
    pandas.DataFrame
        DataFrame of engineered features with NaN rows dropped.
    """
    feats = pd.DataFrame(index=df.index)
    feats["return_1"] = df["close"].pct_change()
    feats["return_5"] = df["close"].pct_change(5)
    return feats.dropna()


def train_direction_model(df: pd.DataFrame) -> Pipeline:
    """Train a simple logistic regression to predict price direction.

    The model predicts whether the next ``close`` price will be higher than
    the current ``close`` based on past percentage returns.

    Parameters
    ----------
    df : pandas.DataFrame
        Price data with a ``close`` column.

    Returns
    -------
    sklearn.pipeline.Pipeline
        Trained scikit-learn pipeline with scaling and logistic regression.
    """
    X = _build_features(df)
    # Target: 1 if next close is higher, else 0
    y = (df["close"].shift(-1) > df["close"]).astype(int).loc[X.index]
    model = Pipeline([
        ("scaler", StandardScaler()),
        ("lr", LogisticRegression(solver="liblinear")),
    ])
    model.fit(X, y)
    return model


def predict_direction(model: Pipeline, df: pd.DataFrame) -> pd.Series:
    """Predict upward (1) or downward (0) movement using a trained model."""
    X = _build_features(df)
    preds = model.predict(X)
    return pd.Series(preds, index=X.index, name="direction")
