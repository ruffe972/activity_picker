# Activity Picker

Randomly picks an activity from the list of activities (user-defined in a configuration file). I wrote this for me and my gf: sometimes we couldn't agree on something.

* weight_ratio of 0.3 means that the activity has a fixed 30% probability of being picked.
* weight_mult of value x means that it's picked more often than any other activity with weight_mult=1 by the factor of x.
* If no weight modifiers are found, weight_mult is automatically assigned to 1.

`-w` command line argument prints activities\' probabilities of being picked (in %).

Please contact me if you want to use the program - I'll quickly make a release and make a config path configurable.

Config file example:

```json
[
    {
        "name": "TV series",
        "weight_ratio": 0.2
    },
    {
        "name": "Movies",
        "weight_ratio": 0.3
    },
    {
        "name": "Super Mario 3D World",
        "weight_mult": 2
    },
    {
        "name": "Checkers",
        "weight_mult": 0.4
    },
    {
        "name": "Chess"
    },
    {
        "name": "Overcooked 2"
    }
]
```

## Info for Developers

Written in python with type hints everywhere. Also there are some unit tests.

Dependencies:
* python 3.9.1
* pydantic 1.7.3

## To Do

* Allow user to temporarily blacklist some activities (checkboxes).