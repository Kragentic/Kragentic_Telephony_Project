import os
from langchain import LangChain
from openai import OpenAI
from claude import Claude

class AIAgent:
    def __init__(self):
        try:
            self.langchain = LangChain(api_key=os.getenv("LANGCHAIN_API_KEY"))
            self.openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            self.claude = Claude(api_key=os.getenv("CLAUDE_API_KEY"))
        except Exception as e:
            print(f"Error initializing AI agent: {e}")
            raise

    def process_input(self, input_text):
        # Process input using LangChain
        try:
            response = self.langchain.process(input_text)
            return response
        except Exception as e:
            print(f"Error processing input: {e}")
            return None

    def generate_response(self, input_text):
        # Generate response using OpenAI or Claude
        try:
            if os.getenv("USE_CLAUDE") == "true":
                response = self.claude.generate(input_text)
            else:
                response = self.openai.generate(input_text)
            return response
        except Exception as e:
            print(f"Error generating response: {e}")
            return None
