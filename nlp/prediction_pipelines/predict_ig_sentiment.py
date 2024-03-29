# %%
import pandas as pd
from nlp.glove.read_vectors import get_vector_dict
from nlp.vectorize.vectorize_with_glove import VectorizeWithGloVe
from sklearn.model_selection import train_test_split
import os

# %%
word_vector_dict, EMBED_LEN = get_vector_dict(
    f"{os.getenv('PYTHONPATH')}/nlp/glove/embeddings/instagram_vectors.txt"
)

# %%
ig_data = pd.read_csv(f"{os.getenv('PYTHONPATH')}/nlp/data/instagram_sample.csv")

vectorizer = VectorizeWithGloVe(word_vector_dict, EMBED_LEN)
ig_data["matrix"] = pd.Series(vectorizer.vectorize(list(ig_data["review_description"])))


# %%
def _normalize_matrix(row):
    row["matrix"] = row["matrix"].flatten()
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

# %%
