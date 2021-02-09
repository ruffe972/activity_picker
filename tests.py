import unittest
from math import inf, nan
from typing import List, Optional

from config import Activity, ActivityError, ConfigError, Configuration
from picker import Picker, PickerError


class ConfigurationTest(unittest.TestCase):
    @staticmethod
    def new_test_config(test_name: str) -> Configuration:
        '''Creates a Configuration that's read from a test file.'''
        return Configuration.from_file('test_configs/' + test_name)

    def test_missing_config(self) -> None:
        with self.assertRaisesRegex(OSError, 'No such file'):
            self.new_test_config('missing.json')

    def test_syntax_error(self) -> None:
        with self.assertRaisesRegex(ConfigError, 'Expecting value'):
            self.new_test_config('syntax_error.json')

    def test_wrong_type(self) -> None:
        with self.assertRaises(ConfigError):
            self.new_test_config('wrong_type.json')

    def test_duplicate_activities(self) -> None:
        activities = [
            {'name': 'a'},
            {
                'name': 'a',
                'weight_mult': 2
            }
        ]
        with self.assertRaises(ConfigError) as context:
            Configuration(activities=activities)
            self.assertEquals(str(context.exception), 'Activities should have unique names')

    def test_minimal(self) -> None:
        self.new_test_config('minimal.json')

    def test_bad_weight_ratio_sum(self) -> None:
        activities = [
            Activity(name='a', weight_ratio=0.5),
            Activity(name='b', weight_ratio=0.5),
            Activity(name='c')
        ]
        with self.assertRaises(ConfigError) as context:
            Configuration(activities=activities)
            self.assertEquals(str(context.exception), 'Total weight_ratio should be < 1')

    def test_no_activities(self) -> None:
        with self.assertRaises(ConfigError) as context:
            Configuration(activities=[])
            self.assertEquals(str(context.exception), 'There should be at least one activity')

    def test_bad_activity(self) -> None:
        activities = [{'name': None}]
        with self.assertRaisesRegex(ConfigError, 'type_error.none.not_allowed'):
            Configuration(activities=activities)


class ActivityTest(unittest.TestCase):
    def test_bad_field_type(self) -> None:
        with self.assertRaisesRegex(ActivityError, 'type_error.none.not_allowed'):
            Activity(name=None)

    @staticmethod
    def _new_no_name_activity(**kwargs) -> Activity:
        return Activity(name='', **kwargs)

    def test_bad_weight_mult(self) -> None:
        for weight in [0, -0.1, -2, inf, -inf, nan]:
            with self.assertRaisesRegex(ActivityError, 'weight_mult'):
                self._new_no_name_activity(weight_mult=weight)

    def test_valid_weight_mult(self) -> None:
        self._new_no_name_activity(weight_mult=0.1)

    def test_conflicting_weight_modifiers(self) -> None:
        with self.assertRaises(ActivityError) as context:
            self._new_no_name_activity(weight_mult=0.5, weight_ratio=0.5)
            self.assertEquals(str(context.exception), 'weight_mult and weight_ratio can not be used simultaneously')

    def test_valid_weight_ratio(self) -> None:
        for weight in [0.1, 0.5, 0.9]:
            self._new_no_name_activity(weight_ratio=weight)

    def test_bad_weight_ratio(self) -> None:
        for weight in [-0.1, -2, 0, 1, 2, -inf, inf, nan]:
            with self.assertRaisesRegex(ActivityError, 'weight_ratio'):
                self._new_no_name_activity(weight_ratio=weight)


class PickerTest(unittest.TestCase):
    def _test_weights(
            self,
            activities: List[Activity],
            expected_weights: List[float],
            blacklist: Optional[List[str]] = None) -> None:
        picker = Picker(Configuration(activities=activities), blacklist)
        actual_weights = picker._get_weights()
        expected_normalized = self._get_normalized(expected_weights)
        for actual, expected in zip(actual_weights, expected_normalized):
            self.assertAlmostEqual(actual, expected)

    @staticmethod
    def _get_normalized(weights: List[float]) -> List[float]:
        return [it / sum(weights) for it in weights]

    def test_single_activity(self) -> None:
        activities = [Activity(name='a')]
        expected = [1.0]
        self._test_weights(activities, expected)

    def test_two_simple_activities(self) -> None:
        activities = [
            Activity(name='a'),
            Activity(name='b')
        ]
        expected = [1.0, 1]
        self._test_weights(activities, expected)

    def test_blacklist(self) -> None:
        activities = [
            Activity(name='A'),
            Activity(name='a'),
            Activity(name='B'),
            Activity(name='b')
        ]
        expected = [1.0, 1]
        blacklist = ['A', 'b']
        self._test_weights(activities, expected, blacklist)

    def test_no_activities(self) -> None:
        activities = [Activity(name='a')]
        blacklist = ['a']

        with self.assertRaises(PickerError) as context:
            self._test_weights(activities, [], blacklist)
            self.assertEquals(str(context.exception), 'There are no activities to pick from')

    def test_weight_ratio(self) -> None:
        activities = [
            Activity(name='a', weight_ratio=0.4),
            Activity(name='b'),
            Activity(name='c', weight_ratio=0.1),
            Activity(name='d')
        ]
        expected = [0.4, 0.25, 0.1, 0.25]
        self._test_weights(activities, expected)

    def test_weight_mult(self) -> None:
        activities = [
            Activity(name='a', weight_mult=2),
            Activity(name='b', weight_mult=0.6),
            Activity(name='c'),
            Activity(name='d')
        ]
        blacklist = ['d']
        expected = [2, 0.6, 1]
        self._test_weights(activities, expected, blacklist)

    def test_complex(self) -> None:
        activities = [
            Activity(name='a', weight_ratio=0.3),
            Activity(name='b', weight_mult=3),
            Activity(name='c', weight_ratio=0.6),
            Activity(name='d'),
            Activity(name='e')
        ]
        blacklist = ['c', 'e']
        expected = [0.3, 0.525, 0.175]
        self._test_weights(activities, expected, blacklist)

    def test_all_with_weight_ratio(self) -> None:
        activities = [
            Activity(name='a', weight_ratio=0.1),
            Activity(name='b', weight_ratio=0.1),
            Activity(name='c')
        ]
        blacklist = ['c']
        with self.assertRaises(PickerError) as context:
            self._test_weights(activities, [], blacklist)
            self.assertEquals(str(context.exception), 'At least one whitelisted activity should not have weight_ratio')

    def test_normal(self) -> None:
        config = ConfigurationTest.new_test_config('normal.json')
        activities = config.activities
        blacklist = ["Overcooked 2"]
        expected = [0.2, 0.3, 0.29411764705882354, 0.05882352941176471, 0.14705882352941177]
        self._test_weights(activities, expected, blacklist)


if __name__ == '__main__':
    unittest.main()
