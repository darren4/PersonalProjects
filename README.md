1. set PYTHONPATH to root of repository
2. Run simulator.py
    Parameters to tune are at the start of run_simulation simulator.py

csv files are created to show what happened

_status.csv traits
- ALIVE_COUNT: alive on that day
- STARVED: starved to death on that day
- CREATED: new organisms created through reproduction on that day
- EATEN: eaten by predators on that day

_evolve_.csv
- STRENGTH: average strength of all that organism type
- CALORIE_USAGE: average daily calorie usage of all that organism type
- OFFSPRING_CAPACITY: average max number of potential offspring from of all that organism type at a time