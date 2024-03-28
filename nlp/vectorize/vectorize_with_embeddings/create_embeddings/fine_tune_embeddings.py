from typing import List, Dict, Tuple, Iterable
import numpy as np
from mittens import Mittens


def get_word_list_and_cooccurrences(corpus: List[List]) -> Tuple[List[str], np.array]:
    word_ids = {}
    word_list = []
    for doc in corpus:
        for word in set(doc):
            if word not in word_ids:
                word_ids[word] = len(word_list)
                word_list.append(word)

    cooccurrences = np.zeros((len(word_list), len(word_list)))
    for doc in corpus:
        word_set = list(set(doc))
        for i in range(len(word_set)):
            for k in range(len(word_set)):
                if i != k:
                    cooccurrences[word_ids[i]][word_ids[k]] += 1
    return word_list, cooccurrences


def fine_tune_embeddings(
    orig_embeddings: Dict[str, Iterable], corpus: List[List], embedding_len=None
) -> Dict[str, np.array]:
    if not embedding_len:
        embedding_len = len(list(orig_embeddings.values())[0])
    mittens_model = Mittens(n=embedding_len, max_iter=1000)

    word_list, cooccurrences = get_word_list_and_cooccurrences(corpus)

    new_embeddings: np.array = mittens_model.fit(
        cooccurrences, vocab=word_list, initial_embedding_dict=orig_embeddings
    )
    new_embedding_dict = {}
    for i in range(len(word_list)):
        new_embedding_dict[word_list[i]] = new_embeddings[i]
    return new_embedding_dict
