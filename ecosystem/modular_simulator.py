import random
from copy import deepcopy
from threading import Lock, Thread, Condition

random.seed(728)


class Organism:
  grid_shape = None
  grid = None

  day = int("nan")
  day_lock = Lock()

  alive_count = int("nan")
  alive_count_lock = Lock()

  processing_count = int("nan")
  processing_count_lock = Lock()
  processing_count_cv = Condition(processing_count_lock)

  @staticmethod
  def new_position(p0, p1):
    valid_positions = []
    if p0 + 1 < Organism.grid_shape[0] and p1 + 1 < Organism.grid_shape[1]:
      # Bottom right
      valid_positions.append((p0 + 1, p1 + 1))
    if p0 + 1 < Organism.grid_shape[0]:
      # Bottom
      valid_positions.append((p0 + 1, p1))
    if p0 + 1 < Organism.grid_shape[0] and p1 - 1 >= 0:
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
    if p0 - 1 >= 0 and p1 + 1 < Organism.grid_shape[1]:
      # Top right
      valid_positions.append((p0 - 1, p1 + 1))
    if p1 + 1 < Organism.grid_shape[1]:
      # Right
      valid_positions.append((p0, p1 + 1))

    random_position = random.randint(0, len(valid_positions) - 1)
    return valid_positions[random_position]

class Predator:
  def __init__(self, _strength=5):
    self.strength = _strength

class Prey:
  alive_count = 0
  def __init__(self, _strength: int=random.randint(5, 10), _calorie_usage: int=random.randint(0, 0), _offspring_capacity: int=random.randint(1, 5)):
    self.inherited = {
      "STRENGTH": _strength,
      "CALORIE_USAGE": _calorie_usage,
      "OFFSPRING_CAPACITY": _offspring_capacity
    }
    self.stored_calories = 10
    Prey.alive_count += 1

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
      offspring.append(Prey(new_traits["STRENGTH"], new_traits["CALORIE_USAGE"], new_traits["OFFSPRING_CAPACITY"]))
    return offspring

def run_simulation():
  # Potential user inputs
  Organism.grid_shape = (10, 10)
  start_predator_count = 1 # can replace with predator types
  start_prey_count = 10 # can replace with prey types
  start_food_source_count = 5 # can replace with food amounts/positions
  day_count = 10

  position_start_state = {
    "PREDATORS": [],
    "PREDATOR_TOP_STRENGTH": 0,
    "PREY": [],
    "FOOD": 0,
    "POSITION_LOCK": Lock(),
  }
  start_end_position = [deepcopy(position_start_state), deepcopy(position_start_state)]
  Organism.grid = []
  for ri in range(Organism.grid_shape[0]):
    Organism.grid.append([])
    for ci in range(Organism.grid_shape[1]):
      Organism.grid[-1].append(start_end_position)

  for _ in range(start_food_source_count):
    p0, p1 = random.randint(0, Organism.grid_shape[0] - 1), random.randint(0, Organism.grid_shape[1] - 1)
    with Organism.grid[p0][p1][0]["POSITION_LOCK"]:
      Organism.grid[p0][p1][0]["FOOD"] += 1

  for _ in range(start_predator_count):
    p0, p1 = random.randint(0, Organism.grid_shape[0] - 1), random.randint(0, Organism.grid_shape[1] - 1)
    with Organism.grid[p0][p1][0]["POSITION_LOCK"]:
      predator = Predator()
      Organism.grid[p0][p1][0]["PREDATORS"].append(predator)
      Organism.grid[p0][p1][0]["PREDATOR_TOP_STRENGTH"] = max(Organism.grid[p0][p1][0]["PREDATOR_TOP_STRENGTH"], predator.strength)
      Organism.grid[p0][p1][0]["PREDATORS"][-1].start()

  for _ in range(start_prey_count):
    p0, p1 = random.randint(0, Organism.grid_shape[0] - 1), random.randint(0, Organism.grid_shape[1] - 1)
    with Organism.grid[p0][p1][0]["POSITION_LOCK"]:
      prey = Prey()
      Organism.grid[p0][p1][0]["PREY"].append(prey)
      Organism.grid[p0][p1][0]["PREY"][-1].start()

  for i in range(day_count):
    with Organism.day_lock:
      print(f"--- Day {Organism.day} ---")
    
    with Organism.processing_count_lock:
      Organism.processing_count_cv.wait_for(Organism.processing_count == 0)

    with Organism.alive_count_lock:
      if Organism.alive_count == 0:
        break
      
    for ri in range(Organism.grid_shape[0]):
      for ci in range(Organism.grid_shape[1]):
        with Organism.grid[p0][p1][0]["POSITION_LOCK"]:
          with Organism.grid[p0][p1][1]["POSITION_LOCK"]:
            Organism.grid[ri][ci][0] = deepcopy(Organism.grid[ri][ci][1])
            Organism.grid[ri][ci][1] = deepcopy(position_start_state)
            Organism.grid[ri][ci][1]["FOOD"] = Organism.grid[ri][ci][0]["FOOD"]
    
    with Organism.day_lock:
      Organism.day = i

if __name__ == "__main__":
  run_simulation()
          

