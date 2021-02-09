import sys
from typing import Dict

from config import ConfigError, Configuration
from picker import Picker, PickerError

_CONFIG = 'C:/Users/Ivan/f/other/activities.json'


def _main() -> None:
    '''Reads a config file with a list of activities, then operates on it according to README.md.
    '''
    try:
        config = Configuration.from_file(_CONFIG)
        picker = Picker(config)
    except (OSError, ConfigError, PickerError) as e:
        print(e)
    else:
        if len(sys.argv) == 2 and sys.argv[1] == '-w':
            _print_weights(picker.get_weights_dict())
        elif len(sys.argv) == 1:
            print(picker.pick())
        else:
            print('Bad arguments.')
            _print_help()


def _print_help() -> None:
    print('No arguments: randomly picks an activity from the list.')
    print('-w: print activities\' probabilities of being picked.')
    print('See README.md for more.')


def _print_weights(weights: Dict[str, float]) -> None:
    for name, weight in weights.items():
        weight_percentage = weight * 100
        print(f'{name}: {weight_percentage:.1f}%')


if __name__ == '__main__':
    _main()
