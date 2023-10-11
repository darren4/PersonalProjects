import random
from threading import Lock, Condition
from abc import ABC
import math


class Logger:
    def __init__(self):
        self.status = open("status.txt", "w")
        self.status_lock = Lock()
        self.evolution_stats = open("evolution_stats.txt", "w")
        self.evolution_stats_lock = Lock()

    def log(self, msg, msg_type="STATUS"):
        if msg_type == "STATUS":
            with self.status_lock:
                self.status.write(f"{msg}\n")
        elif msg_type == "EVOLVE":
            with self.evolution_stats_lock:
                self.evolution_stats.write(f"{msg}\n")
        else:
            print("Unidentified type")
            assert False

    def __del__(self):
        self.status.close()
        self.evolution_stats.close()


class Planet:
    grid = None
    grid_shape = None  # TODO: make reader lock

    ready = 0
    ready_lock = Lock()
    ready_cv = Condition(ready_lock)
    worker_count = None

    # PROCESS, TRANSITION, DONE
    worker_state = "PROCESS"
    worker_state_lock = Lock()
    worker_state_cv = Condition(worker_state_lock)

    logger = Logger()


class Ecosystem:
    alive_count = 0
    alive_count_lock = Lock()

    @staticmethod
    def display_status():
        with Ecosystem.alive_count_lock:
            alive_count = Ecosystem.alive_count
            Planet.logger.log(f"Organism count: {alive_count}")
            return alive_count


class Organism(ABC):
    alive_count = None
    alive_count_lock = None

    starved_in_round = None
    starved_in_round_lock = None
    created_in_round = None
    created_in_round_lock = None

    totals_stats = {
        "STRENGTH": None,
        "CALORIE_USAGE": None,
        "OFFSPRING_CAPACITY": None,
    }
    totals_stats_lock = None

    organism_type = None

    def __init__(self, _inherited=None):
        with Ecosystem.alive_count_lock:
            Ecosystem.alive_count += 1
        with self.__class__.alive_count_lock:
            self.__class__.alive_count += 1

        if _inherited:
            for trait in ["STRENGTH", "CALORIE_USAGE", "OFFSPRING_CAPACITY"]:
                assert trait in _inherited
            self.inherited = _inherited
        else:
            self.inherited = {
                "STRENGTH": random.randint(5, 10),
                "CALORIE_USAGE": random.randint(0, 3),
                "OFFSPRING_CAPACITY": random.randint(1, 5),
            }
        self.stored_calories = 10

        with self.totals_stats_lock:
            for trait in self.__class__.totals_stats:
                self.__class__.totals_stats[trait] += self.inherited[trait]

    def __del__(self):
        with Ecosystem.alive_count_lock:
            Ecosystem.alive_count -= 1

    @classmethod
    def display_status(cls):
        with cls.alive_count_lock:
            Planet.logger.log(f"{cls.organism_type} alive count: {cls.alive_count}")
        Planet.logger.log(f"{cls.organism_type} round changes:")
        with cls.starved_in_round_lock:
            Planet.logger.log(f"    Starved: {cls.starved_in_round}")
        with cls.created_in_round_lock:
            Planet.logger.log(f"    Created: {cls.created_in_round}")

    @classmethod
    def reset_round_status(cls):
        with cls.starved_in_round_lock:
            cls.starved_in_round = 0
        with cls.created_in_round_lock:
            cls.created_in_round = 0

    @classmethod
    def create_child(cls, new_traits):
        return cls(new_traits)

    @classmethod
    def display_evolution_status(cls):
        with cls.totals_stats_lock:
            Planet.logger.log(f"--- {cls.organism_type} ---", msg_type="EVOLVE")
            for trait in cls.totals_stats:
                avg = cls.totals_stats[trait] / cls.alive_count
                Planet.logger.log(f"Avg {trait}: {round(avg, 2)}", msg_type="EVOLVE")

    def reproduce(self, mate):
        offspring = []
        for _ in range(
            min(
                self.inherited["OFFSPRING_CAPACITY"],
                mate.inherited["OFFSPRING_CAPACITY"],
            )
        ):
            new_traits = {}
            for trait, value in self.inherited.items():
                if random.randint(0, 1):
                    new_traits[trait] = value
                else:
                    new_traits[trait] = mate.inherited[trait]
            offspring.append(self.create_child(new_traits))

        with self.__class__.created_in_round_lock:
            self.__class__.created_in_round += len(offspring)
        return offspring

    def confront_day(self):
        raise NotImplementedError()


class Prey(Organism):
    alive_count = 0
    alive_count_lock = Lock()

    starved_in_round = 0
    starved_in_round_lock = Lock()
    eaten_in_round = 0
    eaten_in_round_lock = Lock()
    created_in_round = 0
    created_in_round_lock = Lock()

    totals_stats = {
        "STRENGTH": 0,
        "CALORIE_USAGE": 0,
        "OFFSPRING_CAPACITY": 0,
    }
    totals_stats_lock = Lock()

    organism_type = "Prey"

    @classmethod
    def display_status(self):
        super().display_status()
        with self.eaten_in_round_lock:
            Planet.logger.log(f"    Eaten: {self.eaten_in_round}")

    @classmethod
    def reset_round_status(cls):
        super().reset_round_status()
        with cls.eaten_in_round_lock:
            cls.eaten_in_round = 0

    def confront_day(self, predator_strength=0, eat=0) -> bool:
        still_alive = True
        if self.inherited["STRENGTH"] < predator_strength:
            still_alive = False
            with self.__class__.eaten_in_round_lock:
                self.__class__.eaten_in_round += 1

        self.stored_calories += eat - self.inherited["CALORIE_USAGE"]
        if self.stored_calories <= 0:
            still_alive = False
            with self.__class__.starved_in_round_lock:
                self.__class__.starved_in_round += 1

        return still_alive


class Predator(Organism):
    alive_count = 0
    alive_count_lock = Lock()

    starved_in_round = 0
    starved_in_round_lock = Lock()
    eaten_in_round = 0
    eaten_in_round_lock = Lock()
    created_in_round = 0
    created_in_round_lock = Lock()

    totals_stats = {
        "STRENGTH": 0,
        "CALORIE_USAGE": 0,
        "OFFSPRING_CAPACITY": 0,
    }
    totals_stats_lock = Lock()

    organism_type = "Predator"

    def confront_day(self, prey_strength) -> bool:
        food_amount = 0
        if not math.isnan(prey_strength) and self.inherited["STRENGTH"] > prey_strength:
            food_amount = 1

        self.stored_calories += food_amount - self.inherited["CALORIE_USAGE"]
        if self.stored_calories <= 0:
            with self.__class__.starved_in_round_lock:
                self.__class__.starved_in_round += 1
            return False
        else:
            return True
