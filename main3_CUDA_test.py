import os
from dotenv import load_dotenv
import google.generativeai as genai
from typing import Optional
import cv2
import easyocr

class GenerativeAIAssistant:

    def __init__(self, model_name: str, api_key: str):
        self.model = genai.GenerativeModel(model_name)
        genai.configure(api_key=api_key)
        self.reader = easyocr.Reader(['en'])  # Initialize EasyOCR reader for English

    def generate_response(self, prompt: str) -> str:
        response = self.model.generate_content(prompt)
        return response.text

    def preprocess_image(self, image_path: str) -> str:
        """Use OpenCV to preprocess the image before extracting text."""
        try:
            # Read the image using OpenCV
            image = cv2.imread(image_path)

            # Convert the image to grayscale
            gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # Optional: Apply GaussianBlur to reduce noise
            blurred_image = cv2.GaussianBlur(gray_image, (5, 5), 0)

            # Optional: Apply thresholding to enhance text clarity
            _, thresholded_image = cv2.threshold(blurred_image, 150, 255, cv2.THRESH_BINARY_INV)

            # You can save the processed image if you want to see the output
            # cv2.imwrite('processed_image.png', thresholded_image)

            return thresholded_image
        except Exception as e:
            return f"Error processing image: {str(e)}"

    def extract_text_from_image(self, image_path: str) -> str:
        """Use EasyOCR to extract text from the preprocessed image."""
        try:
            # Preprocess the image using OpenCV
            processed_image = self.preprocess_image(image_path)

            # Convert OpenCV image format back to a format EasyOCR can read (if needed)
            if isinstance(processed_image, str):  # If there's an error in preprocessing
                return processed_image

            # EasyOCR expects file path or raw image input in the form of NumPy arrays
            # Extract text using EasyOCR
            result = self.reader.readtext(processed_image)
            text = ' '.join([res[1] for res in result])  # Extract the text from the OCR result

            return text
        except Exception as e:
            return f"Error extracting text from image: {str(e)}"

    def interactive_session(self):
        print("Welcome to the generative AI assistant!")
        while True:
            user_input = input("Enter 'text' for text input or 'image' for image input (or 'quit' to exit): ").lower()
            
            if user_input == "quit":
                break

            if user_input == "text":
                prompt = input("Enter your prompt: ")
                response = self.generate_response(prompt)
                print("AI Response:", response)

            elif user_input == "image":
                image_path = input("Enter the path to your image: ")
                text_from_image = self.extract_text_from_image(image_path)
                print("Extracted Text:", text_from_image)
                response = self.generate_response(text_from_image)
                print("AI Response:", response)

if __name__ == "__main__":
    load_dotenv()
    google_api_key = os.getenv("GOOGLE_API_KEY")

    assistant = GenerativeAIAssistant(model_name="gemini-pro", api_key=google_api_key)
    assistant.interactive_session()
