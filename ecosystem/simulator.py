"""
General traits
- randomly move in 8 directions (unless in edge or corner)

Prey traits
- general
  - eat when on top of food source
  - reproduce when on same square as other prey
  - die when on same square as stronger predator
- optimize
  - eating speed
  - strength (compared to prey)
  - offspring capacity

Predatory traits
- strength (compared to prey)
- never reproduce or die
"""


class Organism:
    def next_square()
