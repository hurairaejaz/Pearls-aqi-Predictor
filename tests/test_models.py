import numpy as np

from src.models.baseline import persistence_prediction
from src.models.evaluate import regression_metrics
from src.models.ridge import create_ridge_model


def test_persistence():
    assert persistence_prediction(100) == 100.0


def test_metrics():
    result = regression_metrics(
        np.array([1, 2, 3]),
        np.array([1, 2, 4]),
    )
    assert result["rmse"] > 0
    assert result["mae"] > 0


def test_ridge_can_fit():
    X = np.array(
        [
            [1.0, 2.0],
            [2.0, 3.0],
            [3.0, 4.0],
            [4.0, 5.0],
        ]
    )
    y = np.array([2.0, 3.0, 4.0, 5.0])

    model = create_ridge_model()
    model.fit(X, y)

    assert model.predict([[5.0, 6.0]])[0] > 4.0
