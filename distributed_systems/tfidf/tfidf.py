from distributed_systems.base_process import Process, Msg
from distributed_systems.framework import DistributedSystem, ProcessFramework
from utils.string_cleaning import sentence_to_list

from typing import List
import json
import os


class Initializer(Process):
    def get_next_process_id(self):
        output_process_id = self.next_process_id
        self.next_process_id += 1
        return output_process_id

    def start(self, msg: str = None):
        self.next_process_id = 1

        file_count: int = len(ProcessFramework.input)
        reducer_id: int = file_count + 1

        next_doc_id: int = 0
        for file_path in ProcessFramework.input:
            with open(file_path, "r") as fh:
                docs_list = fh.readlines()
            docs_list_json = json.dumps(docs_list)
            mapper_msg = {
                "NEXT_DOC_ID": next_doc_id,
                "DOCS_LIST": docs_list_json,
                "REDUCER_ID": reducer_id,
            }
            self.new_process(
                self.get_next_process_id(),
                Mapper,
                json.dumps(mapper_msg),
            )
            next_doc_id += len(docs_list)
        self.new_process(reducer_id, Reducer, f"{file_count}")
        self.complete()


class Mapper(Process):
    def start(self, msg: str = None):
        msg_dict = json.loads(msg)
        doc_id = msg_dict["NEXT_DOC_ID"]
        docs_list_json = msg_dict["DOCS_LIST"]
        reducer_id = msg_dict["REDUCER_ID"]

        docs_list = json.loads(docs_list_json)
        term_doc_freq = {}

        for doc in docs_list:
            doc_words_list = sentence_to_list(doc)
            for word in doc_words_list:
                if word in term_doc_freq:
                    if doc_id in term_doc_freq[word]:
                        term_doc_freq[word][doc_id] += 1
                    else:
                        term_doc_freq[word][doc_id] = 1
                else:
                    term_doc_freq[word] = {doc_id: 1}
            doc_id += 1

        word_counts_json = json.dumps(term_doc_freq)
        self.send_msg(reducer_id, Msg.build_msg(word_counts_json))
        self.complete()


class Reducer(Process):
    @staticmethod
    def convert_keys_to_int(d: dict):
        int_keys_d = {}
        for key in d:
            int_keys_d[int(key)] = d[key]
        return int_keys_d

    def start(self, msg: str = None):
        mapper_count = int(msg)

        term_doc_freqs: List[dict] = []
        for _ in range(mapper_count):
            mapper_msg = self.get_one_msg()
            mapper_result_dict = json.loads(mapper_msg.content)
            term_doc_freqs.append(mapper_result_dict)

        combined_term_doc_freq = {}
        for term_doc_freq in term_doc_freqs:
            for word, freq_in_docs in term_doc_freq.items():
                freq_in_docs: dict = self.convert_keys_to_int(freq_in_docs)
                if word in combined_term_doc_freq:
                    for doc, freq in freq_in_docs.items():
                        if doc in combined_term_doc_freq[word]:
                            combined_term_doc_freq[word][doc] += freq
                        else:
                            combined_term_doc_freq[word][doc] = freq
                else:
                    combined_term_doc_freq[word] = freq_in_docs

        ProcessFramework.output = combined_term_doc_freq
        self.complete()


if __name__ == "__main__":
    term_freq = {}

    word_file_paths = [
        f"{os.getenv('PYTHONPATH')}/distributed_systems/search_engine/raw_data/sentences0.txt",
        f"{os.getenv('PYTHONPATH')}/distributed_systems/search_engine/raw_data/sentences1.txt",
        f"{os.getenv('PYTHONPATH')}/distributed_systems/search_engine/raw_data/sentences2.txt",
    ]

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
                        term_freq[word] = {sentence_idx: 1}
                sentence_idx += 1

    DistributedSystem.define_faults(msg_drop_prop=0.1)
    DistributedSystem.process_input(word_file_paths, [Initializer])
    attempted_term_freq = DistributedSystem.wait_for_completion()

    if attempted_term_freq == term_freq:
        print("SUCCESS")
    else:
        print("FAILURE")
        for word in attempted_term_freq.keys():
            if term_freq[word] != attempted_term_freq[word]:
                print(f"Expected:\n{term_freq[word]}")
                print(f"Got:\n{attempted_term_freq[word]}")
                break
