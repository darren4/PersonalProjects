# %%

import pandas as pd
import numpy as np
from nlp.glove.read_vectors import get_vector_dict
from nlp.utils.process_corpus import StringsToVectors, NormalizeVectorLens
import time
import os

# %%
start_time = time.time()
word_vector_dict, EMBED_LEN = get_vector_dict(f"{os.getenv('PYTHONPATH')}/nlp/glove/embeddings/glove.6B.50d.txt")
current_time = time.time()
print(f"Finished reading vectors in {current_time - start_time} seconds")
start_time = current_time
# %%
securities_data = pd.read_csv(f"{os.getenv('PYTHONPATH')}/nlp/data/security_descriptions.csv")

clean_descriptions = StringsToVectors(word_vector_dict, EMBED_LEN)
process_columns = {"description_x": "matrix_x", "description_y": "matrix_y"}
securities_data, max_len = clean_descriptions.to_vectors(
    securities_data, process_columns
)
current_time = time.time()
print(f"Finished preprocessing in {current_time - start_time} seconds")
start_time = current_time

# %%
vector_len_normalizer = NormalizeVectorLens(max_len, EMBED_LEN, "ADJUST_LEN")


def _normalize_matrix(row):
    row["matrix_x"] = vector_len_normalizer.noramlize(row["matrix_x"])
    row["matrix_y"] = vector_len_normalizer.noramlize(row["matrix_y"])
    row["matrix_x-y"] = (np.absolute(row["matrix_x"] - row["matrix_y"])).flatten()
    row["matrix_x-y_norm"] = np.linalg.norm(row["matrix_x-y"], axis=0)
    return row


securities_data = securities_data.apply(_normalize_matrix, axis=1)
print(f"Finished conversion to vectors in {time.time() - start_time} seconds")

# %%
securities_true = securities_data[securities_data["same_security"]]
securities_false = securities_data[~securities_data["same_security"]]
# import matplotlib.pyplot as plt

# plt.hist(securities_true["matrix_x-y_norm"])
# plt.show()
# plt.hist(securities_false["matrix_x-y_norm"])
# plt.show()

# %%
from sklearn.model_selection import train_test_split

securities_true = securities_true.sample(n=len(securities_false))
securities_train_true, securities_test_true = train_test_split(securities_true)
securities_train_false, securities_test_false = train_test_split(securities_false)
securities_train = pd.concat([securities_train_true, securities_train_false])
securities_test = pd.concat([securities_test_true, securities_test_false])
X_train, y_train = list(securities_train["matrix_x-y"]), list(
    securities_train["same_security"]
)
X_test, y_test = list(securities_test["matrix_x-y"]), list(
    securities_test["same_security"]
)

# %%
from sklearn.neural_network import MLPClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import confusion_matrix, f1_score

models = {
    "NN": {"model": MLPClassifier(hidden_layer_sizes=(100), random_state=0)},
    "Decision Tree": {"model": DecisionTreeClassifier(random_state=0)},
}
for model_name, model_data in models.items():
    print(f"Results for {model_name}")
    model_data["model"].fit(X_train, y_train)
    predictions = model_data["model"].predict(X_test)
    cm = confusion_matrix(y_test, predictions)
    print(cm)
    print(f1_score(y_test, predictions))
    models[model_name]["predictions"] = predictions

# %%
securities_test["predictions"] = list(models["NN"]["predictions"])
securities_test = securities_test[
    ["description_x", "description_y", "same_security", "predictions"]
]
securities_test.to_csv("resolve_securities_predictions.csv")
