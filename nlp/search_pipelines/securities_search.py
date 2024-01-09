from nlp.glove.read_vectors import get_vector_dict
from nlp.utils.process_corpus import StringsToVectors, NormalizeVectorLens
from nlp.vector_search.linear_search import LinearVectorSearch
from utils.logger import Logger

import pandas as pd
import numpy as np
import os
import time


logger = Logger("nlp/search_pipelines/securities_search_logs.txt")

X_WORDS, Y_WORDS, SAME = "description_x", "description_y", "same_security"
X_MAT, Y_MAT = "matrix_x", "matrix_y"
securities_df = pd.read_csv(
    f"{os.environ.get('PYTHONPATH')}/nlp/data/security_descriptions.csv"
)


start_time = time.time()
securities_embeddings_dict, embed_len = get_vector_dict(
    f"{os.environ.get('PYTHONPATH')}/nlp/glove/embeddings/securities_vectors.txt"
)
logger.log(f"Embeddings load time: {time.time() - start_time}")


strings_to_vectors = StringsToVectors(securities_embeddings_dict, embed_len)
process_columns = {X_WORDS: X_MAT, Y_WORDS: Y_MAT}
start_time = time.time()
securities_df, max_len = strings_to_vectors.to_vectors(securities_df, process_columns)
logger.log(f"Vector conversion time: {time.time() - start_time}")
logger.log(f"Max sentence len: {max_len}")
logger.log(f"Proportion of unknown tokens: {strings_to_vectors.last_unknown_prop()}")


vector_normalizer = NormalizeVectorLens(10, embed_len, "AVG_SEMANTICS")


def normalize(matrix):
    return vector_normalizer.noramlize(matrix).flatten()


def _normalize_row(row):
    row[X_MAT] = normalize(row[X_MAT])
    row[Y_MAT] = normalize(row[Y_MAT])
    return row


start_time = time.time()
securities_df = securities_df.apply(_normalize_row, axis=1)
logger.log(f"Vector normalization time: {time.time() - start_time}")

vector_list = []
sentence_list = []
duplicate_search = set()


def _add_row(row):
    if row[X_WORDS] not in duplicate_search:
        sentence_list.append(row[X_WORDS])
        vector_list.append(row[X_MAT])
        duplicate_search.add(row[X_WORDS])
    if row[Y_WORDS] not in duplicate_search:
        sentence_list.append(row[Y_WORDS])
        vector_list.append(row[Y_MAT])
        duplicate_search.add(row[Y_WORDS])


securities_df.apply(_add_row, axis=1)
vector_search = LinearVectorSearch(sentence_list, vector_list)


query = "tesla mtrs inc com"
vector = strings_to_vectors.to_vector(query)
vector = normalize(vector)
result = vector_search.search(vector)
logger.log(result)

logger.log("---")

query = "tesla motors inc com"
vector = strings_to_vectors.to_vector(query)
vector1 = normalize(vector)
logger.log(query)

query = "tesla mtrs inc com"
vector = strings_to_vectors.to_vector(query)
vector2 = normalize(vector)
logger.log(query)

logger.log(np.linalg.norm(abs(vector1 - vector2)))
