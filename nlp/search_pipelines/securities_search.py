# %%
from nlp.glove.read_vectors import get_vector_dict
from nlp.vectorize.vectorize_with_dict import VectorizeWithDict
from nlp.vectorize.vectorize_with_hg import VectorizeWithHG
from nlp.vector_search.linear_search import LinearVectorSearch
from nlp.vector_search.perpendicular_search import PerpendicularVectorSearch
from utils.logger import Logger

import pandas as pd
import os
import time


logger = Logger("nlp/search_pipelines/securities_search_logs.txt")

X_WORDS, Y_WORDS, SAME = "description_x", "description_y", "same_security"
X_MAT, Y_MAT = "matrix_x", "matrix_y"
securities_df = pd.read_csv(
    f"{os.environ.get('PYTHONPATH')}/nlp/data/security_descriptions.csv"
)


# start_time = time.time()
# securities_embeddings_dict, embed_len = get_vector_dict(
#     f"{os.environ.get('PYTHONPATH')}/nlp/glove/embeddings/securities_vectors.txt"
# )
# logger.log(f"Embeddings load time: {time.time() - start_time}")
# vectorizer = VectorizeWithDict(securities_embeddings_dict, embed_len)

vectorizer = VectorizeWithHG("sentence-t5-base")

start_time = time.time()
securities_df[X_MAT] = pd.Series(list(vectorizer.vectorize(securities_df[X_WORDS])))
securities_df[Y_MAT] = pd.Series(list(vectorizer.vectorize(securities_df[Y_WORDS])))
logger.log(f"Vector conversion time: {time.time() - start_time}")
logger.log(f"Proportion of unknown tokens: {vectorizer.last_unknown_prop()}")


def _normalize_row(row):
    row[X_MAT] = row[X_MAT].flatten()
    row[Y_MAT] = row[Y_MAT].flatten()
    return row


start_time = time.time()
securities_df = securities_df.apply(_normalize_row, axis=1)
logger.log(f"Vector normalization time: {time.time() - start_time}")

# %%
start_time = time.time()
vector_search = LinearVectorSearch(list(securities_df[X_MAT]))
# vector_search = PerpendicularSearch(list(securities_df[X_MAT]), coverage_cutoff=0.5)
logger.log(f"Loaded vectors into search in {time.time() - start_time} seconds")

start_time = time.time()
correct = 0
for i in range(len(securities_df)):
    query = securities_df[Y_MAT][i]
    result = vector_search.search(query, approx_max_result_count=1)[0]
    if securities_df["ticker_x"][result] == securities_df["ticker_y"][i]:
        correct += 1
logger.log(f"Accuracy: {correct / len((securities_df))}")
logger.log(f"Search completed in {time.time() - start_time} seconds")
# %%
