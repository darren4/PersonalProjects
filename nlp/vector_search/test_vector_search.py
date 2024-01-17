from nlp.vector_search.perpendicular_search import PerpendicularSearch

import numpy as np


def test_perpendicular_search():
    embeddings = [np.array([-0.18, 0.249]), np.array([0.9999, 1.0])]
    search = PerpendicularSearch(embeddings)

    result = search.search(np.array([-0.18, 0.249]))
    assert len(result) == 1
    assert result[0] == 0
    result = search.search(np.array([-0.10, 0.30]))
    assert len(result) == 1
    assert result[0] == 0
    result = search.search(np.array([-0.10, 0.2]))
    assert (len(result)) == 1
    assert result[0] == 0

    result = search.search(np.array([0.9999, 1.0]))
    assert len(result) == 1
    assert result[0] == 1
    result = search.search(np.array([0.95, 0.92]))
    assert len(result) == 1
    assert result[0] == 1


if __name__ == "__main__":
    test_perpendicular_search()
