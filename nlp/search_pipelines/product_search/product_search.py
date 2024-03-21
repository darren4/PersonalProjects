# %%
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
from typing import Final, Dict, List

BASE_PATH: Final[str] = f"{os.getenv('PYTHONPATH')}/nlp/search_pipelines/product_search"


logger = Logger(f"{BASE_PATH}/logs.txt")

def jsonable_to_str(json_obj):
    return json.dumps(json_obj, separators=(",", ":"))


print(f"{BASE_PATH}/amazon_products.csv")
raw_data = pd.read_csv(f"{BASE_PATH}/amazon_products.csv")
print(f"Product data length: {len(raw_data)}")
raw_data = raw_data.head(1000)
raw_data = raw_data[["product_name", "manufacturer"]]
json_dicts = raw_data.to_dict("records")
json_strs = [clean_str(json.dumps(json_dict)) for json_dict in json_dicts]

# %%
start_time = time.time()
vector_dict: Dict[str, List] = read_vectors_from_path(f"{BASE_PATH}/vectors.txt")
vectorizer: BaseVectorize = VectorizeWithDict(vector_dict, 10)
companies_vectors = vectorizer.vectorize(json_strs)
logger.log(f"Vectorizing {len(companies_vectors)} strings took {time.time() - start_time} seconds")


# %%
start_time = time.time()
search = LinearVectorSearch(companies_vectors)
logger.log(f"Storing vectors took {time.time() - start_time} seconds")


# %%
query_dict = {
    "product_name": "Ohigawa Railway SL Kawane-ji Model Train",
    "manufacturer": "Kato"
}
start_time = time.time()
query_str = json.dumps(query_dict)
query_vector = vectorizer.vectorize([query_str])[0]
result_ids = search.search(query_vector)
logger.log(f"Query took {time.time() - start_time} seconds")

result_jsons = [json_strs[result_id] for result_id in result_ids]
logger.log(f"Results:\n{result_jsons}")

# %%


