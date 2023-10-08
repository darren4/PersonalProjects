import random
from threading import Lock, Thread, Condition


class Planet:
    grid = None
    grid_shape = None  # TODO: make reader lock

    ready = 0
    ready_lock = Lock()
    ready_cv = Condition(ready_lock)
    worker_count = None

    # PROCESS, TRANSITION
    worker_state = "PROCESS"
    worker_state_lock = Lock()
    worker_state_cv = Condition(worker_state_lock)

    DAY_COUNT = None


class Organism:
    alive_count = 0
    alive_count_lock = Lock()


class Predator(Organism):
    def __init__(self, _strength=5):
        self.strength = _strength


class Prey(Organism):
    alive_count = 0
    alive_count_lock = Lock()

    def __init__(
        self,
        _strength: int = random.randint(5, 10),
        _calorie_usage: int = random.randint(0, 3),
        _offspring_capacity: int = random.randint(1, 5),
    ):
        self.inherited = {
            "STRENGTH": _strength,
            "CALORIE_USAGE": _calorie_usage,
            "OFFSPRING_CAPACITY": _offspring_capacity,
        }
        self.stored_calories = 10
        with Organism.alive_count_lock:
            Organism.alive_count += 1
        with Prey.alive_count_lock:
            Prey.alive_count += 1

    def starved(self, eat=0) -> bool:
        self.stored_calories += eat - self.inherited["CALORIE_USAGE"]
        if self.stored_calories <= 0:
            return True
        else:
            return False

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
            offspring.append(
                Prey(
                    new_traits["STRENGTH"],
                    new_traits["CALORIE_USAGE"],
                    new_traits["OFFSPRING_CAPACITY"],
                )
            )
        return offspring


def new_position(ri, ci, grid_shape):
    valid_positions = []
    if ri + 1 < grid_shape[0] and ci + 1 < grid_shape[1]:
        # Bottom right
        valid_positions.append((ri + 1, ci + 1))
    if ri + 1 < grid_shape[0]:
        # Bottom
        valid_positions.append((ri + 1, ci))
    if ri + 1 < grid_shape[0] and ci - 1 >= 0:
        # Bottom left
        valid_positions.append((ri + 1, ci - 1))
    if ci - 1 >= 0:
        # Left
        valid_positions.append((ri, ci - 1))
    if ri - 1 >= 0 and ci - 1 >= 0:
        # Top left
        valid_positions.append((ri - 1, ci - 1))
    if ri - 1 >= 0:
        # Top
        valid_positions.append((ri - 1, ci))
    if ri - 1 >= 0 and ci + 1 < grid_shape[1]:
        # Top right
        valid_positions.append((ri - 1, ci + 1))
    if ci + 1 < grid_shape[1]:
        # Right
        valid_positions.append((ri, ci + 1))

    random_position = random.randint(0, len(valid_positions) - 1)
    return valid_positions[random_position]


def apply_position(target, source):
    target["PREDATORS"].clear()
    target["PREY"].clear()
    for predator in source["PREDATORS"]:
        target["PREDATORS"].append(predator)
    for prey in source["PREY"]:
        target["PREY"].append(prey)

    target["PREDATOR_TOP_STRENGTH"] = source["PREDATOR_TOP_STRENGTH"]


