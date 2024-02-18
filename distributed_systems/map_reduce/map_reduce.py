from distributed_systems.map_reduce import generate_test_data
from distributed_systems.base_process import Process
from distributed_systems.framework import DistributedSystem

import random
from typing import List


class WordCounter(Process):
    

if __name__ == "__main__":
    vocab = {
        0: "cat", 
        1: "dog", 
        2: "bird", 
        3: "mouse",
        4: "horse" 
    }

    word_counts = {
        "cat": 0,
        "dog": 0,
        "bird": 0,
        "mouse": 0,
        "horse": 0
    }

    word_list = []

    for _ in range(100):
        word = vocab[random.randint(0, 4)]
        word_counts[word] += 1
        word_list.append(word_list)
    
    DistributedSystem.define_faults()
    DistributedSystem.process_input(word_list, [])
    attempted_word_counts = DistributedSystem.wait_for_completion()

    if attempted_word_counts == word_counts:
        print("SUCCESS")
    else:
        print("FAILURE")
        print(f"Correct: {word_counts}")
        print(f"Got: {attempted_word_counts}")
