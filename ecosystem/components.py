import random
from threading import Lock, Condition


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


class Organism:
    alive_count = 0
    alive_count_lock = Lock()

    @staticmethod
    def display_status():
        with Organism.alive_count_lock:
            alive_count = Organism.alive_count
            Planet.logger.log(f"Organism count: {alive_count}")
        Prey.display_status()
        Prey.reset_round_status()
        return alive_count

    @staticmethod
    def born():
        with Organism.alive_count_lock:
            Organism.alive_count += 1

    @staticmethod
    def died():
        with Organism.alive_count_lock:
            Organism.alive_count -= 1

    def generate_offspring(self, mate):
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
            offspring.append(Prey(new_traits))
        return offspring


class Predator(Organism):
    alive_count = 0
    alive_count_lock = Lock()

    starved_in_round = 0
    starved_in_round_lock = Lock()
    created_in_round = 0
    created_in_round_lock = Lock()

    def __init__(self, _strength=50):
        self.strength = _strength

    def reproduce(self, mate):
        offspring = self.generate_offspring(mate)
        with Predator.created_in_round_lock:
            Predator.created_in_round += len(offspring)
        return offspring

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

    def __init__(self, _inherited=None):
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
        self.born()

    @staticmethod
    def display_status():
        with Prey.alive_count_lock:
            Planet.logger.log(f"Prey alive count: {Prey.alive_count}")
        Planet.logger.log("Prey round changes:")
        with Prey.starved_in_round_lock:
            Planet.logger.log(f"    Starved: {Prey.starved_in_round}")
        with Prey.eaten_in_round_lock:
            Planet.logger.log(f"    Eaten: {Prey.eaten_in_round}")
        with Prey.created_in_round_lock:
            Planet.logger.log(f"    Created: {Prey.created_in_round}")

    @staticmethod
    def reset_round_status():
        with Prey.starved_in_round_lock:
            Prey.starved_in_round = 0
        with Prey.eaten_in_round_lock:
            Prey.eaten_in_round = 0
        with Prey.created_in_round_lock:
            Prey.created_in_round = 0

    @staticmethod
    def display_evolution_status():
        with Prey.totals_stats_lock:
            Planet.logger.log("---", msg_type="EVOLVE")
            for trait in Prey.totals_stats:
                avg = Prey.totals_stats[trait] / Prey.alive_count
                Planet.logger.log(f"Avg {trait}: {round(avg, 2)}", msg_type="EVOLVE")

    def born(self):
        Organism.born()
        with Prey.alive_count_lock:
            Prey.alive_count += 1
        with Prey.totals_stats_lock:
            for trait in Prey.totals_stats:
                Prey.totals_stats[trait] += self.inherited[trait]

    def died(self):
        Organism.died()
        with Prey.alive_count_lock:
            Prey.alive_count -= 1
        with Prey.totals_stats_lock:
            for trait in Prey.totals_stats:
                Prey.totals_stats[trait] -= self.inherited[trait]

    def confront_day(self, predator_strength=0, eat=0) -> bool:
        still_alive = True
        if self.inherited["STRENGTH"] < predator_strength:
            still_alive = False
            with Prey.eaten_in_round_lock:
                Prey.eaten_in_round += 1

        self.stored_calories += eat - self.inherited["CALORIE_USAGE"]
        if self.stored_calories <= 0:
            still_alive = False
            with Prey.starved_in_round_lock:
                Prey.starved_in_round += 1

        if not still_alive:
            self.died()
        return still_alive

    def reproduce(self, mate):
        offspring = self.generate_offspring(mate)
        with Prey.created_in_round_lock:
            Prey.created_in_round += len(offspring)
        return offspring