def process_position(ri, ci):
    for day_num in range(Planet.DAY_COUNT):
        with Organism.alive_count_lock:
            if not Organism.alive_count:
                return

        with Planet.worker_state_lock:
            while Planet.worker_state != "PROCESS":
                Planet.worker_state_cv.wait()

        with Planet.grid[ri][ci][0]["POSITION_LOCK"]:
            surviving_prey = []
            for current_prey in Planet.grid[ri][ci][0]["PREY"]:
                if current_prey.inherited["STRENGTH"] < Planet.grid[ri][ci][0][
                    "PREDATOR_TOP_STRENGTH"
                ] or current_prey.starved(Planet.grid[ri][ci][0]["FOOD"]):
                    with Prey.alive_count_lock:
                        Prey.alive_count -= 1
                    with Organism.alive_count_lock:
                        Organism.alive_count -= 1
                else:
                    surviving_prey.append(current_prey)

            next_prey = []
            next_prey.extend(surviving_prey)
            if surviving_prey:
                random.shuffle(surviving_prey)
                correction = 0
                if len(surviving_prey) % 2 == 1:
                    correction = 1
                for left_idx in range(0, len(surviving_prey) - correction, 2):
                    left_prey, right_prey = (
                        surviving_prey[left_idx],
                        surviving_prey[left_idx + 1],
                    )
                    new_prey = left_prey.reproduce(right_prey)
                    next_prey.extend(new_prey)

            for prey in next_prey:
                new_ri, new_ci = new_position(ri, ci, Planet.grid_shape)
                with Planet.grid[new_ri][new_ci][1]["POSITION_LOCK"]:
                    Planet.grid[new_ri][new_ci][1]["PREY"].append(prey)

            for predator in Planet.grid[ri][ci][0]["PREDATORS"]:
                new_ri, new_ci = new_position(ri, ci, Planet.grid_shape)
                with Planet.grid[new_ri][new_ci][1]["POSITION_LOCK"]:
                    Planet.grid[new_ri][new_ci][1]["PREDATORS"].append(predator)
                    Planet.grid[new_ri][new_ci][1]["PREDATOR_TOP_STRENGTH"] = max(
                        Planet.grid[ri][ci][0]["PREDATOR_TOP_STRENGTH"],
                        predator.strength,
                    )

        with Planet.ready_lock:
            Planet.ready += 1
            if Planet.ready == Planet.worker_count:
                print(f"--- Post Day {day_num} ---")
                with Organism.alive_count_lock:
                    print(f"Organism alive count: {Organism.alive_count}")
                Planet.ready = 0
                with Planet.worker_state_lock:
                    Planet.worker_state = "TRANSITION"
                    Planet.worker_state_cv.notify_all()

        with Planet.worker_state_lock:
            while Planet.worker_state != "TRANSITION":
                Planet.worker_state_cv.wait()

        with Planet.grid[ri][ci][0]["POSITION_LOCK"]:
            with Planet.grid[ri][ci][1]["POSITION_LOCK"]:
                apply_position(Planet.grid[ri][ci][0], Planet.grid[ri][ci][1])
                apply_position(
                    {
                        "PREDATORS": [],
                        "PREDATOR_TOP_STRENGTH": 0,
                        "PREY": [],
                    },
                    Planet.grid[ri][ci][1],
                )

        with Planet.ready_lock:
            Planet.ready += 1
            if Planet.ready == Planet.worker_count:
                Planet.ready = 0
                with Planet.worker_state_lock:
                    Planet.worker_state = "PROCESS"
                    Planet.worker_state_cv.notify_all()


def run_simulation():
    # Potential user inputs
    Planet.grid_shape = (10, 10)
    start_predator_count = 1  # can replace with predator types
    start_prey_count = 10  # can replace with prey types
    start_food_source_count = 5  # can replace with food amounts/positions
    Planet.DAY_COUNT = 3
    prey_calorie_usage = 0  # prey never starve

    Planet.grid = []
    for ri in range(Planet.grid_shape[0]):
        Planet.grid.append([])
        for ci in range(Planet.grid_shape[1]):
            Planet.grid[-1].append(
                (
                    {
                        "PREDATORS": [],
                        "PREDATOR_TOP_STRENGTH": 0,
                        "PREY": [],
                        "FOOD": 0,
                        "POSITION_LOCK": Lock(),
                    },
                    {
                        "PREDATORS": [],
                        "PREDATOR_TOP_STRENGTH": 0,
                        "PREY": [],
                        "FOOD": 0,
                        "POSITION_LOCK": Lock(),
                    },
                )
            )

    for _ in range(start_food_source_count):
        ri, ci = random.randint(0, Planet.grid_shape[0] - 1), random.randint(
            0, Planet.grid_shape[1] - 1
        )
        with Planet.grid[ri][ci][0]["POSITION_LOCK"]:
            Planet.grid[ri][ci][0]["FOOD"] += 1
            Planet.grid[ri][ci][1]["FOOD"] += 1

    for _ in range(start_predator_count):
        ri, ci = random.randint(0, Planet.grid_shape[0] - 1), random.randint(
            0, Planet.grid_shape[1] - 1
        )
        with Planet.grid[ri][ci][0]["POSITION_LOCK"]:
            predator = Predator()
            Planet.grid[ri][ci][0]["PREDATORS"].append(predator)
            Planet.grid[ri][ci][0]["PREDATOR_TOP_STRENGTH"] = max(
                Planet.grid[ri][ci][0]["PREDATOR_TOP_STRENGTH"], predator.strength
            )

    for _ in range(start_prey_count):
        ri, ci = random.randint(0, Planet.grid_shape[0] - 1), random.randint(
            0, Planet.grid_shape[1] - 1
        )
        with Planet.grid[ri][ci][0]["POSITION_LOCK"]:
            prey = Prey(_calorie_usage=prey_calorie_usage)
            Planet.grid[ri][ci][0]["PREY"].append(prey)

    Planet.worker_count = Planet.grid_shape[0] * Planet.grid_shape[1]

    # START THREADS
    for ri in range(Planet.grid_shape[0]):
        for ci in range(Planet.grid_shape[1]):
            Thread(target=process_position, args=[ri, ci]).start()


if __name__ == "__main__":
    run_simulation()
