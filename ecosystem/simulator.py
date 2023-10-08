from components import Planet, Organism, Prey, Predator

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


def process_position(ri, ci, day_count):
    for day_num in range(day_count):
        with Planet.worker_state_lock:
            while Planet.worker_state != "PROCESS":
                Planet.worker_state_cv.wait()

        with Planet.grid[ri][ci][0]["POSITION_LOCK"]:
            surviving_prey = []
            for current_prey in Planet.grid[ri][ci][0]["PREY"]:
                if current_prey.confront_day(
                    Planet.grid[ri][ci][0]["PREDATOR_TOP_STRENGTH"],
                    Planet.grid[ri][ci][0]["FOOD"],
                ):
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
                Planet.ready = 0
                Planet.logger.log(f"--- DAY {day_num} ---")
                ecosystem_alive = Organism.display_status()
                with Planet.worker_state_lock:
                    if ecosystem_alive:
                        Planet.worker_state = "TRANSITION"
                        Prey.display_evolution_status()
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
    start_predator_count = 1  # can replace with predator types
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
    assert Organism.display_status()

    # START THREADS
    for ri in range(Planet.grid_shape[0]):
        for ci in range(Planet.grid_shape[1]):
            Thread(target=process_position, args=[ri, ci, day_count]).start()


if __name__ == "__main__":
    run_simulation()
