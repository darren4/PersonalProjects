from components import Planet, Ecosystem, Prey, Predator
from constants import *

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
    target[PREDATORS].clear()
    target[PREY].clear()
    for predator in source[PREDATORS]:
        target[PREDATORS].append(predator)
    for prey in source[PREY]:
        target[PREY].append(prey)


def get_survivors(prey, predators, food):
    random.shuffle(prey)
    random.shuffle(predators)

    prey_count = len(prey)
    predator_count = len(predators)

    surviving_prey = []
    surviving_predators = []

    if predator_count > 0:
        predators_to_prey = []
        for i in range(predator_count):
            predators_to_prey.append((predators[i], []))
        if prey_count <= predator_count:
            for i in range(prey_count):
                predators_to_prey[i][1].append(prey[i])
        else:
            predator_idx = 0
            for prey_idx in range(prey_count):
                if predator_idx == predator_count:
                    predator_idx = 0

                predators_to_prey[predator_idx][1].append(prey[prey_idx])
                predator_idx += 1

        for predator, victims in predators_to_prey:
            predator.eat_for_day(victims)
            if predator.still_alive():
                surviving_predators.append(predator)

    for one_prey in prey:
        if one_prey.still_alive():
            one_prey.eat_for_day([food])
            if one_prey.still_alive():
                surviving_prey.append(one_prey)
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


def display_ecosystem_status(day_num):
    ecosystem_alive = Ecosystem.display_status() > 0
    Prey.display_status()
    Predator.display_status()

    Prey.display_evolution_status()
    Prey.reset_round_status()
    Predator.display_evolution_status()
    Predator.reset_round_status()

    if day_num % 10 == 0:
        Ecosystem.save_status_history()
        Prey.save_status_history()
        Predator.save_status_history()
        Prey.save_evolution_history()
        Predator.save_evolution_history()

    return ecosystem_alive


def process_position(ri, ci, day_count):
    for day_num in range(day_count):
        with Planet.worker_state_lock:
            while Planet.worker_state != PROCESS:
                Planet.worker_state_cv.wait()

        with Planet.grid[ri][ci][0][POSITION_LOCK]:
            surviving_prey, surviving_predators = get_survivors(
                Planet.grid[ri][ci][0][PREY],
                Planet.grid[ri][ci][0][PREDATORS],
                Planet.grid[ri][ci][0][FOOD],
            )

            next_prey = reproduce(surviving_prey)
            next_predators = reproduce(surviving_predators)

            for prey in next_prey:
                new_ri, new_ci = new_position(ri, ci, Planet.grid_shape)
                with Planet.grid[new_ri][new_ci][1][POSITION_LOCK]:
                    Planet.grid[new_ri][new_ci][1][PREY].append(prey)
            for predator in next_predators:
                new_ri, new_ci = new_position(ri, ci, Planet.grid_shape)
                with Planet.grid[new_ri][new_ci][1][POSITION_LOCK]:
                    Planet.grid[new_ri][new_ci][1][PREDATORS].append(predator)

        with Planet.ready_lock:
            Planet.ready += 1
            if Planet.ready == Planet.worker_count:
                # Single threaded
                Planet.ready = 0
                ecosystem_alive = display_ecosystem_status(day_num)
                with Planet.worker_state_lock:
                    if ecosystem_alive:
                        Planet.worker_state = TRANSITION
                    else:
                        Planet.worker_state = DONE
                    Planet.worker_state_cv.notify_all()

        with Planet.worker_state_lock:
            while Planet.worker_state == PROCESS:
                Planet.worker_state_cv.wait()
            if Planet.worker_state == DONE:
                return

        with Planet.grid[ri][ci][0][POSITION_LOCK]:
            with Planet.grid[ri][ci][1][POSITION_LOCK]:
                apply_position(Planet.grid[ri][ci][0], Planet.grid[ri][ci][1])
                apply_position(
                    Planet.grid[ri][ci][1],
                    {
                        PREDATORS: [],
                        PREY: [],
                    },
                )

        with Planet.ready_lock:
            Planet.ready += 1
            if Planet.ready == Planet.worker_count:
                # Single threaded
                Planet.ready = 0
                with Planet.worker_state_lock:
                    Planet.worker_state = PROCESS
                    Planet.worker_state_cv.notify_all()


def run_simulation():
    # Potential user inputs
    Planet.grid_shape = (15, 15)
    start_predator_count = 45
    start_prey_count = 45
    start_food_source_count = 225
    day_count = 150

    def get_prey_starting_traits():
        return {
            STRENGTH: random.randint(0, 5),
            OFFSPRING_CAPACITY: random.randint(0, 4),
            CALORIE_USAGE: random.randint(1, 2),
        }

    prey_starting_calories = 5

    def get_predator_starting_traits():
        return {
            STRENGTH: random.randint(3, 7),
            OFFSPRING_CAPACITY: random.randint(0, 4),
            CALORIE_USAGE: random.uniform(0, 0.25),
        }

    predator_starting_calories = 1

    Planet.grid = []
    for ri in range(Planet.grid_shape[0]):
        Planet.grid.append([])
        for ci in range(Planet.grid_shape[1]):
            Planet.grid[-1].append(
                (
                    {
                        PREDATORS: [],
                        PREY: [],
                        FOOD: 0,
                        POSITION_LOCK: Lock(),
                    },
                    {
                        PREDATORS: [],
                        PREY: [],
                        FOOD: 0,
                        POSITION_LOCK: Lock(),
                    },
                )
            )

    for _ in range(start_food_source_count):
        ri, ci = random.randint(0, Planet.grid_shape[0] - 1), random.randint(
            0, Planet.grid_shape[1] - 1
        )
        with Planet.grid[ri][ci][0][POSITION_LOCK]:
            Planet.grid[ri][ci][0][FOOD] += 1
            Planet.grid[ri][ci][1][FOOD] += 1

    for _ in range(start_prey_count):
        ri, ci = random.randint(0, Planet.grid_shape[0] - 1), random.randint(
            0, Planet.grid_shape[1] - 1
        )
        with Planet.grid[ri][ci][0][POSITION_LOCK]:
            prey = Prey(
                _inherited=get_prey_starting_traits(),
                starting_calories=prey_starting_calories,
            )
            Planet.grid[ri][ci][0][PREY].append(prey)

    for _ in range(start_predator_count):
        ri, ci = random.randint(0, Planet.grid_shape[0] - 1), random.randint(
            0, Planet.grid_shape[1] - 1
        )
        with Planet.grid[ri][ci][0][POSITION_LOCK]:
            predator = Predator(
                _inherited=get_predator_starting_traits(),
                starting_calories=predator_starting_calories,
            )
            Planet.grid[ri][ci][0][PREDATORS].append(predator)

    Planet.worker_count = Planet.grid_shape[0] * Planet.grid_shape[1]

    assert Ecosystem.display_status() > 0
    Prey.display_status()
    Predator.display_status()
    Prey.display_evolution_status()
    Predator.display_evolution_status()
    # START THREADS
    threads = []
    for ri in range(Planet.grid_shape[0]):
        for ci in range(Planet.grid_shape[1]):
            t = Thread(target=process_position, args=[ri, ci, day_count])
            t.start()
            threads.append(t)
    for thread in threads:
        thread.join()
    # Ecosystem.save_status_history()
    # Prey.save_status_history()
    # Predator.save_status_history()
    # Prey.save_evolution_history()
    # Predator.save_evolution_history()
    print("Done")


if __name__ == "__main__":
    run_simulation()
