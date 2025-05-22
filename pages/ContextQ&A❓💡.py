import streamlit as st
import google.generativeai as genai
import os
import time
from utils2 import translate_text  # Import translation function

# Load CSS
def load_css():
    with open("styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# Configure Google Gemini AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to generate AI-powered answers
def generate_answer(question, context):
    try:
        time.sleep(1.5)
        model = genai.GenerativeModel('gemini-1.5-pro')
        response = model.generate_content(f"Based on this PDF content, provide an accurate answer to: {question}\n\n{context}")

        if response.text:
            return response.text.strip()
        else:
            return translate_text("⚠ AI could not generate a response. Try rephrasing your question.")
    except Exception as e:
        return f"{translate_text('❌ Error')}: {str(e)}"

# Main Q&A Page
def answer():
    st.markdown(f"<h1 style='text-align: center;'>{translate_text('❓ AI-Powered Q&A')}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; font-size: 18px;'>{translate_text('Ask any question from your uploaded PDFs, and AI will provide the best answer!')}</p>", unsafe_allow_html=True)
    st.write("---")

    # Check if PDFs are uploaded
    if "text_chunks" not in st.session_state or not st.session_state.text_chunks:
        st.warning(translate_text("⚠ Please upload PDFs on the Home page first!"))
        return
    
    # Create two sections (Left: Question, Right: Icon)
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader(translate_text("💡 Ask Your Question:"))
        question = st.text_input(translate_text("Type your question here..."), placeholder=translate_text("Example: What are the key concepts in the PDFs?"))
    
    with col2:
        st.image("img/q&a.jpg", width=200)  # Add a related image/icon

    # Generate answer button
    if st.button(translate_text("🔍 Get Answer")):
        if not question.strip():
            st.error(translate_text("⚠ Please enter a valid question."))
            return

        with st.spinner(translate_text("Thinking... 🤖")):
            pdf_text = " ".join(st.session_state.text_chunks)  # Combine all uploaded PDF text
            answer = generate_answer(question, pdf_text)

        # Display answer in a clean format
        st.success(translate_text("✅ AI Answer:"))
        st.markdown(f"<div style='padding:10px; border-radius:8px;'> {translate_text(answer)} </div>", unsafe_allow_html=True)

if __name__ == "__main__":
    answer()
