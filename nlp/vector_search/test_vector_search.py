from nlp.vector_search.vector_space_search import MultiDimSearch

import numpy as np


def test_create_small():
    embedding_len = 2
    corpus_embeddings = [
        (np.array([0.18, 0.249]), "cat"),
        (np.array([0.9999, 1.0]), "dog"),
    ]
    search = MultiDimSearch(embedding_len, corpus_embeddings)
    assert search._index[0, 118][0] == 0
    assert search._index[1, 124][0] == 0
    assert search._index[0, 199][0] == 1
    assert search._index[1, 200][0] == 1

    assert search.search(np.array([0.18, 0.249]))[0] == "cat"
    assert search.search(np.array([0.10, 0.30]))[0] == "cat"

    assert search.search(np.array([0.9999, 1.0]))[0] == "dog"
    assert search.search(np.array([0.95, 0.92]))[0] == "dog"


if __name__ == "__main__":
    test_create_small()
