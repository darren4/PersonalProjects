import re


def clean_str(string: str):
    if type(string) != str:
        return ""
    return re.sub(r"\W+", " ", string.encode("ascii", "ignore").decode())


def sentence_to_list(sentence: str):
    return clean_str(sentence).upper().split()


def get_clean_corpus(corpus):
    corpus_list = []
    for sentence in corpus:
        corpus_list.append(sentence_to_list(sentence))
    return corpus_list


if __name__ == "__main__":
    print(sentence_to_list("cat and dogẀ"))
