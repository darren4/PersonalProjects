from .create_nn_embedding import get_neighbor_pairs_list


def test_get_neighbor_pairs_list():
    corpus_list = ["cat", "dog", "mouse"]
    pairs = get_neighbor_pairs_list(corpus_list, 1, 1)
    assert len(pairs) == 2
    first_found, second_found = False, False
    for pair in pairs:
        if pair[0] == "cat" and pair[1] == "dog":
            first_found = True
        elif pair[0] == "dog" and pair[1] == "mouse":
            second_found = True
        else:
            assert False
    assert first_found and second_found
