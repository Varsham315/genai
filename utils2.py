import streamlit as st
from deep_translator import GoogleTranslator

# 🌍 Supported Languages
languages = {
    "English": "en",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Chinese": "zh-cn",
    "Hindi": "hi"
}

# ✅ Initialize language selection in session state
if "selected_language" not in st.session_state:
    st.session_state.selected_language = "en"  # Default to English

# **Function to Translate Text Dynamically**
def translate_text(text):
    if "selected_language" not in st.session_state:
        st.session_state.selected_language = "en"  # Fallback to English

    if st.session_state.selected_language == "en":
        return text  # No translation needed for English
    
    try:
        return GoogleTranslator(source="auto", target=st.session_state.selected_language).translate(text)
    except Exception as e:
        return f"⚠ Translation Error: {str(e)}"
