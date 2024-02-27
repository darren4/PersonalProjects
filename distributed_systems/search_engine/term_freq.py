from distributed_systems.base_process import Process, Msg
from distributed_systems.framework import DistributedSystem, ProcessFramework
from utils.cleaning import sentence_to_list

from typing import List
import json
import os
from functools import reduce


class Initializer(Process):
    def get_next_process_id(self):
        output_process_id = self.next_process_id
        self.next_process_id += 1
        return output_process_id

    def start(self, msg: str = None):
        self.next_process_id = 1

        file_count: int = len(ProcessFramework.input)
        reducer_id: int = file_count + 1

        next_doc_id = 0
        for file_path in ProcessFramework.input:
            with open(file_path, "r") as fh:
                docs_list = fh.readlines()
            docs_list_json = json.dumps(docs_list)
            self.new_process(
                self.get_next_process_id(), TFMapper, f"{next_doc_id},{docs_list_json},{reducer_id}"
            )
            next_doc_id += len(docs_list)
        self.new_process(reducer_id, TFReducer, f"{file_count}")
        self.complete()


class TFMapper(Process):
    def start(self, msg: str = None):
        msg_list = msg.split(",")
        doc_id: int = int(msg_list[0])
        docs_list_json: str = str(msg_list[1])
        reducer_id: int = int(msg_list[2])

        docs_list = json.loads(docs_list_json)
        term_doc_freq = {}

        for doc in docs_list:
            doc_words_list = sentence_to_list(doc)
            for word in doc_words_list:
                if word in term_doc_freq:
                    if doc_id in term_doc_freq[doc_id]:
                        term_doc_freq[word][doc_id] += 1
                    else:
                        term_doc_freq[word][doc_id] = 1
                else:
                    term_doc_freq[word] = {
                        doc_id: 1
                    }
            doc_id += 1

        word_counts_json = json.dumps(term_doc_freq)
        self.send_msg(reducer_id, Msg.build_msg(word_counts_json))
        self.complete()


class TFReducer(Process):
    def start(self, msg: str = None):
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
    term_freq = {}

    word_file_paths = [f"{os.getenv('PYTHONPATH')}/distributed_systems/search_engine/raw_data/sentences0.txt",
                       f"{os.getenv('PYTHONPATH')}/distributed_systems/search_engine/raw_data/sentences1.txt",
                       f"{os.getenv('PYTHONPATH')}/distributed_systems/search_engine/raw_data/sentences2.txt"]

    sentence_idx = 0
    for word_file_path in word_file_paths:
        with open(word_file_path, "r") as fh:
            for raw_sentence in fh.readlines():
                word_list = sentence_to_list(raw_sentence)
                for word in word_list:
                    if word in term_freq:
                        if sentence_idx in term_freq[word]:
                            term_freq[word][sentence_idx] += 1
                        else:
                            term_freq[word][sentence_idx] = 1
                    else:
                        term_freq[word] = {
                            sentence_idx: 1
                        }
                sentence_idx += 1

    DistributedSystem.define_faults(msg_drop_prop=0.1)
    DistributedSystem.process_input(word_file_paths, [Initializer])
    attempted_term_freq = DistributedSystem.wait_for_completion()

    if attempted_term_freq == term_freq:
        print("SUCCESS")
    else:
        print("FAILURE")
        print(f"Correct: {term_freq}")
        print(f"Got: {attempted_term_freq}")
