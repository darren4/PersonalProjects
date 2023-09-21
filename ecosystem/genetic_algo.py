from typing import List, Tuple
import random
import numpy as np
import math

"""
Genetic algo considerations
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
    fit_population = population[:int(population_size/2)]
    children = []

    for _ in range(4):
        random.shuffle(fit_population)
        for parent_idx in range(0, len(fit_population), 2):
            parent0 = fit_population[parent_idx][1]
            parent1 = fit_population[parent_idx+1][1]
            if len(parent0) != len(parent1):
                raise ValueError("Attribute lists not same len")
            child = []

            for attr_idx in range(len(parent0)):
                if random.randint(0, 1):
                    child.append(parent0[attr_idx])
                else:
                    child.append(parent1[attr_idx])
            children.append(child)
    assert(len(children) == population_size)
    return children


if __name__ == "__main__":
    def distance(organism, target):
        return np.linalg.norm(np.abs(np.array(organism) - np.array(target)))

    target = [1, 2, 3]
    population = []
    for i in range(32):
        organism = []
        for j in range(3):
            organism.append(random.randint(0, 50))
        population.append(organism)

    for round_num in range(50):
        total_fitness = 0
        for i in range(len(population)):
            organism = population[i]
            fitness = -1 * distance(organism, target)
            total_fitness += fitness
            population[i] = (fitness, organism)
        average_fitness = total_fitness / len(population)
        print(f"Average fitness in round {round_num}: {average_fitness}")
        population = genetic_algo_one_round(population)

    best_organism = None
    best_fitness = -math.inf
    for organism in population:
        fitness = distance(organism, target)
        if fitness > best_fitness:
            best_fitness = fitness
            best_organism = organism
    print(f"Final best fitness: {best_fitness}")
    print(f"Best organism: {best_organism}")
