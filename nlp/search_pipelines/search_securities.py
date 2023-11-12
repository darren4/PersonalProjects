# %%
from glove.read_vectors import get_vector_dict
from utils.process_corpus import StringsToVectors, NormalizeVectorLens
import pandas as pd
from utils.vector_search import SimpleVectorSearch
import numpy as np

# %%
X_WORDS, Y_WORDS, SAME = "description_x", "description_y", "same_security"
X_MAT, Y_MAT = "matrix_x", "matrix_y"
securities_df = pd.read_csv(f"data/security_descriptions.csv")

# %%
securities_embeddings_dict, embed_len = get_vector_dict(
    f"glove/data/securities_vectors.txt"
)

# %%
strings_to_vectors = StringsToVectors(securities_embeddings_dict, embed_len)
process_columns = {X_WORDS: X_MAT, Y_WORDS: Y_MAT}
securities_df, max_len = strings_to_vectors.to_vectors(securities_df, process_columns)
print(max_len)

# %%
vector_normalizer = NormalizeVectorLens(10, embed_len, "ADJUST_LEN")


def normalize(matrix):
    return vector_normalizer.noramlize(matrix).flatten()


def _normalize_row(row):
    row[X_MAT] = normalize(row[X_MAT])
    row[Y_MAT] = normalize(row[Y_MAT])
    return row


securities_df = securities_df.apply(_normalize_row, axis=1)

# %%
vector_search = SimpleVectorSearch()
duplicate_search = set()


def _add_row(row):
    if row[X_WORDS] not in duplicate_search:
        vector_search.add(row[X_MAT], row[X_WORDS])
        duplicate_search.add(row[X_WORDS])
    if row[Y_WORDS] not in duplicate_search:
        vector_search.add(row[Y_MAT], row[Y_WORDS])
        duplicate_search.add(row[Y_WORDS])


securities_df.apply(_add_row, axis=1)

# %%
query = "tesla motors inc"
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
