import json
import os
import subprocess
from typing import Dict, List, AnyStr

VERBOSITY = "0"
MEMORY_LIMIT = "4.0"
VOCAB_MIN_COUNT = "1"
MAX_ITER = "15"
BINARY = "0"
NUM_THREADS = "4"
X_MAX = "10"

PROJECT_ROOT = os.getenv("PYTHONPATH")
TEMP_DIR = f"{PROJECT_ROOT}/nlp/vectorize/lib/build_glove_embeddings/glove/temp"
GLOVE_BUILD_DIR = f"{PROJECT_ROOT}/nlp/vectorize/lib/build_glove_embeddings/glove/build"


class GloVeProcessor:
    def __init__(self, vector_size: int = 10, window_len: int = 3):
        self._vector_size = str(vector_size)
        self._window_len = str(window_len)

    def _write_docs_to_file(self, docs) -> str:
        corpus_path = f"{TEMP_DIR}/corpus.txt"
        with open(corpus_path, "w") as fh:
            for doc in docs:
                doc = doc.replace("\n", "")
                fh.write(f"{doc}\n")
        return corpus_path

    def _write_vocab_counts_to_file(self, corpus_path: str) -> str:
        vocab_count_path = f"{TEMP_DIR}/vocab_count.txt"
        subprocess.run(
            f"{GLOVE_BUILD_DIR}/vocab_count -min-count {VOCAB_MIN_COUNT} -verbose {VERBOSITY} < {corpus_path} > {vocab_count_path}",
            shell=True,
        )
        return vocab_count_path

    def write_coocurrence_to_file(self, corpus_path: str, vocab_count_path: str) -> str:
        coocurrence_path = f"{TEMP_DIR}/coocurrence.bin"
        subprocess.run(
            f"{GLOVE_BUILD_DIR}/cooccur -memory {MEMORY_LIMIT} -vocab-file {vocab_count_path} -verbose {VERBOSITY} -window-size {self._window_len} < {corpus_path} > {coocurrence_path}",
            shell=True,
        )
        return coocurrence_path

    def _write_coocurr_shuffle_to_file(self, coocurrence_path: str):
        coocurr_shuffle_path = f"{TEMP_DIR}/cooccurrence.shuf.bin"
        subprocess.run(
            f"{GLOVE_BUILD_DIR}/shuffle -memory {MEMORY_LIMIT} -verbose {VERBOSITY} < {coocurrence_path} > {coocurr_shuffle_path}",
            shell=True,
        )
        return coocurr_shuffle_path

    def _write_vectors_to_file(self, vocab_count_path: str, coocurr_shuffle_path: str):
        vectors_path = f"{TEMP_DIR}/vectors"
        subprocess.run(
            f"{GLOVE_BUILD_DIR}/glove -save-file {vectors_path} -threads {NUM_THREADS} -input-file {coocurr_shuffle_path} -x-max {X_MAX} -iter {MAX_ITER} -vector-size {self._vector_size} -binary {BINARY} -vocab-file {vocab_count_path} -verbose {VERBOSITY}",
            shell=True,
        )
        return vectors_path + ".txt"

    def read_vectors_from_path(self, vectors_path: str) -> Dict[AnyStr, List]:
        with open(vectors_path, "r") as fh:
            words_to_vectors = fh.readlines()

        word_to_vector_dict = {}
        for idx, word_to_vector_str in enumerate(words_to_vectors):
            word_to_vector_list = word_to_vector_str.split()
            if len(word_to_vector_list) != int(self._vector_size) + 1:
                raise ValueError(
                    f"Row {idx} in vector file had {len(word_to_vector_list)} instead of {int(self._vector_size) + 1} columns"
                )
            word: str = word_to_vector_list[0]
            if word in word_to_vector_dict:
                raise ValueError(f"Row {idx} in vector file had duplicate word {word}")
            vector: List = [
                float(vector_value) for vector_value in word_to_vector_list[1:]
            ]
            word_to_vector_dict[word] = vector
        return word_to_vector_dict

    def train_glove_vectors(self, docs: List[AnyStr]) -> Dict[AnyStr, List]:
        subprocess.run(["make", "clean", "-C", f"{PROJECT_ROOT}/nlp/glove"])
        subprocess.run(["make", "-C", f"{PROJECT_ROOT}/nlp/glove"])
        if not os.path.isdir(TEMP_DIR):
            subprocess.run(["mkdir", TEMP_DIR])
        corpus_path: str = self._write_docs_to_file(docs)
        vocab_count_path: str = self._write_vocab_counts_to_file(corpus_path)
        coocurrence_path: str = self.write_coocurrence_to_file(
            corpus_path, vocab_count_path
        )
        coocurr_shuffle_path: str = self._write_coocurr_shuffle_to_file(
            coocurrence_path
        )
        vectors_path: str = self._write_vectors_to_file(
            vocab_count_path, coocurr_shuffle_path
        )
        return self.read_vectors_from_path(vectors_path)


if __name__ == "__main__":
    # Credit ChatGPT
    corpus_list = [
        {
            "id": 1,
            "name": "John Doe",
            "age": 30,
            "gender": "male",
            "email": "john.doe@example.com",
            "address": {
                "street": "123 Main St",
                "city": "Cityville",
                "state": "CA",
                "zipCode": "12345",
            },
        },
        {
            "id": 2,
            "name": "Jane Smith",
            "age": 25,
            "gender": "female",
            "email": "jane.smith@example.com",
            "address": {
                "street": "456 Oak Ave",
                "city": "Townsville",
                "state": "NY",
                "zipCode": "67890",
            },
        },
        {
            "id": 3,
            "name": "Sam Johnson",
            "age": 35,
            "gender": "non-binary",
            "email": "sam.johnson@example.com",
            "address": {
                "street": "789 Pine Blvd",
                "city": "Villagetown",
                "state": "TX",
                "zipCode": "54321",
            },
        },
        {
            "id": 4,
            "name": "Johnn Doe",
            "age": 30,
            "gender": "male",
            "email": "johnn.doe@example.com",
            "address": {
                "street": "124 Main St",
                "city": "Citysville",
                "state": "CA",
                "zipCode": "12346",
            },
        },
        {
            "id": 5,
            "name": "Jane Smithe",
            "age": 26,
            "gender": "female",
            "email": "jane.smithe@example.com",
            "address": {
                "street": "457 Oak Ave",
                "city": "Townsville",
                "state": "NY",
                "zipCode": "67891",
            },
        },
        {
            "id": 6,
            "name": "Sam Jhonson",
            "age": 35,
            "gender": "non-binary",
            "email": "sam.jhonson@example.com",
            "address": {
                "street": "789 Pine Blvd",
                "city": "Villagetown",
                "state": "TX",
                "zipCode": "54322",
            },
        },
    ]

    def convert_list_elements_to_json_str(json_list: List) -> List[AnyStr]:
        for i in range(len(json_list)):
            json_list[i] = json.dumps(json_list[i], separators=(", ", ": "))
            json_list[i] = (
                json_list[i]
                .replace('"', "")
                .replace("{", "")
                .replace("}", "")
                .replace(",", "")
                .replace(":", "")
            )
        return json_list

    corpus_list_str = convert_list_elements_to_json_str(corpus_list)
    vector_dict = train_glove_vectors(corpus_list_str)
    print(json.dumps(vector_dict, indent=2))
