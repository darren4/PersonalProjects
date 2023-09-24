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
from collections import deque
from copy import deepcopy


class Ecosystem:
  class Prey:
    alive_count = 0
    def __init__(self):
      self.strength = random.randint(0, 10)
      self.stored_calories = 10
      self.calorie_usage = random.randint(0, 5)
      self.offspring_capacity = random.randint(0, 5)
      self.alive_count += 1

    def starved(self, eat=0) -> bool:
      self.stored_calories += (eat - self.calorie_usage)
      if self.stored_calories <= 0:
        return True
      else:
        self.alive_count -= 1
        return False

  class Predator:
    def __init__(self):
      self.strength = 5

  def __init__(self, _dims, _predator_count=1, _prey_count=5):
    assert(len(_dims) == 2)
    self.grid = np.full((_dims[0], _dims[1]), {
          "WEAK_PREDATORS": [],
          "STRONG_PREDATOR": None,
          "PREY": deque(),
          "FOOD": 0
        })

    self.predators = []
    for _ in range(_predator_count):
        self.predators.append(Ecosystem.Predator())
    self.prey = []
    for _ in range(_prey_count):
        self.prey.append(Ecosystem.Prey())
    self.day = 0

  def new_position(self, p0, p1):
    grid_shape = self.grid.shape
    valid_positions = []
    if p0 + 1 < grid_shape[0] and p1 + 1 < grid_shape[1]:
      # Bottom right
      valid_positions.append((p0 + 1, p1 + 1))
    if p0 + 1 < grid_shape[0]:
      # Bottom
      valid_positions.append((p0 + 1, p1))
    if p0 + 1 < grid_shape[0] and p1 - 1 >= 0:
      # Bottom left
      valid_positions.append((p0 + 1, p1 - 1))
    if p1 - 1 >= 0:
      # Left
      valid_positions.append((p0, p1 - 1))
    if p0 - 1 >= 0 and p1 - 1 >= 0:
      # Top left
      valid_positions.append((p0 - 1, p1 - 1))
    if p0 - 1 >= 0:
      # Top
      valid_positions.append((p0 - 1, p1))
    if p0 - 1 >= 0 and p1 + 1 < grid_shape[1]:
      # Top right
      valid_positions.append((p0 - 1, p1 + 1))
    if p1 + 1 < grid_shape[1]:
      # Right
      valid_positions.append((p0, p1 + 1))

    random_position = random.randint(0, len(valid_positions) - 1)
    return valid_positions[random_position]
  
  def run_simulation(self):
    grid_shape = self.grid.shape

    print("Initializing food")
    start_food_source_count = int(grid_shape[0] * grid_shape[1] * 0.2)
    for _ in range(start_food_source_count):
      p0, p1 = random.randint(0, grid_shape[0] - 1), random.randint(1, grid_shape[1] - 1)
      self.grid[p0, p1]["FOOD"] += 1
    reset_grid = deepcopy(self.grid)

    print("Initializing predators")
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
    
    print("Initializing prey")
    for prey in self.prey:
      p0, p1 = random.randint(0, grid_shape[0] - 1), random.randint(1, grid_shape[1] - 1)
      self.grid[p0, p1]["PREY"].append(prey)
    print("Initialized prey")

    print("Starting simulation")
    for day in range(5):
      print(f"--- Day {day} ---")
      next_grid = deepcopy(reset_grid)
      for p0 in range(grid_shape[0]):
        for p1 in range(grid_shape[1]):
          # Process surviving prey
          for _ in range(len(self.grid[p0, p1]["PREY"])):
            current_prey = self.grid[p0, p1]["PREY"].pop()
            survived = True

            if self.grid[p0, p1]["STRONG_PREDATOR"] and current_prey.strength < self.grid[p0, p1]["STRONG_PREDATOR"].strength:
              survived = False

            food_amount = self.grid[p0, p1]["FOOD"]
            if current_prey.starved(food_amount):
              survived = False

            if survived:
              new_p0, new_p1 = self.new_position(p0, p1)
              next_grid[new_p0, new_p1]["PREY"].append(current_prey)

          # Process mvoing predators
          if self.grid[p0, p1]["STRONG_PREDATOR"]:
            self.grid[p0, p1]["WEAK_PREDATORS"].append(self.grid[p0, p1]["STRONG_PREDATOR"])
          self.grid[p0, p1]["STRONG_PREDATOR"] = None
          for predator in self.grid[p0, p1]["WEAK_PREDATORS"]:
            new_p0, new_p1 = self.new_position(p0, p1)
            if next_grid[new_p0, new_p1]["STRONG_PREDATOR"]:
              if predator.strength > next_grid[new_p0, new_p1]["STRONG_PREDATOR"].strength:
                next_grid[new_p0, new_p1]["WEAK_PREDATORS"].append(next_grid[new_p0, new_p1]["STRONG_PREDATOR"])
                next_grid[new_p0, new_p1]["STRONG_PREDATOR"] = predator
              else:
                next_grid[new_p0, new_p1]["WEAK_PREDATORS"].append(predator)
            else:
              next_grid[new_p0, new_p1]["STRONG_PREDATOR"] = predator

      # Process day aftermath
      print(f"Alive prey: {Ecosystem.Prey.alive_count}")


if __name__ == "__main__":
  e = Ecosystem((3, 3))
  e.run_simulation()
          

