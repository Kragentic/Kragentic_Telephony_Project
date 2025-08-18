import os
from langchain import LangChain
from vector_db import VectorDB

class RAGCAG:
    def __init__(self):
        try:
            self.langchain = LangChain(api_key=os.getenv("LANGCHAIN_API_KEY"))
            self.vector_db = VectorDB(api_key=os.getenv("VECTOR_DB_API_KEY"))
        except Exception as e:
            print(f"Error initializing RAGCAG: {e}")
            raise

    def retrieve_knowledge(self, query):
        # Retrieve knowledge from vector DB
        try:
            results = self.vector_db.search(query)
            return results
        except Exception as e:
            print(f"Error retrieving knowledge: {e}")
            return None

    def augment_response(self, query, context):
        # Augment response with retrieved knowledge
        try:
            augmented_response = self.langchain.augment(query, context)
            return augmented_response
        except Exception as e:
            print(f"Error augmenting response: {e}")
            return None
