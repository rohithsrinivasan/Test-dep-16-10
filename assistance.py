import streamlit as st
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

def main():
    load_dotenv()
    google_api_key = os.getenv("GOOGLE_API_KEY")

    assistant = GenerativeAIAssistant(model_name="gemini-pro", api_key=google_api_key)

    st.title("Generative AI Assistant")

    user_input = st.text_input("Enter your prompt:")

    if st.button("Generate Response"):
        response = assistant.generate_response(user_input)
        st.text_area("Response:", value=response, height=200)

if __name__ == "__main__":
    main()