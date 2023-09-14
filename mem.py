from collections import deque
import openai
import numpy as np
from sklearn.neighbors import BallTree

class LongTermMemory:
    def __init__(self, max_size, api_key, model="text-embedding-ada-002"):
        self.max_size = max_size
        self.memory_deque = deque()
        self.embedding_to_text = {}
        self.api_key = api_key
        self.model = model
        openai.api_key = self.api_key  # Initialize the OpenAI client in the constructor
        self.tree = None  # BallTree for nearest neighbor search

    def add_memory(self, text):
        embedding = self.get_embedding(text)
        self.memory_deque.append(embedding)

        if len(self.memory_deque) > self.max_size:
            # Remove the oldest entry and its associated key-value pair
            oldest_embedding = self.memory_deque.popleft()
            del self.embedding_to_text[oldest_embedding]

        # Add the new memory to the dictionary
        self.embedding_to_text[tuple(embedding)] = text

        # Rebuild the BallTree
        embeddings = list(self.embedding_to_text.keys())
        self.tree = BallTree(embeddings)

    def find_memory(self, query_text):
        if not self.tree:
            return 'No relevant memories'
        query_embedding = self.get_embedding(query_text)

        # Query the BallTree for the nearest neighbor
        _, index = self.tree.query([query_embedding], k=1)
        nearest_embedding = list(self.embedding_to_text.keys())[index[0, 0]]
        text_result = self.embedding_to_text[nearest_embedding]

        return nearest_embedding

    def clear_memory(self):
        self.memory_deque.clear()
        self.embedding_to_text.clear()
        self.tree = None

    def get_embedding(self, text):
        text = text.replace("\n", " ")
        embedding_data = openai.Embedding.create(input=[text], model=self.model)['data'][0]
        embedding = np.array(embedding_data['embedding'])
        return embedding

# Example usage:
# Replace 'YOUR_API_KEY' with your actual OpenAI API key
#memory = LongTermMemory(max_size=100, api_key='YOUR_API_KEY')
