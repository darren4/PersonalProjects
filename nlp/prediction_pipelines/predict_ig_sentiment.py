# %%
import pandas as pd
from glove.read_vectors import get_vector_dict
from utils.process_corpus import StringsToVectors, NormalizeVectorLens
from sklearn.model_selection import train_test_split

# %%
word_vector_dict, EMBED_LEN = get_vector_dict("glove/data/instagram_vectors.txt")

# %%
ig_data = pd.read_csv("data/instagram.csv")

clean_descriptions = StringsToVectors(word_vector_dict, EMBED_LEN)
process_columns = {"review_description": "matrix"}
ig_data, target_len = clean_descriptions.to_vectors(ig_data, process_columns)

# %%
vector_len_normalizer = NormalizeVectorLens(target_len, EMBED_LEN, "ADJUST_LEN")


def _normalize_matrix(row):
    row["matrix"] = vector_len_normalizer.noramlize(row["matrix"]).flatten()
    return row


ig_data = ig_data.apply(_normalize_matrix, axis=1)

# %%

ig_train, ig_test = train_test_split(ig_data)
X_train, y_train = list(ig_train["matrix"]), list(ig_train["rating"])
X_test, y_test = list(ig_test["matrix"]), list(ig_test["rating"])

# %%

from sklearn.linear_model import LinearRegression
from sklearn.neural_network import MLPRegressor

models = {"Linear": LinearRegression(), "NN": MLPRegressor((16, 8, 4))}

# %%


def calculate_error(ground_truth, predictions):
    assert len(ground_truth) == len(predictions)
    diff = 0
    for i in range(len(ground_truth)):
        diff += abs(ground_truth[i] - predictions[i])
    return diff / len(ground_truth)


for model_name, model in models.items():
    print(f"Results for {model_name}")
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)
    print(f"Loss: {calculate_error(y_test, predictions)}")
