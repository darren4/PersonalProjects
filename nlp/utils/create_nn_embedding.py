import torch
import numpy as np
from torch import nn
import torch.nn.functional as F
import torch.optim as optim
import matplotlib.pyplot as plt
import os


def get_neighbor_pairs_list(corpus_list, forward_count=2, backward_count=2):
    pairs_list = []
    for s_list in corpus_list:
        for i in range(len(s_list)):
            for j in range(1, forward_count + 1):
                try:
                    pairs_list.append([s_list[i], s_list[i + j]])
                except IndexError:
                    break
            for j in range(1, backward_count + 1):
                if i - j < 0:
                    break
                pairs_list.append([s_list[i], s_list[i - j]])
    return pairs_list


def get_word_dict(corpus_list):
    all_words = []
    word_dict = {}
    for s_list in corpus_list:
        for word in s_list:
            if word not in word_dict:
                word_dict[word] = 0
                all_words.append(word)

    all_words = sorted(all_words)
    for i in range(len(all_words)):
        word_dict[all_words[i]] = i
    return word_dict


def word_pairs_to_numpy_arrays(pairs_list, word_dict):
    vocab_size = len(word_dict)
    left_arrays = []
    right_arrays = []
    for pair in pairs_list:
        left, right = pair[0], pair[1]
        left_array, right_array = np.zeros(vocab_size), np.zeros(vocab_size)
        left_array[word_dict[left]], right_array[word_dict[right]] = 1, 1
        left_arrays.append(left_array)
        right_arrays.append(right_array)
    left_arrays, right_arrays = torch.from_numpy(
        np.asarray(left_arrays)
    ), torch.from_numpy(np.asanyarray(right_arrays))
    left_arrays, right_arrays = left_arrays.to(torch.float32), right_arrays.to(
        torch.float32
    )
    return left_arrays, right_arrays


def define_nn(vocab_size, embed_size=2):
    class EmbeddingNN(nn.Module):
        def __init__(self):
            super().__init__()
            self.linear1 = nn.Linear(vocab_size, embed_size)
            self.linear2 = nn.Linear(embed_size, vocab_size)

        def forward(self, x):
            x = self.linear1(x)
            x = self.linear2(x)
            return x

    model = EmbeddingNN().to("cpu")
    print(f"Word Embedding Model: \n{model}\n")
    return model


def optimize_nn(
    model, left_side, right_side, optimizer, criterion=nn.CrossEntropyLoss()
):
    print(f"Training Word Embedding")
    for epoch in range(30):  # loop over the dataset multiple times
        # forward + backward + optimize
        optimizer.zero_grad()
        outputs = model(left_side)
        loss = criterion(outputs, right_side)
        loss.backward()
        optimizer.step()
        print(f"Epoch {epoch} loss: {loss.item()}")
    print("")
    print("Finished Creating Word Embedding\n")


def get_basic_word_embeddings(clean_corpus):
    pairs_list = get_neighbor_pairs_list(clean_corpus)
    word_dict = get_word_dict(clean_corpus)
    vocab_size = len(word_dict)
    left_side, right_side = word_pairs_to_numpy_arrays(pairs_list, word_dict)
    model = define_nn(vocab_size, 2)
    optimizer = optim.SGD(model.parameters(), lr=0.001, momentum=0.9)
    optimize_nn(model, left_side, right_side, optimizer)
    return model, word_dict


def display_word_weights(word_dict, weights, max_display_size=None):
    if not max_display_size:
        max_display_size = len(word_dict)
    embedding_dict = {}
    for i, word in enumerate(word_dict):
        if len(embedding_dict) == max_display_size:
            break
        embedding_dict[word] = weights[i]
    plt.figure(figsize=(10, 10))
    for word in embedding_dict:
        coord = embedding_dict[word].detach().numpy()
        plt.scatter(coord[0], coord[1])
        plt.annotate(word, (coord[0], coord[1]))

    if os.path.exists("embeddings.png"):
        os.remove("embeddings.png")
    plt.show()
