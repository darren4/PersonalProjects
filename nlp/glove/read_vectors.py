import numpy as np


def get_vector_dict(vector_file: str) -> tuple:
    word_vector_dict = {}
    with open(vector_file) as fh:
        word_vector_str = fh.readline()
        embed_len = len(word_vector_str.split()) - 1
        while word_vector_str:
            word_vector_list = word_vector_str.split()
            word, vector_list_str = word_vector_list[0], word_vector_list[1:]
            vector = np.array([eval(i) for i in vector_list_str])
            word_vector_dict[word] = vector
            word_vector_str = fh.readline()
    return word_vector_dict, embed_len
