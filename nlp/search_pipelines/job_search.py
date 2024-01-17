# %%
from nlp.glove.read_vectors import get_vector_dict
from nlp.vectorize.vectorize_with_dict import VectorizeWithDict
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
vectorizer = VectorizeWithDict(securities_embeddings_dict, embed_len)
jobs_df[DESCRIPTION_VECTOR] = pd.Series(vectorizer.vectorize(list(jobs_df[DESCRIPTION])))
print(f"Unknown word prop: {vectorizer.last_unknown_prop()}")

# %%
def _normalize_row(row):
    row[DESCRIPTION_VECTOR] = row[DESCRIPTION_VECTOR].flatten()
    return row


jobs_df = jobs_df.apply(_normalize_row, axis=1)

# %%
vector_search = LinearVectorSearch(list(jobs_df[DESCRIPTION_VECTOR]))


# %%
query = "writer"
vector = vectorizer.vectorize([query])[0].flatten()
result = vector_search.search(vector)
print(jobs_df[DESCRIPTION][result])