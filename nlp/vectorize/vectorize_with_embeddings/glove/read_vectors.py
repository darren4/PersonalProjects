import numpy as np


def get_vector_dict(vector_file: str) -> tuple:
    word_vector_dict = {}
    failure_count = 0
    row_count = 0
    with open(vector_file) as fh:
        word_vector_str = fh.readline()
        embed_len = len(word_vector_str.split()) - 1
        while word_vector_str:
            row_count += 1
            word_vector_list = word_vector_str.split()
            word, vector_list_str = word_vector_list[0], word_vector_list[1:]
            try:
                vector = np.array([eval(i) for i in vector_list_str])
            except:
                failure_count += 1
                continue
            word_vector_dict[word] = vector
            word_vector_str = fh.readline()
    print(f"get_vector_dict failure proportion: {failure_count / row_count}")
    return word_vector_dict, embed_len
