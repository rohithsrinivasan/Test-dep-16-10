import os
from dotenv import load_dotenv
import google.generativeai as genai
from typing import Optional

class GenerativeAIAssistant:

    def __init__(self, model_name: str, api_key: str):
        self.model = genai.GenerativeModel(model_name)
        genai.configure(api_key=api_key)

    def generate_response(self, prompt: str) -> str:
        response = self.model.generate_content(prompt)
        return response.text

    def interactive_session(self):
        print("Welcome to the generative AI assistant!")
        while True:
            user_input = input("Enter your prompt (or 'quit' to exit): ")
            if user_input.lower() == "quit":
                break
            response = self.generate_response(user_input)
            print(response)

if __name__ == "__main__":
    load_dotenv()
    google_api_key = os.getenv("GOOGLE_API_KEY")

    assistant = GenerativeAIAssistant(model_name="gemini-pro", api_key=google_api_key)
    assistant.interactive_session()