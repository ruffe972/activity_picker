import json
from json.decoder import JSONDecodeError
import math
from typing import Any, List, Optional

from pydantic import BaseModel, Extra, validator
from pydantic.error_wrappers import ValidationError


class Activity(BaseModel):
    name: str
    weight_mult: Optional[float]
    weight_ratio: Optional[float]

    class Config:
        extra = Extra.forbid
        allow_mutation = False

    def __init__(
            self,
            weight_mult: Optional[float] = None,
            weight_ratio: Optional[float] = None,
            **kwargs) -> None:
        try:
            if weight_mult is not None and weight_ratio is not None:
                raise ConfigError
            if weight_mult is None and weight_ratio is None:
                weight_mult = 1
            super().__init__(weight_mult=weight_mult, weight_ratio=weight_ratio, **kwargs)
        except ValidationError as e:
            raise ConfigError from e

    @validator('weight_mult')
    def _validate_weight_mult(cls, weight: Optional[float]) -> Optional[float]:
        del cls
        if weight is not None:
            assert math.isfinite(weight) and weight > 0
        return weight

    @validator('weight_ratio')
    def _validate_weight_ratio(cls, weight: Optional[float]) -> Optional[float]:
        del cls
        if weight is not None:
            assert 0 < weight and weight < 1
        return weight


class Configuration(BaseModel):
    activities: List[Activity]

    class Config:
        extra = Extra.forbid
        allow_mutation = False

    def __init__(self, **kwargs) -> None:
        try:
            super().__init__(**kwargs)
        except ValidationError as e:
            raise ConfigError from e

    @staticmethod
    def from_file(path: str) -> 'Configuration':
        activities = Configuration._get_data_from_path(path)
        return Configuration(activities=activities)

    @staticmethod
    def _get_data_from_path(path: str) -> Any:
        with open(path, 'r') as file:
            try:
                return json.load(file)
            except JSONDecodeError as e:
                raise ConfigError from e

    @validator('activities')
    def _validate_activities(cls, activities: List[Activity]) -> List[Activity]:
        del cls
        activity_names = frozenset([activity.name for activity in activities])
        assert(len(activities) == len(activity_names))
        return activities


class ConfigError(Exception):
    pass
