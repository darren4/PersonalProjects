# %%
from nlp.vectorize.base_vectorize import BaseVectorize
from nlp.vectorize.vectorize_with_huggingface_transformer import VectorizeWithHG
from nlp.vector_search.linear_search import LinearVectorSearch
from nlp.vector_search.perpendicular_search import PerpendicularVectorSearch
from utils.logger import Logger

import os
import time
import json

logger = Logger("nlp/search_pipelines/company_search.txt")


# %%
with open(f"{os.getenv('PYTHONPATH')}/nlp/data/companies.json", "r") as fh:
    companies_dicts = json.load(fh)

companies_jsons = [json.dumps(company_dict) for company_dict in companies_dicts]


# %%
vectorizer: BaseVectorize = VectorizeWithHG("sentence-t5-base", convert_to_tensor=True)
start_time = time.time()
companies_vectors = vectorizer.vectorize(companies_jsons)
logger.log(
    f"Vectorizing {len(companies_vectors)} strings took {time.time() - start_time} seconds"
)


# %%
start_time = time.time()
search = PerpendicularVectorSearch(companies_vectors)
logger.log(f"Storing vectors took {time.time() - start_time} seconds")


# %%
"""
7:
    {
        "name": "Global Logistics Solutions",
        "origin": "Dallas, USA",
        "size": "Large"
    }
"""
query_dict = {
    "name": "global logistics solutions corp",
    "origin": "Dallas, USA",
    "size": "Large",
}
start_time = time.time()
query_str = json.dumps(query_dict)
query_vector = vectorizer.vectorize([query_str])[0]
result_ids = search.search(query_vector)
logger.log(f"Query took {time.time() - start_time} seconds")
logger.log(result_ids)

# %%
