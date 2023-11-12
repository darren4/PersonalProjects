from typing import List, Tuple
import random

"""
Genetic algo attributes
Inheritance: average values, take alternating values, take values randomly
Mate selection: random, more fit/less fit
Mating rounds: pair (or other) produces many children, more rounds with less children each
"""


def genetic_algo_one_round(population: List[Tuple[float, List[float]]]):
    """
    population: list of members
        each member as tuple(<fitness>, <list of attributes>)
    """
    population_size = len(population)
    if population_size % 4 != 0:
        raise ValueError(f"Population size {population_size} not divisible by 4")

    population.sort(reverse=True)
    fit_population = population[: int(population_size / 2)]
    children = []

    for _ in range(4):
        random.shuffle(fit_population)
        for parent_idx in range(0, len(fit_population), 2):
            parent0 = fit_population[parent_idx][1]
            parent1 = fit_population[parent_idx + 1][1]
            if len(parent0) != len(parent1):
                raise ValueError("Attribute lists not same len")
            child = []

            for attr_idx in range(len(parent0)):
                if random.randint(0, 1):
                    child.append(parent0[attr_idx])
                else:
                    child.append(parent1[attr_idx])
            children.append(child)
    assert len(children) == population_size
    return children


if __name__ == "__main__":
    list_of_tuples = [
        (2, [3, 7, 1]),
        (8, [9, 9, 9]),
        (1, [2, 3, 6]),
        (5, [8, 8, 8]),
    ]
    print(genetic_algo_one_round(list_of_tuples))
