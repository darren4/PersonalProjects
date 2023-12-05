from nlp.vector_search.coverage_search import CoverageSearch

import numpy as np


def test_coverage_search():
    embeddings = [np.array([-0.18, 0.249]), np.array([0.9999, 1.0])]
    corpus = [
        "cat",
        "dog",
    ]
    search = CoverageSearch(corpus, embeddings)

    assert search.search(np.array([-0.18, 0.249])) == ["cat"]
    assert search.search(np.array([-0.10, 0.30])) == ["cat"]
    assert search.search(np.array([-0.10, 0.2])) == ["cat"]

    assert search.search(np.array([0.9999, 1.0])) == ["dog"]
    assert search.search(np.array([0.95, 0.92])) == ["dog"]


if __name__ == "__main__":
    test_coverage_search()
