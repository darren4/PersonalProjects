# %%
from nlp.glove.train import train_glove_vectors
from nlp.vectorize.base_vectorize import BaseVectorize
from nlp.vectorize.vectorize_with_hg import VectorizeWithHG
from nlp.vectorize.vectorize_with_dict import VectorizeWithDict
from nlp.vector_search.linear_search import LinearVectorSearch
from nlp.vector_search.perpendicular_search import PerpendicularVectorSearch
from nlp.glove.train import read_vectors_from_path
from utils.logger import Logger
from utils.string_cleaning import clean_str

import os
import time
import json
import pandas as pd
from typing import Final, Dict, List, Tuple

BASE_PATH: Final[str] = f"{os.getenv('PYTHONPATH')}/nlp/search_pipelines/product_search"


logger = Logger(f"{BASE_PATH}/logs.txt")


def describe_product(record: dict):
    name: str = record["product_name"]
    manufacturer: str = record["manufacturer"]
    return f"Product {name} built by {manufacturer}"


def process_product(record: dict):
    return clean_str(describe_product(record))


# %%
raw_data = pd.read_csv(f"{BASE_PATH}/amazon_products.csv")
logger.log(f"Product data length: {len(raw_data)}")
start_time = time.time()
raw_data = raw_data[["product_name", "manufacturer"]]
json_dicts = raw_data.to_dict("records")
json_strs = [process_product(json_dict) for json_dict in json_dicts]
logger.log(f"Preprocessing took {time.time() - start_time} seconds")

# %%
start_time = time.time()
vector_dict = train_glove_vectors(json_strs)
print(f"Training embeddings took {time.time() - start_time} seconds")

# %%
start_time = time.time()
vectorizer: BaseVectorize = VectorizeWithDict(vector_dict, 10)
companies_vectors = vectorizer.vectorize(json_strs)
logger.log(f"Vectorizing {len(companies_vectors)} strings took {time.time() - start_time} seconds")


# %%
start_time = time.time()
search = LinearVectorSearch(companies_vectors)
logger.log(f"Storing vectors took {time.time() - start_time} seconds")


# %%
query_dict = {
    "product_name": "Oldtime Lanterns Working",
    "manufacturer": "Busch"
}
start_time = time.time()
query_str = process_product(query_dict)
query_vector = vectorizer.vectorize([query_str])[0]
result_ids = search.search(query_vector)
logger.log(f"Query took {time.time() - start_time} seconds")

result_jsons = [json_strs[result_id] for result_id in result_ids]
logger.log(f"Results:\n{result_jsons}")

# %%


