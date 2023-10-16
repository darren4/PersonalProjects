from ecosystem.constants import *

import random
from threading import Lock, Condition
from abc import ABC, abstractmethod
import pandas as pd


class Logger:
    def __init__(self, traits):
        self.data = {}
        for trait in traits:
            self.data[trait] = []

    def log(self, trait, value):
        try:
            self.data[trait].append(value)
        except KeyError:
            print(f"Invalid trait: {trait}")

    def to_csv(self, filename):
        lens = []
        for trait in self.data:
            lens.append(len(self.data[trait]))
        for i in range(1, len(lens)):
            assert lens[i] == lens[i - 1]
        df = pd.DataFrame.from_dict(self.data, orient="index").transpose()
        df.to_csv(f"ecosystem/{filename}")


class Planet:
    grid = None
    grid_shape = None  # TODO: make reader lock

    ready = 0
    ready_lock = Lock()
    ready_cv = Condition(ready_lock)
    worker_count = None

    # PROCESS, TRANSITION, DONE
    worker_state = PROCESS
    worker_state_lock = Lock()
    worker_state_cv = Condition(worker_state_lock)


class Ecosystem:
    alive_count = 0
    alive_count_lock = Lock()

    logger = Logger([ALIVE_COUNT])

    @staticmethod
    def display_status():
        with Ecosystem.alive_count_lock:
            alive_count = Ecosystem.alive_count
            Ecosystem.logger.log(ALIVE_COUNT, alive_count)
            return alive_count

    @staticmethod
    def save_status_history():
        Ecosystem.logger.to_csv("ecosystem_status.csv")


