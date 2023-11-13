import numpy as np


class SimpleVectorSearch:
    def __init__(self):
        self.vectors = []

    def add(self, vector: np.array, key: list):
        self.vectors.append((vector, key))

    def search(self, vector: np.array, result_count=5):
        results = []
        for stored in self.vectors:
            dist = np.linalg.norm(abs(vector - stored[0]))

            if len(results) == result_count:
                if dist < results[-1][0]:
                    results[-1] = (dist, stored[1])
            else:
                results.append((dist, stored[1]))
            results.sort()
        return results
