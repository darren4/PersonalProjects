from nlp.vector_search.coverage_search import CoverageSearch

import numpy as np


def test_multi_dim_search():
    embeddings = [np.array([0.18, 0.249]), np.array([0.9999, 1.0])]
    corpus = [
        "cat",
        "dog",
    ]
    search = CoverageSearch(corpus, embeddings)
    assert search._index[0, 118][0] == 0
    assert search._index[1, 124][0] == 0
    assert search._index[0, 199][0] == 1
    assert search._index[1, 200][0] == 1

    assert search.search(np.array([0.18, 0.249]))[0] == "cat"
    assert search.search(np.array([0.10, 0.30]))[0] == "cat"

    assert search.search(np.array([0.9999, 1.0]))[0] == "dog"
    assert search.search(np.array([0.95, 0.92]))[0] == "dog"


if __name__ == "__main__":
    test_multi_dim_search()
