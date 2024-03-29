# %%
from nlp.vectorize.base_vectorize import BaseVectorize
from nlp.vectorize.lib.build_glove_embeddings.glove.GloVeProcessor import GloVeProcessor
from nlp.vectorize.vectorize_with_glove import VectorizeWithGloVe
from nlp.vector_search.linear_search import LinearVectorSearch
from utils.logger import Logger

import os
import time
import json
import pandas as pd
from typing import Final, Dict, List, Tuple

PYTHON_PATH = os.getenv("PYTHONPATH")

logger = Logger(f"{PYTHON_PATH}/nlp/search_pipelines/logs.txt")


def describe_product(record: dict):
    name: str = record["product_name"]
    manufacturer: str = record["manufacturer"]
    return f"Product {name} built by {manufacturer}"


def process_product(record: dict):
    return describe_product(record)


# %%
raw_data = pd.read_csv(f"{PYTHON_PATH}/nlp/data/amazon_products.csv")
logger.log(f"Product data length: {len(raw_data)}")
start_time = time.time()
raw_data = raw_data[["product_name", "manufacturer"]]
json_dicts = raw_data.to_dict("records")
product_description_words = [process_product(json_dict) for json_dict in json_dicts]
logger.log(f"Preprocessing took {time.time() - start_time} seconds")

# %%
start_time = time.time()
EMBED_LEN = 50
pretrained_vectors_path = f"{PYTHON_PATH}/nlp/vectorize/lib/build_glove_embeddings/glove/embeddings/glove.6B.50d.txt"
pretrained_vectors: dict = GloVeProcessor(vector_size=EMBED_LEN).read_vectors_from_path(
    pretrained_vectors_path
)
vectorizer: BaseVectorize = VectorizeWithGloVe(
    product_description_words, embed_len=EMBED_LEN
)
print(f"Training embeddings took {time.time() - start_time} seconds")

# %%
start_time = time.time()
companies_vectors = vectorizer.vectorize(product_description_words)
logger.log(
    f"Vectorizing {len(companies_vectors)} strings took {time.time() - start_time} seconds"
)


# %%
start_time = time.time()
search = LinearVectorSearch(companies_vectors)
logger.log(f"Storing vectors took {time.time() - start_time} seconds")


# %%
query_dict = {"product_name": "Oldtime Lanterns Working", "manufacturer": "Busch"}
start_time = time.time()
query_str = process_product(query_dict)
query_vector = vectorizer.vectorize([query_str])[0]
result_ids = search.search(query_vector)
logger.log(f"Query took {time.time() - start_time} seconds")

result_jsons = [json_dicts[result_id] for result_id in result_ids]
logger.log(f"Results:\n{result_jsons}")

# %%
