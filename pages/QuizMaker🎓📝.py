import streamlit as st
import google.generativeai as genai
import os
import json
import time
import re  # ✅ Import regex for JSON extraction
from utils2 import translate_text  # Import translation function

# 🌟 Configure Google Gemini AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# 🎨 Load Custom CSS
def load_css():
    with open("styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# ✨ Function to Generate AI Quiz in JSON Format
def generate_quiz(text, num_questions=5, max_retries=3):
    try:
        model = genai.GenerativeModel('gemini-1.5-pro')

        for attempt in range(max_retries):
            time.sleep(1.5)  # Prevent excessive API calls

            # 🔍 AI Prompt for Generating JSON Quiz
            prompt = f"""
            Generate {num_questions} multiple-choice questions (MCQs) based on this text.
            **Return only valid JSON** formatted like this:
            {{
              "questions": [
                {{
                  "id": 1,
                  "question": "What is the purpose of assembler directives?",
                  "options": [
                    "A. To define segments and allocate space for variables",
                    "B. To represent specific machine instructions",
                    "C. To simplify the programmer's task",
                    "D. To provide information to the assembler"
                  ],
                  "correct_answer": "D. To provide information to the assembler"
                }},
                ...
              ]
            }}
            **DO NOT RETURN ANYTHING ELSE EXCEPT JSON.**
            Text: {text}
            """

            response = model.generate_content(prompt)

            # 🔎 Step 2: Extract Only JSON Part
            json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if json_match:
                json_text = json_match.group(0)  # Extract JSON portion
            else:
                st.warning(translate_text(f"⚠ AI did not return valid JSON. Retrying... ({attempt+1}/{max_retries})"))
                continue  # Try again

            # 🔎 Step 3: Validate and Fix JSON Formatting
            try:
                quiz_data = json.loads(json_text)  # Convert response to JSON
                if "questions" in quiz_data and len(quiz_data["questions"]) == num_questions:
                    return quiz_data  # ✅ Valid JSON, return result
                else:
                    st.warning(translate_text(f"⚠ AI did not generate {num_questions} questions. Retrying... ({attempt+1}/{max_retries})"))
            except json.JSONDecodeError:
                st.warning(translate_text(f"⚠ JSON parsing failed. Retrying... ({attempt+1}/{max_retries})"))

        st.error(translate_text("❌ AI failed to generate valid quiz questions after multiple attempts."))
        return {"questions": []}

    except Exception as e:
        st.error(translate_text(f"❌ Error generating quiz: {str(e)}"))
        return {"questions": []}

# 📝 **Main Quiz Page**
def quiz():
    st.markdown(f"<h1 style='text-align: center;'>{translate_text('📝 AI-Generated Quiz')}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; font-size: 18px;'>{translate_text('Test Your Knowledge with AI-Generated Questions')}</p>", unsafe_allow_html=True)
    st.write("---")

    # **Subheading & Image**
    col1, col2 = st.columns([3, 1])  # Adjust column width ratio

    with col1:
        st.markdown(f"### {translate_text('🎯 Test Your Knowledge')}")
        st.markdown(f"""
        - 🧠 **{translate_text('Challenge yourself')}** {translate_text('with AI-generated multiple-choice questions')}  
        - 📚 **{translate_text('Based on the PDFs you\'ve uploaded')}**  
        - 🎓 **{translate_text('Great for self-assessment & learning')}**  
        """)
        num_questions = st.slider(translate_text("🔢 Select Number of Questions"), min_value=1, max_value=20, value=5)

    with col2:
        st.image("img/quiz2.jpg", width=200, caption=translate_text("Take the AI Quiz!"))  # Adjust path & size

    # **Check if PDFs are uploaded**
    if "text_chunks" not in st.session_state or not st.session_state.text_chunks:
        st.warning(translate_text("⚠ Please upload PDFs on the Home page first!"))
        return

    # **Initialize session state for storing quiz data**
    if "quiz_data" not in st.session_state:
        st.session_state.quiz_data = {"questions": []}
    if "user_answers" not in st.session_state:
        st.session_state.user_answers = {}

    # **Generate Quiz Button**
    if st.button(translate_text("🎯 Generate Quiz")):
        with st.spinner(translate_text("🔍 Generating questions...")):
            quiz_data = generate_quiz(st.session_state.text_chunks, num_questions)

        if quiz_data["questions"]:
            st.session_state.quiz_data = quiz_data
            st.rerun()  # ✅ Ensures UI updates properly

    # **Display generated questions**
    if st.session_state.quiz_data["questions"]:
        st.success(translate_text("✅ Quiz Generated! Answer the following questions:"))

        for q in st.session_state.quiz_data["questions"]:
            st.subheader(f"Q{q['id']}: {translate_text(q['question'])}")

            # Ensure options are displayed correctly
            if "options" in q and isinstance(q["options"], list):
                st.session_state.user_answers[q["id"]] = st.radio(
                    f"{translate_text('Choose the correct answer for')} Q{q['id']}:",
                    [translate_text(opt) for opt in q["options"]],
                    key=f"question_{q['id']}"
                )

                # **Show Answer Button**
                if st.button(translate_text(f"Show Answer for Q{q['id']}"), key=f"answer_{q['id']}"):
                    st.success(f"✅ {translate_text('Correct Answer')}: **{translate_text(q['correct_answer'])}**")

            st.write("---")  # Divider between questions

# **Run the App**
if __name__ == "__main__":
    quiz()
