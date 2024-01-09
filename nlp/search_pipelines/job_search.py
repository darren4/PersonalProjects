# %%
from nlp.glove.read_vectors import get_vector_dict
from nlp.utils.process_corpus import StringsToVectors, NormalizeVectorLens
from nlp.vector_search.linear_search import LinearVectorSearch

import pandas as pd
import numpy as np
import os

# %%
DESCRIPTION, DESCRIPTION_VECTOR = "description", "vector"
jobs_df = pd.read_csv(f"{os.environ.get('PYTHONPATH')}/nlp/data/jobs.csv")

# %%
securities_embeddings_dict, embed_len = get_vector_dict(
    f"{os.environ.get('PYTHONPATH')}/nlp/glove/embeddings/jobs_vectors.txt"
)

# %%
strings_to_vectors = StringsToVectors(securities_embeddings_dict, embed_len)
process_columns = {DESCRIPTION: DESCRIPTION_VECTOR}
jobs_df, max_len = strings_to_vectors.to_vectors(jobs_df, process_columns)
print(f"max_len: {max_len}")
print(f"Unknown word len: {strings_to_vectors.unknown_token_count}")

# %%
vector_normalizer = NormalizeVectorLens(max_len, embed_len, "ADJUST_LEN")


def normalize(matrix):
    return vector_normalizer.noramlize(matrix).flatten()


def _normalize_row(row):
    row[DESCRIPTION_VECTOR] = normalize(row[DESCRIPTION_VECTOR])
    return row


jobs_df = jobs_df.apply(_normalize_row, axis=1)

# %%
vector_search = LinearVectorSearch(list(jobs_df[DESCRIPTION]), jobs_df[DESCRIPTION_VECTOR])


# %%
query = "writer"
vector = strings_to_vectors.to_vector(query)
vector = normalize(vector)
result = vector_search.search(vector)
print(result[0][0])

# %%
query = "tesla motors inc"
vector = strings_to_vectors.to_vector(query)
vector1 = normalize(vector)

query = "tesla inc"
vector = strings_to_vectors.to_vector(query)
vector2 = normalize(vector)

print(np.linalg.norm(abs(vector1 - vector2)))
