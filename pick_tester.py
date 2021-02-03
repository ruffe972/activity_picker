from typing import Dict, List
from config import Activity, Configuration
from picker import Picker
from dataclasses import dataclass, field


@dataclass(frozen=True)
class PickTester:
    _PASSES = 10000
    activities: List[Activity]
    expected_ratios: Dict[str, float]
    blacklist: List[str] = field(default_factory=list)

    def test_and_get_deviation(self) -> float:
        Configuration(activities=self.activities)
        actual_ratios = self._get_actual_ratios()
        return self._get_max_deviation(actual_ratios)

    def _get_actual_ratios(self) -> Dict[str, float]:
        picks = {it.name: 0 for it in self.activities}
        for _ in range(self._PASSES):
            name = Picker(self.activities, self.blacklist).pick()
            picks[name] += 1
        return {k: v / self._PASSES for k, v in picks.items()}

    def _get_max_deviation(self, actual_ratios: Dict[str, float]) -> float:
        deviations = [self._get_deviation(k, actual) for k, actual in actual_ratios.items()]
        return max(deviations)

    def _get_deviation(self, activity_name: str, actual_ratio: float) -> float:
        return abs(self.expected_ratios[activity_name] - actual_ratio)
