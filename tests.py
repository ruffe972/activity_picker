from config import Activity, Configuration, ConfigError
import unittest
from math import nan, inf
from pick_tester import PickTester
from picker import PickerError


class ConfigurationTest(unittest.TestCase):
    @staticmethod
    def _new_test_config(test_name: str) -> Configuration:
        return Configuration.from_file('test_configs/' + test_name)

    def test_missing_config(self) -> None:
        with self.assertRaises(OSError):
            self._new_test_config('missing.json')

    def test_syntax_error(self) -> None:
        with self.assertRaises(ConfigError):
            self._new_test_config('syntax_error.json')

    def test_duplicate_activities(self) -> None:
        activities = [
            {'name': 'a'},
            {
                'name': 'a',
                'weight_mult': 2
            }
        ]
        with self.assertRaises(ConfigError):
            Configuration(activities=activities)

    def test_normal_valid(self) -> None:
        self._new_test_config('normal_valid.json')

    def test_minimal_valid(self) -> None:
        self._new_test_config('minimal_valid.json')


class ActivityTest(unittest.TestCase):
    def test_bad_field_type(self) -> None:
        with self.assertRaises(ConfigError):
            Activity(name=None)

    @staticmethod
    def _new_no_name_activity(**kwargs) -> Activity:
        return Activity(name='', **kwargs)

    def test_bad_weight_mult(self) -> None:
        for weight in [0, -0.1, -2, inf, -inf, nan]:
            with self.assertRaises(ConfigError):
                self._new_no_name_activity(weight_mult=weight)

    def test_valid_weight_mult(self) -> None:
        self._new_no_name_activity(weight_mult=0.1)

    def test_conflicting_weight_modifiers(self) -> None:
        with self.assertRaises(ConfigError):
            self._new_no_name_activity(weight_mult=0.5, weight_ratio=0.5)

    def test_valid_weight_ratio(self) -> None:
        for weight in [0.1, 0.5, 0.9]:
            self._new_no_name_activity(weight_ratio=weight)

    def test_bad_weight_ratio(self) -> None:
        for weight in [-0.1, -2, 0, 1, 2, -inf, inf, nan]:
            with self.assertRaises(ConfigError):
                self._new_no_name_activity(weight_ratio=weight)


class PickerTest(unittest.TestCase):
    ''' These tests can theoretically fail because random is involved.
    '''

    _ALLOWED_DEVIATION = 0.015
    _max_deviation: float = 0

    @classmethod
    def tearDownClass(cls) -> None:
        print(f'\nMax deviation: {cls._max_deviation:.3f}. Should be < {cls._ALLOWED_DEVIATION}.')

    def _test_pick(self, pick_tester: PickTester) -> None:
        max_deviation = pick_tester.test_and_get_deviation()
        PickerTest._max_deviation = max(self._max_deviation, max_deviation)
        self.assertLess(max_deviation, self._ALLOWED_DEVIATION)

    def test_two_simple_activities(self) -> None:
        activities = [
            Activity(name='a'),
            Activity(name='b')
        ]
        expected_ratios = {'a': 0.5, 'b': 0.5}
        tester = PickTester(activities, expected_ratios)
        self._test_pick(tester)

    def test_single_activity(self) -> None:
        activities = [Activity(name='a')]
        expected_ratios = {'a': 1.0}
        tester = PickTester(activities, expected_ratios)
        self._test_pick(tester)

    def test_blacklist(self) -> None:
        activities = [
            Activity(name='A'),
            Activity(name='a'),
            Activity(name='B'),
            Activity(name='b')
        ]
        expected_ratios = {
            'B': 0.5,
            'a': 0.5,
            'A': 0,
            'b': 0}
        blacklist = ['A', 'b']
        tester = PickTester(activities, expected_ratios, blacklist)
        self._test_pick(tester)

    def test_no_activities(self) -> None:
        activities = [Activity(name='a')]
        blacklist = ['a']
        with self.assertRaises(PickerError):
            tester = PickTester(activities, {}, blacklist)
            self._test_pick(tester)

    def test_weight_ratio(self) -> None:
        activities = [
            Activity(name='a', weight_ratio=0.4),
            Activity(name='b'),
            Activity(name='c', weight_ratio=0.1),
            Activity(name='d')
        ]
        expected_ratios = {
            'a': 0.4,
            'b': 0.25,
            'c': 0.1,
            'd': 0.25
        }
        tester = PickTester(activities, expected_ratios)
        self._test_pick(tester)

    # def test_weight_mult(self) -> None:
    #     activities = [
    #         Activity(name='a', weight_mult=2),
    #         Activity(name='b', weight_mult=0.6),
    #         Activity(name='c'),
    #         Activity(name='d')
    #     ]
    #     blacklist = ['d']
    #     expected = [2, 0.6, 1, 0]
    #     tester = PickTester(activities, expected, blacklist)
    #     self._test_pick(tester)


if __name__ == '__main__':
    unittest.main()
