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
from copy import deepcopy

random.seed(728)

class Ecosystem:
  class Prey:
    alive_count = 0
    def __init__(self, _strength=random.randint(5, 10), _calorie_usage=random.randint(0, 0), _offspring_capacity=random.randint(1, 5)):
      self.inherited = {
        "STRENGTH": _strength,
        "CALORIE_USAGE": _calorie_usage,
        "OFFSPRING_CAPACITY": _offspring_capacity
      }
      self.stored_calories = 10
      Ecosystem.Prey.alive_count += 1

    def starved(self, eat=0) -> bool:
      self.stored_calories += (eat - self.inherited["CALORIE_USAGE"])
      if self.stored_calories <= 0:
        return True
      else:
        return False
      
    def reproduce(self, mate):
      offspring = []
      for _ in range(min(self.inherited["OFFSPRING_CAPACITY"], mate.inherited["OFFSPRING_CAPACITY"])):
        new_traits = {}
        for trait, value in self.inherited.items():
          if random.randint(0, 1):
            new_traits[trait] = value
          else:
            new_traits[trait] = mate.inherited[trait]
        offspring.append(Ecosystem.Prey(new_traits["STRENGTH"], new_traits["CALORIE_USAGE"], new_traits["OFFSPRING_CAPACITY"]))
      return offspring
      

  class Predator:
    def __init__(self):
      self.strength = 5

  def __init__(self, _dims, _predator_count=1, _prey_count=5):
    assert(isinstance(_dims, tuple) and len(_dims) == 2)
    position_start_state = {
          "WEAK_PREDATORS": [],
          "STRONG_PREDATOR": None,
          "PREY": [],
          "FOOD": 0
        }
    self.grid_shape = _dims
    self.grid = []
    for ri in range(_dims[0]):
      self.grid.append([])
      for ci in range(_dims[1]):
        self.grid[-1].append(deepcopy(position_start_state))

    self.predators = []
    for _ in range(_predator_count):
        self.predators.append(Ecosystem.Predator())
    self.prey = []
    for _ in range(_prey_count):
        self.prey.append(Ecosystem.Prey())
    self.day = 0

  def new_position(self, p0, p1):
    valid_positions = []
    if p0 + 1 < self.grid_shape[0] and p1 + 1 < self.grid_shape[1]:
      # Bottom right
      valid_positions.append((p0 + 1, p1 + 1))
    if p0 + 1 < self.grid_shape[0]:
      # Bottom
      valid_positions.append((p0 + 1, p1))
    if p0 + 1 < self.grid_shape[0] and p1 - 1 >= 0:
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
    if p0 - 1 >= 0 and p1 + 1 < self.grid_shape[1]:
      # Top right
      valid_positions.append((p0 - 1, p1 + 1))
    if p1 + 1 < self.grid_shape[1]:
      # Right
      valid_positions.append((p0, p1 + 1))

    random_position = random.randint(0, len(valid_positions) - 1)
    return valid_positions[random_position]
  
  def run_simulation(self):
    print("Initializing food")
    start_food_source_count = int(self.grid_shape[0] * self.grid_shape[1] * 0.2)
    for _ in range(start_food_source_count):
      p0, p1 = random.randint(0, self.grid_shape[0] - 1), random.randint(0, self.grid_shape[1] - 1)
      self.grid[p0][p1]["FOOD"] += 1
    
    reset_grid = deepcopy(self.grid)

    print("Initializing predators")
    for predator in self.predators:
      p0, p1 = random.randint(0, self.grid_shape[0] - 1), random.randint(0, self.grid_shape[1] - 1)
      if self.grid[p0][p1]["STRONG_PREDATOR"]:
        if predator.strength > self.grid[p0][p1]["STRONG_PREDATOR"].strength:
          self.grid[p0][p1]["WEAK_PREDATORS"].append(self.grid[p0][p1]["STRONG_PREDATOR"])
          self.grid[p0][p1]["STRONG_PREDATOR"] = predator
        else:
          self.grid[p0][p1]["WEAK_PREDATORS"].append(predator)
      else:
        self.grid[p0][p1]["STRONG_PREDATOR"] = predator
    
    print("Initializing prey")
    for prey in self.prey:
      p0, p1 = random.randint(0, self.grid_shape[0] - 1), random.randint(0, self.grid_shape[1] - 1)
      self.grid[p0][p1]["PREY"].append(prey)
    print(f"Initialized {Ecosystem.Prey.alive_count} prey")

    print("Starting simulation")
    for day in range(10):
      print(f"--- Day {day} ---")
      next_grid = deepcopy(reset_grid)
      for p0 in range(self.grid_shape[0]):
        for p1 in range(self.grid_shape[1]):
          # Display position status
          # print(f"Position ({p0}, {p1}) starting")
          # print(f"Prey count: {len(self.grid[p0][p1]['PREY'])}")
          # if self.grid[p0][p1]['STRONG_PREDATOR']:
          #   print(f"Predator strength: {self.grid[p0][p1]['STRONG_PREDATOR'].strength}")
          # print(f"Food quantity: {self.grid[p0][p1]['FOOD']}")
          
          # Process surviving prey
          surviving_prey = []
          for _ in range(len(self.grid[p0][p1]["PREY"])):
            current_prey = self.grid[p0][p1]["PREY"].pop()
            survived = True

            if self.grid[p0][p1]["STRONG_PREDATOR"] and current_prey.inherited["STRENGTH"] < self.grid[p0][p1]["STRONG_PREDATOR"].strength:
              print("Prey eaten")
              Ecosystem.Prey.alive_count -= 1
              survived = False

            food_amount = self.grid[p0][p1]["FOOD"]
            if current_prey.starved(food_amount):
              print("Prey starved")
              Ecosystem.Prey.alive_count -= 1
              survived = False

            if survived:
              new_p0, new_p1 = self.new_position(p0, p1)
              next_grid[new_p0][new_p1]["PREY"].append(current_prey)
              surviving_prey.append(current_prey)
          
          # Process reproduction
          if surviving_prey:
            random.shuffle(surviving_prey)
            correction = 0
            if len(surviving_prey) % 2 == 1:
              correction = 1
            for left_idx in range(0, len(surviving_prey) - correction, 2):
              left_prey, right_prey = surviving_prey[left_idx], surviving_prey[left_idx + 1]
              new_prey = left_prey.reproduce(right_prey)
              for prey in new_prey:
                new_p0, new_p1 = self.new_position(p0, p1)
                next_grid[new_p0][new_p1]["PREY"].append(prey)

          # Process moving predators
          if self.grid[p0][p1]["STRONG_PREDATOR"]:
            self.grid[p0][p1]["WEAK_PREDATORS"].append(self.grid[p0][p1]["STRONG_PREDATOR"])
          self.grid[p0][p1]["STRONG_PREDATOR"] = None
          for predator in self.grid[p0][p1]["WEAK_PREDATORS"]:
            new_p0, new_p1 = self.new_position(p0, p1)
            if next_grid[new_p0][new_p1]["STRONG_PREDATOR"]:
              if predator.strength > next_grid[new_p0][new_p1]["STRONG_PREDATOR"].strength:
                next_grid[new_p0][new_p1]["WEAK_PREDATORS"].append(next_grid[new_p0][new_p1]["STRONG_PREDATOR"])
                next_grid[new_p0][new_p1]["STRONG_PREDATOR"] = predator
              else:
                next_grid[new_p0][new_p1]["WEAK_PREDATORS"].append(predator)
            else:
              next_grid[new_p0][new_p1]["STRONG_PREDATOR"] = predator
      self.grid = next_grid

      # Process day aftermath
      print(f"Alive prey: {Ecosystem.Prey.alive_count}")
      if Ecosystem.Prey.alive_count == 0:
        return

      # TODO display grid each day
      prey_counts = np.zeros((self.grid_shape))
      for p0 in range(self.grid_shape[0]):
        for p1 in range(self.grid_shape[1]):
          prey_counts[p0, p1] = len(self.grid[p0][p1]["PREY"])
      print(prey_counts)

      # TODO write output to file


if __name__ == "__main__":
  e = Ecosystem((10, 10))
  e.run_simulation()
          

