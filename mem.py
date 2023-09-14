from collections import deque
import openai
import numpy as np
from sklearn.neighbors import BallTree
from llm import LLMAgent
from profiler import parse_generation

class MemoryModule:
    def __init__(self, profile, max_size=100, model="text-embedding-ada-002"):
        self.model = LLMAgent(profile)
        self.embed_model = model
        self.max_size = max_size
        self.memory_deque = deque()
        self.embedding_to_text = {}
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

        return text_result

    def relevant_memory(self, planned_step):
        generation = self.model.prompt(f"""
Find the most relevant memory for this planned action:
$PLANNED_ACTION: {planned_step}
""")
        as_dict = parse_generation(generation)
        return self.find_memory(as_dict['MAIN_CONTENT'])

    def gen_memory(self, attempted_step, attempted_action, result, feedback):
        insight = self.model.prompt(f"""
Given the following information, generate a valuable insight that could help future planning.
$ATTEMPTED_STEP: {attempted_step}
$ATTEMPTED_ACTION: {attempted_action}
$RESULT_OF_ACTION: {result}
$FEEDBACK: {str(feedback)}
        """)
        as_dict = parse_generation(insight)
        self.add_memory(as_dict['MAIN_CONTENT'])

    def clear_memory(self):
        self.memory_deque.clear()
        self.embedding_to_text.clear()
        self.tree = None

    def get_embedding(self, text):
        text = text.replace("\n", " ") if text else ''
        embedding_data = openai.Embedding.create(input=[text], model=self.embed_model)['data'][0]
        embedding = np.array(embedding_data['embedding'])
        return embedding

