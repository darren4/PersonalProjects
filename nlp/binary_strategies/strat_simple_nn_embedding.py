from binary_strategies.strat_base import Strategy
import numpy as np
from utils.cleaning import sentence_to_list
from utils.create_nn_embedding import get_basic_word_embeddings
from sklearn.linear_model import LogisticRegression


def extend_list(nums, count):
    if len(nums) == 0:
        nums = []
        for i in range(count):
            nums.append(0)
        return nums
    elif len(nums) == 1:
        val = nums[0]
        nums = [val]
        for i in range(count):
            nums.append(val)
        return nums
    else:
        for _ in range(count):
            extended_nums = [nums[0]]
            for i in range(1, len(nums)):
                extended_nums.append((nums[i - 1] + nums[i]) / 2)
                extended_nums.append(nums[i])
            nums = [extended_nums[0]]
            for i in range(1, len(extended_nums), 2):
                nums.append(extended_nums[i])
            nums.append(extended_nums[-1])
        return nums


class SimpleNNEmbedding(Strategy):
    def __init__(self):
        self.corpus = []
        self.sentence_list_pairs = []
        self.longest_sentence = 0
        self.embed_dim = 0

        self.word_embedding_vectors = {}
        self.ml_model = None

    def _add_to_corpus(self, row):
        lhs, rhs = sentence_to_list(row[0]), sentence_to_list(row[1])
        self.longest_sentence = max(self.longest_sentence, len(lhs), len(rhs))
        self.corpus.append(lhs)
        self.corpus.append(rhs)
        self.sentence_list_pairs.append([lhs, rhs])

    def _normalized_embeddings_diff(self, word_pair):
        left_word_list = word_pair[0]
        left_embed_vector = np.zeros((self.longest_sentence, self.embed_dim))
        for i in range(len(left_word_list)):
            try:
                embedding_vec = np.array(self.word_embedding_vectors[left_word_list[i]])
            except KeyError:
                embedding_vec = np.array((self.embed_dim))
            left_embed_vector[i] = embedding_vec
        for i in range(self.embed_dim):
            left_embed_slice_list = list(left_embed_vector[0 : len(left_word_list), i])
            extended_embedding = extend_list(
                left_embed_slice_list,
                max(0, self.longest_sentence - len(left_word_list)),
            )
            left_embed_vector[:, i] = np.array(extended_embedding)
        right_word_list = word_pair[1]
        right_embed_vector = np.zeros((self.longest_sentence, self.embed_dim))
        for i in range(len(right_word_list)):
            try:
                embedding_vec = np.array(
                    self.word_embedding_vectors[right_word_list[i]]
                )
            except KeyError:
                embedding_vec = np.array((self.embed_dim))
            right_embed_vector[i] = embedding_vec
        for i in range(self.embed_dim):
            right_embed_slice_list = list(
                right_embed_vector[0 : len(right_word_list), i]
            )
            extended_embedding = extend_list(
                right_embed_slice_list,
                max(0, self.longest_sentence - len(right_word_list)),
            )
            right_embed_vector[:, i] = np.array(extended_embedding)
        diff_vector = abs(left_embed_vector - right_embed_vector)
        return np.linalg.norm(diff_vector, axis=0)

    def train(self, X, y):
        # edit here
        np.apply_along_axis(self._add_to_corpus, 1, X)
        model, word_dict = get_basic_word_embeddings(self.corpus)
        embeddings = model.linear2.weight.detach().numpy()
        self.embed_dim = len(embeddings[0])
        for word, num in word_dict.items():
            self.word_embedding_vectors[word] = embeddings[num]
        # how to modularize this away from the strategy
        X_embeddings_diff = np.array(
            list(map(self._normalized_embeddings_diff, self.sentence_list_pairs)),
            dtype=object,
        )
        y = np.array(y)
        self.ml_model = LogisticRegression()
        self.ml_model.fit(X_embeddings_diff, y)
        return self

    def predict(self, X):
        def _clean_input(lhs_rhs):
            lhs, rhs = sentence_to_list(lhs_rhs[0]), sentence_to_list(lhs_rhs[1])
            lhs, rhs = lhs[0 : self.longest_sentence], rhs[0 : self.longest_sentence]
            return [lhs, rhs]

        X_clean = list(map(_clean_input, X))
        X_embeddings = np.array(list(map(self._normalized_embeddings_diff, X_clean)))
        return self.ml_model.predict(X_embeddings)


if __name__ == "__main__":
    test_train_data_X = np.array(
        [
            ["the cat and the dog", "the dog and the cat"],
            ["computers on tables", "tables with computers on them"],
            ["lamp on desk", "lamp very bright"],
            ["lamp on desk", "blah blah blah blah"],
        ],
        dtype=object,
    )
    test_train_data_Y = np.array([True, True, False, True], dtype=bool)
    e = SimpleNNEmbedding()
    e.train(test_train_data_X, test_train_data_Y)
