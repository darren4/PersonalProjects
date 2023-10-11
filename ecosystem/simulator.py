from components import Planet, Ecosystem, Prey, Predator

import random
from threading import Lock, Thread


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


def get_survivors(prey, predators, food):
    surviving_prey = []
    surviving_predators = []
    end_confront_idx = min(len(prey), len(predators))
    for i in range(end_confront_idx):
        current_prey = prey[i]
        current_predator = predators[i]
        if current_prey.confront_day(current_predator.inherited["STRENGTH"], food):
            surviving_prey.append(current_prey)
        if current_predator.confront_day(current_prey.inherited["STRENGTH"]):
            surviving_predators.append(current_predator)
    for i in range(end_confront_idx, len(prey)):
        current_prey = prey[i]
        if current_prey.confront_day(0, food):
            surviving_prey.append(current_prey)
    for i in range(end_confront_idx, len(predators)):
        current_predator = predators[i]
        if current_predator.confront_day(None):
            surviving_predators.append(current_predator)
    return surviving_prey, surviving_predators

def reproduce(parents):
    parents_and_offspring = []
    parents_and_offspring.extend(parents)
    if parents:
        correction = 0
        if len(parents) % 2 == 1:
            correction = 1
        for left_idx in range(0, len(parents) - correction, 2):
            left_parent, right_parent = (
                parents[left_idx],
                parents[left_idx + 1],
            )
            offspring = left_parent.reproduce(right_parent)
            parents_and_offspring.extend(offspring)
    return parents_and_offspring


def process_position(ri, ci, day_count):
    for day_num in range(day_count):
        with Planet.worker_state_lock:
            while Planet.worker_state != "PROCESS":
                Planet.worker_state_cv.wait()

        with Planet.grid[ri][ci][0]["POSITION_LOCK"]:
            surviving_prey, surviving_predators = get_survivors(
                Planet.grid[ri][ci][0]["PREY"],
                Planet.grid[ri][ci][0]["PREDATORS"],
                Planet.grid[ri][ci][0]["FOOD"],
            )

            next_prey = reproduce(surviving_prey)
            next_predators = reproduce(surviving_predators)

            for prey in next_prey:
                new_ri, new_ci = new_position(ri, ci, Planet.grid_shape)
                with Planet.grid[new_ri][new_ci][1]["POSITION_LOCK"]:
                    Planet.grid[new_ri][new_ci][1]["PREY"].append(prey)
            for predator in next_predators:
                new_ri, new_ci = new_position(ri, ci, Planet.grid_shape)
                with Planet.grid[new_ri][new_ci][1]["POSITION_LOCK"]:
                    Planet.grid[new_ri][new_ci][1]["PREDATORS"].append(predator)

        with Planet.ready_lock:
            Planet.ready += 1
            if Planet.ready == Planet.worker_count:
                Planet.ready = 0
                Planet.logger.log(f"--- DAY {day_num} ---")
                ecosystem_alive = Ecosystem.display_status()
                with Planet.worker_state_lock:
                    if ecosystem_alive:
                        Planet.worker_state = "TRANSITION"
                        Prey.display_evolution_status()
                        Predator.display_evolution_status()
                    else:
                        Planet.worker_state = "DONE"
                    Planet.worker_state_cv.notify_all()

        with Planet.worker_state_lock:
            while Planet.worker_state == "PROCESS":
                Planet.worker_state_cv.wait()
            if Planet.worker_state == "DONE":
                return

        with Planet.grid[ri][ci][0]["POSITION_LOCK"]:
            with Planet.grid[ri][ci][1]["POSITION_LOCK"]:
                apply_position(Planet.grid[ri][ci][0], Planet.grid[ri][ci][1])
                apply_position(
                    Planet.grid[ri][ci][1],
                    {
                        "PREDATORS": [],
                        "PREDATOR_TOP_STRENGTH": 0,
                        "PREY": [],
                    },
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
    start_predator_count = 20  # can replace with predator types
    start_prey_count = 10  # can replace with prey types
    start_food_source_count = 5  # can replace with food amounts/positions
    day_count = 10

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
            prey = Prey()
            Planet.grid[ri][ci][0]["PREY"].append(prey)

    Planet.worker_count = Planet.grid_shape[0] * Planet.grid_shape[1]

    Planet.logger.log("--- STARTING POSITION ---")
    assert Ecosystem.display_status()

    # START THREADS
    for ri in range(Planet.grid_shape[0]):
        for ci in range(Planet.grid_shape[1]):
            Thread(target=process_position, args=[ri, ci, day_count]).start()


if __name__ == "__main__":
    run_simulation()
