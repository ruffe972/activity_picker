import json
import math
from json.decoder import JSONDecodeError
from typing import Any, List, Optional

from pydantic import BaseModel, Extra, validator
from pydantic.error_wrappers import ValidationError


class Activity(BaseModel):
    '''Represents an activity config entry.
    There are two variants of having weight modifiers.
    First: no modifiers (this sets weight_mult to 1).
    Second: Either weight_mult or weight_ratio modifier is present.
    '''

    name: str
    '''Should be unique.'''

    weight_mult: Optional[float]
    '''Activity's weight is calculated automatically.
    It's picked more often than any other activity with weight_mult=1 by the factor of weight_mult.
    '''

    weight_ratio: Optional[float]
    '''Activity's weight has a fixed weight_ratio to total weight of all activities.
    For example, weight_ratio of 0.3 means that the activity has a 30% probability of being picked.
    '''

    class Config:
        extra = Extra.forbid
        allow_mutation = False

    def __init__(
            self,
            weight_mult: Optional[float] = None,
            weight_ratio: Optional[float] = None,
            **kwargs) -> None:
        '''Throws ActivityError if something goes wrong.'''
        try:
            if weight_mult is not None and weight_ratio is not None:
                raise ActivityError('weight_mult and weight_ratio can not be used simultaneously')
            if weight_mult is None and weight_ratio is None:
                weight_mult = 1
            super().__init__(weight_mult=weight_mult, weight_ratio=weight_ratio, **kwargs)
        except ValidationError as e:
            raise ActivityError(e)

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


class ActivityError(Exception):
    pass


class Configuration(BaseModel):
    '''Represents data from a config file.
    '''

    activities: List[Activity]

    class Config:
        extra = Extra.forbid
        allow_mutation = False

    def __init__(self, **kwargs) -> None:
        '''Throws ConfigError if somethings goes wrong.'''
        try:
            super().__init__(**kwargs)
        except (ValidationError, ActivityError) as e:
            raise ConfigError(e)

    @staticmethod
    def from_file(path: str) -> 'Configuration':
        '''Throws OSError if the config file is not found.
        Throws ConfigError if something else goes wrong.
        '''
        activities = Configuration._get_data_from_path(path)
        return Configuration(activities=activities)

    @staticmethod
    def _get_data_from_path(path: str) -> Any:
        '''Throws OSError/ConfigError.'''
        with open(path, 'r') as file:
            try:
                return json.load(file)
            except JSONDecodeError as e:
                raise ConfigError(e)

    @validator('activities')
    def _validate_activities(cls, activities: List[Activity]) -> List[Activity]:
        assert activities, 'There should be at least one activity'
        cls._assert_activities_are_unique(activities)
        assert cls.get_total_weight_ratio(activities) < 1, 'Total weight_ratio should be < 1'
        return activities

    @staticmethod
    def _assert_activities_are_unique(activities: List[Activity]) -> None:
        activity_names = frozenset([activity.name for activity in activities])
        assert len(activities) == len(activity_names), 'Activities should have unique names'

    @staticmethod
    def get_total_weight_ratio(activities: List[Activity]) -> float:
        '''Gets sum of all weight_ratio fields.'''
        weight_ratios = [it.weight_ratio for it in activities if it.weight_ratio is not None]
        return sum(weight_ratios)


class ConfigError(Exception):
    pass
