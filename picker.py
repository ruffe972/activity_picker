from typing import List
from config import Activity
import random


class Picker:
    _TOTAL_WEIGHT = 1

    def __init__(self, activities: List[Activity], blacklist: List[str]) -> None:
        ''' Throws PickerError
        '''
        self.activities = [it for it in activities if it.name not in blacklist]
        if not self.activities:
            raise PickerError
        total_weight_ratio = sum([it.weight_ratio for it in self.activities if it.weight_ratio is not None])
        total_weight_mult = sum([it.weight_mult for it in self.activities if it.weight_mult is not None])
        self.weight_mult_base: float = (self._TOTAL_WEIGHT - total_weight_ratio) / total_weight_mult

    def get_weights(self) -> List[float]:
        return [self._get_weight(it) for it in self.activities]

    def pick(self) -> str:
        return random.choices(self.activities, self.get_weights())[0].name

    def _get_weight(self, activity: Activity) -> float:
        if activity.weight_ratio is not None:
            return self._TOTAL_WEIGHT * activity.weight_ratio
        if activity.weight_mult is not None:
            return self.weight_mult_base * activity.weight_mult
        raise RuntimeError


class PickerError(Exception):
    pass
