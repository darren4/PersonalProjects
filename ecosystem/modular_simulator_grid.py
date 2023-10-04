import random
from copy import deepcopy
from threading import Lock, Thread, Condition

random.seed(728)


grid = None
grid_shape = None

day = -1
day_lock = Lock()

def new_position(ri, ci, grid_shape):
  valid_positions = []
  if ri + 1 <  grid_shape[0] and ci + 1 <  grid_shape[1]:
    # Bottom right
    valid_positions.append((ri + 1, ci + 1))
  if ri + 1 <  grid_shape[0]:
    # Bottom
    valid_positions.append((ri + 1, ci))
  if ri + 1 <  grid_shape[0] and ci - 1 >= 0:
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
  if ri - 1 >= 0 and ci + 1 <  grid_shape[1]:
    # Top right
    valid_positions.append((ri - 1, ci + 1))
  if ci + 1 <  grid_shape[1]:
    # Right
    valid_positions.append((ri, ci + 1))

  random_position = random.randint(0, len(valid_positions) - 1)
  return valid_positions[random_position]

def process_position(ri, ci):
  current_day = 0
  

class Organism:
  alive_count = 0
  alive_count_lock = Lock()

class Predator(Organism):
  def __init__(self, _strength=5):
    self.strength = _strength

class Prey(Organism):
  alive_count = 0
  alive_count_lock = Lock()
  def __init__(self, _strength: int=random.randint(5, 10), _calorie_usage: int=random.randint(0, 0), _offspring_capacity: int=random.randint(1, 5)):
    self.inherited = {
      "STRENGTH": _strength,
      "CALORIE_USAGE": _calorie_usage,
      "OFFSPRING_CAPACITY": _offspring_capacity
    }
    self.stored_calories = 10
    with Organism.alive_count_lock:
      Organism.alive_count += 1
    with Prey.alive_count_lock:
      Prey.alive_count += 1

  def _starved(self, eat=0) -> bool:
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
  grid_shape = (10, 10)
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
  grid = []
  for ri in range(grid_shape[0]):
    grid.append([])
    for ci in range(grid_shape[1]):
      grid[-1].append(start_end_position)

  for _ in range(start_food_source_count):
    ri, ci = random.randint(0, grid_shape[0] - 1), random.randint(0, grid_shape[1] - 1)
    with grid[ri][ci][0]["POSITION_LOCK"]:
      grid[ri][ci][0]["FOOD"] += 1

  for _ in range(start_predator_count):
    ri, ci = random.randint(0, grid_shape[0] - 1), random.randint(0, grid_shape[1] - 1)
    with grid[ri][ci][0]["POSITION_LOCK"]:
      predator = Predator()
      grid[ri][ci][0]["PREDATORS"].append(predator)
      grid[ri][ci][0]["PREDATOR_TOP_STRENGTH"] = max(grid[ri][ci][0]["PREDATOR_TOP_STRENGTH"], predator.strength)

  for _ in range(start_prey_count):
    ri, ci = random.randint(0, grid_shape[0] - 1), random.randint(0, grid_shape[1] - 1)
    with grid[ri][ci][0]["POSITION_LOCK"]:
      prey = Prey()
      grid[ri][ci][0]["PREY"].append(prey)

  for ri in range(grid_shape[0]):
    for ci in range(grid_shape[1]):
      Thread(target=process_position, args=[ri, ci]).start()

  for i in range(day_count):
    with day_lock:
      print(f"--- Day {day} ---")
      day = i

    with Organism.alive_count_lock:
      if Organism.alive_count == 0:
        break
      
    for ri in range(grid_shape[0]):
      for ci in range(grid_shape[1]):
        with grid[ri][ci][0]["POSITION_LOCK"]:
          with grid[ri][ci][1]["POSITION_LOCK"]:
            grid[ri][ci][0] = deepcopy(grid[ri][ci][1])
            grid[ri][ci][1] = deepcopy(position_start_state)
            grid[ri][ci][1]["FOOD"] = grid[ri][ci][0]["FOOD"]
      

if __name__ == "__main__":
  run_simulation()
          

