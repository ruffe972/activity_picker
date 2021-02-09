import random
from typing import Dict, List, Optional

from config import Activity, Configuration


class Picker:
    '''Picks an activity from Configuration.'''
    def __init__(self, configuration: Configuration, blacklist: Optional[List[str]] = None) -> None:
        ''' Can throw PickerError.'''
        just_blacklist = [] if blacklist is None else blacklist
        self.activities: List[Activity] = [it for it in configuration.activities if it.name not in just_blacklist]
        if not self.activities:
            raise PickerError('There are no activities to pick from')
        if all([it.weight_ratio is not None for it in self.activities]):
            raise PickerError('At least one whitelisted activity should not have weight_ratio')
        total_weight_ratio = configuration.get_total_weight_ratio(self.activities)
        total_weight_mult = sum([it.weight_mult for it in self.activities if it.weight_mult is not None])
        self.weight_mult_base: float = (1 - total_weight_ratio) / total_weight_mult

    def pick(self) -> str:
        return random.choices(self.activities, self._get_weights())[0].name

    def get_weights_dict(self) -> Dict[str, float]:
        '''Returns a dict of (activity.name: weight) pairs.'''
        keys = [it.name for it in self.activities]
        return dict(zip(keys, self._get_weights()))

    def _get_weights(self) -> List[float]:
        return [self._get_weight(it) for it in self.activities]

    def _get_weight(self, activity: Activity) -> float:
        if activity.weight_ratio is not None:
            return activity.weight_ratio
        if activity.weight_mult is not None:
            return self.weight_mult_base * activity.weight_mult
        raise RuntimeError


class PickerError(Exception):
    pass
