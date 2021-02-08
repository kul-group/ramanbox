from joblib import load
from typing import List
import numpy as np


class Controller:
    def __init__(self, ml_model_path):
        self.ml_model = load(ml_model_path)

    def make_prediction(self, data: List, pos_threshold: float = 0.5) -> int:
        data_wrap = np.array([data])
        result = self.ml_model.predict(data_wrap)
        if result[0] > pos_threshold:
            return self.get_next()
        else:
            self.get_more()

    def get_next(self) -> int:
        return 0

    def get_more(self) -> int:
        return 1
