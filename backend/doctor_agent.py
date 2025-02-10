from langchain_community.llms import Ollama
import re

# Load the AI model
def load_model():
    return Ollama(model="deepseek-r1:1.5B")

llm = load_model()

# List of medical questions
QUESTIONS = [
    "How long have you had these symptoms?",
    "Do you have any other symptoms? (e.g., chills, cough, nausea, sore throat, dizziness)?",
    "Have you noticed any breathing issues, chest pain, or fatigue?",
    "Any recent exposure to sick individuals or known infections?",
]

# Function to get the next question
def get_next_question(chat_history):
    """Finds the next unanswered question based on chat history."""
    answered_questions = {msg["text"] for msg in chat_history if msg["sender"] == "bot"}
    
    for question in QUESTIONS:
        if question not in answered_questions:
            return question  # Return the next unanswered question
    
    return None  # If all questions are answered, return None

# Function to generate final diagnosis
def generate_diagnosis(symptoms, responses):
    response_text = "\n".join([f"{q} {a}" for q, a in responses.items()])
    
    prompt = (
        "You are an AI doctor assistant. Based on the patient's responses, analyze the symptoms and provide a structured final report.\n"
        "Include:\n"
        "1️⃣ Possible conditions.\n"
        "2️⃣ Medical reasoning.\n"
        "3️⃣ Recommended medications & care.\n\n"
        f"Patient reported symptoms: {symptoms}\n\nPatient's answers:\n{response_text}"
    )
    
    response = llm.invoke(prompt)
    clean_response = re.sub(r"<think>.*?</think>", "", response, flags=re.DOTALL).strip()
    return clean_response
