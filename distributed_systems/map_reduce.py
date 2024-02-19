from distributed_systems.base_process import Process, Msg
from distributed_systems.framework import DistributedSystem, ProcessFramework

import random
from typing import List
import json


class Initializer(Process):
    BITE_SIZE = 20

    def get_next_process_id(self):
        output_process_id = self.next_process_id
        self.next_process_id += 1
        return output_process_id

    def start(self, msg: str=None):
        self.start_background_processing()
        self.next_process_id = 1

        input_len: int = len(ProcessFramework.input)
        bites = []
        for next_idx in range(0, input_len, Initializer.BITE_SIZE):
            bites.append((next_idx, next_idx + Initializer.BITE_SIZE))

        reducer_id: int = len(bites) + 1
        for bite in bites:
            self.new_process(self.get_next_process_id(), Mapper, f"{bite[0]},{bite[1]},{reducer_id}")
        self.new_process(reducer_id, Reducer, f"{len(bites)}")
        self.complete()


class Mapper(Process):
    def start(self, msg: str=None):
        self.start_background_processing()
        msg_list = msg.split(",")
        process_range_start: int = int(msg_list[0])
        process_range_end: int = int(msg_list[1])
        reducer_id: int = int(msg_list[2])

        word_counts = {}
        for word_idx in range(process_range_start, process_range_end):
            word = ProcessFramework.input[word_idx]
            if word in word_counts:
                word_counts[word] += 1
            else:
                word_counts[word] = 1

        word_counts_json = json.dumps(word_counts)
        self.send_msg(reducer_id, Msg.build_msg(word_counts_json))
        self.complete()

class Reducer(Process):
    def start(self, msg: str=None):
        self.start_background_processing()
        mapper_count = int(msg)

        mapper_results: List[dict] = []
        for _ in range(mapper_count):
            mapper_msg = self.get_one_msg()
            mapper_result_dict = json.loads(mapper_msg.content)
            mapper_results.append(mapper_result_dict)

        word_counts = {}
        for mapper_result in mapper_results:
            for word, count in mapper_result.items():
                if word in word_counts:
                    word_counts[word] += count
                else:
                    word_counts[word] = count

        ProcessFramework.output = word_counts
        self.complete()

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
        word_list.append(word)
    
    DistributedSystem.define_faults()
    DistributedSystem.process_input(word_list, [Initializer])
    attempted_word_counts = DistributedSystem.wait_for_completion()

    if attempted_word_counts == word_counts:
        print("SUCCESS")
    else:
        print("FAILURE")
        print(f"Correct: {word_counts}")
        print(f"Got: {attempted_word_counts}")