class Organism(ABC):
    # Override all these static variables

    alive_count = None
    alive_count_lock = None

    starved_in_round = None
    starved_in_round_lock = None
    created_in_round = None
    created_in_round_lock = None

    totals_stats = {
        STRENGTH: None,
        CALORIE_USAGE: None,
        OFFSPRING_CAPACITY: None,
    }
    totals_stats_lock = None

    organism_type = None

    status_logger = Logger([ALIVE_COUNT, STARVED, CREATED])
    evolve_logger = Logger(list(totals_stats.keys()))

    def __init__(self, _inherited=None, starting_calories=1):
        with Ecosystem.alive_count_lock:
            Ecosystem.alive_count += 1
        with self.__class__.alive_count_lock:
            self.__class__.alive_count += 1

        self.alive = True

        if _inherited:
            if set(_inherited.keys()) != {
                STRENGTH,
                CALORIE_USAGE,
                OFFSPRING_CAPACITY,
            }:
                raise ValueError(
                    f"Inherited traits have invalid keys: {list(_inherited.keys())}"
                )
            self.inherited = _inherited
        else:
            self.inherited = {
                STRENGTH: random.randint(0, 10),
                CALORIE_USAGE: random.randint(1, 3),
                OFFSPRING_CAPACITY: random.randint(0, 3),
            }
        self.stored_calories = starting_calories

        with self.totals_stats_lock:
            for trait in self.__class__.totals_stats:
                self.__class__.totals_stats[trait] += self.inherited[trait]

    def still_alive(self):
        return self.alive

    @classmethod
    def display_status(cls):
        with cls.alive_count_lock:
            cls.status_logger.log(ALIVE_COUNT, cls.alive_count)
        with cls.starved_in_round_lock:
            cls.status_logger.log(STARVED, cls.starved_in_round)
        with cls.created_in_round_lock:
            cls.status_logger.log(CREATED, cls.created_in_round)

    @classmethod
    def save_status_history(cls):
        cls.status_logger.to_csv(f"{cls.organism_type}_status.csv")

    @classmethod
    def reset_round_status(cls):
        with cls.starved_in_round_lock:
            cls.starved_in_round = 0
        with cls.created_in_round_lock:
            cls.created_in_round = 0

    @classmethod
    def display_evolution_status(cls):
        with cls.totals_stats_lock:
            for trait in cls.totals_stats:
                try:
                    avg = cls.totals_stats[trait] / cls.alive_count
                    cls.evolve_logger.log(trait, round(avg, 2))
                except ZeroDivisionError:
                    break

    @classmethod
    def save_evolution_history(cls):
        cls.evolve_logger.to_csv(f"{cls.organism_type}_evolve.csv")

    @classmethod
    def create_child(cls, new_traits, starting_calories):
        return cls(new_traits, starting_calories)

    def reproduce(self, mate):
        offspring = []
        offspring_capacity = min(
            self.inherited[OFFSPRING_CAPACITY],
            mate.inherited[OFFSPRING_CAPACITY],
        )
        starting_calories = (self.stored_calories + mate.stored_calories) / (
            offspring_capacity + 2
        )
        self.stored_calories, mate.stored_calories = (
            starting_calories,
            starting_calories,
        )
        for _ in range(offspring_capacity):
            new_traits = {}
            for trait, value in self.inherited.items():
                if random.randint(0, 1):
                    new_traits[trait] = value
                else:
                    new_traits[trait] = mate.inherited[trait]
            offspring.append(self.create_child(new_traits, starting_calories))

        with self.__class__.created_in_round_lock:
            self.__class__.created_in_round += len(offspring)
        return offspring

    @abstractmethod
    def eat_for_day(self, food):
        raise NotImplementedError()

    # @abstractmethod
    # def confront_day(self):
    #     raise NotImplementedError()


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
        STRENGTH: 0,
        CALORIE_USAGE: 0,
        OFFSPRING_CAPACITY: 0,
    }
    totals_stats_lock = Lock()

    organism_type = "Prey"

    status_logger = Logger([ALIVE_COUNT, STARVED, CREATED, EATEN])
    evolve_logger = Logger(list(totals_stats.keys()))

    @classmethod
    def display_status(cls):
        super().display_status()
        with cls.eaten_in_round_lock:
            cls.status_logger.log(EATEN, cls.eaten_in_round)

    @classmethod
    def reset_round_status(cls):
        super().reset_round_status()
        with cls.eaten_in_round_lock:
            cls.eaten_in_round = 0

    def eat_for_day(self, food_list):
        if not self.alive:
            with self.__class__.eaten_in_round_lock:
                self.__class__.eaten_in_round += 1
        else:
            self.stored_calories -= self.inherited[CALORIE_USAGE]
            for food in food_list:
                self.stored_calories += food
            self.alive = self.stored_calories > 0
            if not self.alive:
                with self.__class__.starved_in_round_lock:
                    self.__class__.starved_in_round += 1
        if not self.alive:
            with Ecosystem.alive_count_lock:
                Ecosystem.alive_count -= 1
            with self.__class__.alive_count_lock:
                self.__class__.alive_count -= 1
            with self.totals_stats_lock:
                for trait in self.__class__.totals_stats:
                    self.__class__.totals_stats[trait] -= self.inherited[trait]


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
        STRENGTH: 0,
        CALORIE_USAGE: 0,
        OFFSPRING_CAPACITY: 0,
    }
    totals_stats_lock = Lock()

    organism_type = "Predator"

    def eat_for_day(self, prey_list):
        self.stored_calories -= self.inherited[CALORIE_USAGE]
        for prey in prey_list:
            if self.inherited[STRENGTH] > prey.inherited[STRENGTH]:
                prey.alive = False
                self.stored_calories += prey.stored_calories
        self.alive = self.stored_calories > 0
        if not self.alive:
            with self.__class__.starved_in_round_lock:
                self.__class__.starved_in_round += 1
            with Ecosystem.alive_count_lock:
                Ecosystem.alive_count -= 1
            with self.__class__.alive_count_lock:
                self.__class__.alive_count -= 1
            with self.totals_stats_lock:
                for trait in self.__class__.totals_stats:
                    self.__class__.totals_stats[trait] -= self.inherited[trait]

    # def confront_day(self, prey_strength, prey_calories=0) -> bool:
    #     food_amount = 0
    #     if not math.isnan(prey_strength) and self.inherited[STRENGTH] > prey_strength:
    #         food_amount = prey_calories

    #     self.stored_calories += food_amount - self.inherited[CALORIE_USAGE]
    #     if self.stored_calories <= 0:
    #         with self.__class__.starved_in_round_lock:
    #             self.__class__.starved_in_round += 1

    #         with Ecosystem.alive_count_lock:
    #             Ecosystem.alive_count -= 1
    #         with self.__class__.alive_count_lock:
    #             self.__class__.alive_count -= 1
    #         with self.totals_stats_lock:
    #             for trait in self.__class__.totals_stats:
    #                 self.__class__.totals_stats[trait] -= self.inherited[trait]
    #         return False
    #     else:
    #         return True
