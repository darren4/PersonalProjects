import heapq
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
                if dist < results[0][0]:
                    heapq.heappop(results)
                    heapq.heappush(results, (dist, stored[1]))
            else:
                heapq.heappush(results, (dist, stored[1]))
        return results
