# %%
from nlp.vectorize.base_vectorize import BaseVectorize
from nlp.vectorize.vectorize_with_hg import VectorizeWithHG
from nlp.vector_search.linear_search import LinearVectorSearch
from nlp.vector_search.perpendicular_search import PerpendicularVectorSearch
from utils.logger import Logger

import os
import time
import json
import pandas as pd

logger = Logger("nlp/search_pipelines/product_search.txt")

def jsonable_to_str(json_obj):
    return json.dumps(json_obj, separators=(",", ":"))


# %%
raw_data = pd.read_csv(f"{os.getenv('PYTHONPATH')}/nlp/data/amazon_products.csv").head(100)
json_strs = []
raw_data.apply(lambda row: json_strs.append(jsonable_to_str({
    "product_name": row["product_name"],
    "manufacturer": row["manufacturer"]
})), axis=1)

# %%
vectorizer: BaseVectorize = VectorizeWithHG("sentence-t5-base", convert_to_tensor=True)
start_time = time.time()
companies_vectors = vectorizer.vectorize(json_strs)
logger.log(f"Vectorizing {len(companies_vectors)} strings took {time.time() - start_time} seconds")


# %%
start_time = time.time()
search = PerpendicularVectorSearch(companies_vectors)
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


