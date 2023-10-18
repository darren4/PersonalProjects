#include "organisms.h"

#include <vector>
#include <iostream>
#include <cstdlib>

using std::cout;


void run_simulation(){
    cout << "Starting simulation\n";
    srand(0);

    Planet.grid_height = 15;
    Planet.grid_width = 15;
    start_predator_count = 45;
    start_prey_count = 45;
    start_food_source_count = 225;
    day_count = 150;

    prey_starting_calories = 5;
    predator_starting_calories = 1;


}

int main(){
    run_simulation();
    return 0;
}
