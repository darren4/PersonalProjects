from nlp.vector_search.perpendicular_search import PerpendicularSearch

import numpy as np


def test_perpendicular_search():
    embeddings = [np.array([-0.18, 0.249]), np.array([0.9999, 1.0])]
    corpus = [
        "cat",
        "dog",
    ]
    search = PerpendicularSearch(corpus, embeddings)

    result = search.search(np.array([-0.18, 0.249]))
    assert len(result) == 1
    assert result[0][0] == "cat"
    result = search.search(np.array([-0.10, 0.30]))
    assert len(result) == 1
    assert result[0][0] == "cat"
    result = search.search(np.array([-0.10, 0.2]))
    assert (len(result)) == 1
    assert result[0][0] == "cat"

    result = search.search(np.array([0.9999, 1.0]))
    assert len(result) == 1
    assert result[0][0] == "dog"
    result = search.search(np.array([0.95, 0.92]))
    assert len(result) == 1
    assert result[0][0] == "dog"


if __name__ == "__main__":
    test_perpendicular_search()
