"""
General traits
- randomly move in 8 directions (unless in edge or corner)

Prey traits
- general
  - eat when on top of food source
  - reproduce when on same square as other prey
  - die when on same square as stronger predator
- optimize
  - daily calorie usage
  - strength (compared to prey)
  - offspring capacity

Predatory traits
- strength (compared to prey)
- never reproduce or die
"""
import numpy as np
import random


class Ecosystem:
  class Prey:
    def __init__(self):
      self.strength = random.randint(0, 10)
      self.stored_calories = 10
      self.calorie_usage = random.randint(0, 5)
      self.offspring_capacity = random.randint(0, 5)

    def new_day(self, eat=0) -> bool:
      self.stored_calories += (eat - self.calorie_usage)
      if not self.stored_calories > 0:
        return False
      else:
        return True

  class Predator:
    def __init__(self):
      self.strength = 5

  def __init__(self, _dims, _predator_count=1, _prey_count=5):
    assert(len(_dims) == 2)
    self.grid = np.zeros(_dims)
    for i in range(_dims[0]):
      for j in range(_dims[1]):
        self.grid[i, j] = {
          "WEAK_PREDATORS": [],
          "STRONG_PREDATOR": None,
          "PREY": [], # TODO: turn to deque
          "FOOD": 0
        }

    self.predators = []
    for _ in range(_predator_count):
        self.predators.append(Ecosystem.Predator())
    self.prey = []
    for _ in range(_prey_count):
        self.prey.append(Ecosystem.Prey())
    self.day = 0  
  
  def run_simulation(self):
    grid_shape = self.grid.shape

    # Initialize predators
    for predator in self.predators:
      p0, p1 = random.randint(0, grid_shape[0] - 1), random.randint(1, grid_shape[1] - 1)
      if self.grid[p0, p1]["STRONG_PREDATOR"]:
        if predator.strength > self.grid[p0, p1]["STRONG_PREDATOR"].strength:
          self.grid[p0, p1]["WEAK_PREDATORS"].append(self.grid[p0, p1]["STRONG_PREDATOR"])
          self.grid[p0, p1]["STRONG_PREDATOR"] = predator
        else:
          self.grid[p0, p1]["WEAK_PREDATORS"].append(predator)
      else:
        self.grid[p0, p1]["STRONG_PREDATOR"] = predator
    
    # Initialize prey
    for prey in self.prey:
      p0, p1 = random.randint(0, grid_shape[0] - 1), random.randint(1, grid_shape[1] - 1)
      self.grid[p0, p1]["PREY"].append(prey)

    # Initialize food
    start_food_source_count = int(grid_shape[0] * grid_shape[1] * 0.2)
    for _ in start_food_source_count:
      p0, p1 = random.randint(0, grid_shape[0] - 1), random.randint(1, grid_shape[1] - 1)
      self.grid[p0, p1] += 1

    # Run simulation
    for _ in range(5):
      # Evaluate current state
      for p0 in range(grid_shape[0]):
        for p1 in range(grid_shape[1]):
          if self.grid[p0, p1]["STRONG_PREDATOR"]:
            if 

