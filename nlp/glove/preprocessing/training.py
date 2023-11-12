import pandas as pd
from utils.cleaning import sentence_to_list


ig_raw = pd.read_csv("data/instagram.csv")["review_description"]
fh = open("glove/data/instagram_corpus.txt", "w")


def process_row(doc):
    words = sentence_to_list(doc)
    for word in words:
        fh.write(f"{word} ")
    fh.write("\n")


ig_raw.apply(process_row)

fh.close()
