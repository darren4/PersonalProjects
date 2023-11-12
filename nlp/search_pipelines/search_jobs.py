# %%
from glove.read_vectors import get_vector_dict
from utils.process_corpus import StringsToVectors, NormalizeVectorLens
import pandas as pd
from utils.vector_search import SimpleVectorSearch
import numpy as np

# %%
DESCRIPTION, DESCRIPTION_VECTOR = "description", "vector"
securities_df = pd.read_csv(f"data/jobs.csv")

# %%
securities_embeddings_dict, embed_len = get_vector_dict(f"glove/data/jobs_vectors.txt")

# %%
strings_to_vectors = StringsToVectors(securities_embeddings_dict, embed_len)
process_columns = {DESCRIPTION: DESCRIPTION_VECTOR}
securities_df, max_len = strings_to_vectors.to_vectors(securities_df, process_columns)
print(max_len)

# %%
vector_normalizer = NormalizeVectorLens(max_len, embed_len, "ADJUST_LEN")


def normalize(matrix):
    return vector_normalizer.noramlize(matrix).flatten()


def _normalize_row(row):
    row[DESCRIPTION_VECTOR] = normalize(row[DESCRIPTION_VECTOR])
    return row


securities_df = securities_df.apply(_normalize_row, axis=1)

# %%
vector_search = SimpleVectorSearch()


def _add_row(row):
    vector_search.add(row[DESCRIPTION_VECTOR], row[DESCRIPTION])


securities_df.apply(_add_row, axis=1)

# %%
query = "tax evasion"
vector = strings_to_vectors.to_vector(query)
vector = normalize(vector)
result = vector_search.search(vector)
print(result)

# %%
query = "tesla motors inc"
vector = strings_to_vectors.to_vector(query)
vector1 = normalize(vector)

query = "tesla inc"
vector = strings_to_vectors.to_vector(query)
vector2 = normalize(vector)

print(np.linalg.norm(abs(vector1 - vector2)))
