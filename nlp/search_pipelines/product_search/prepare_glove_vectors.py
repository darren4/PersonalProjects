# %%
from utils.string_cleaning import clean_str
from nlp.glove.train import train_glove_vectors

import os
import pandas as pd
import json
import time

start_time = time.time()
raw_data = pd.read_csv(f"{os.getenv('PYTHONPATH')}/nlp/product_search/amazon_products.csv")
raw_data = raw_data[["product_name", "manufacturer"]]

json_dicts = raw_data.to_dict("records")
json_strs = [clean_str(json.dumps(json_dict)) for json_dict in json_dicts]
with open(f"{os.getenv('PYTHONPATH')}/nlp/product_search/amazon_products.json", "w") as fh:
    json.dump(json_strs, fh, indent=2)
glove_vectors = train_glove_vectors(json_strs)
print(time.time() - start_time)


# %%
