import streamlit as st
import google.generativeai as genai
import os
import base64
import time
from utils2 import translate_text  # Import translation function
import tempfile
from gtts import gTTS
# Configure Google Gemini AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Load Custom CSS
def load_css():
    with open("styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()
def play_text_as_audio(text, language_code="en"):
    try:
        tts = gTTS(text=text, lang=language_code)
        with tempfile.NamedTemporaryFile(delete=True, suffix=".mp3") as tmp_file:
            tts.save(tmp_file.name)
            audio_file = open(tmp_file.name, "rb")
            st.audio(audio_file.read(), format="audio/mp3")
    except Exception as e:
        st.error(f"❌ Error generating audio: {str(e)}")

# **Function to Generate AI-Powered Paraphrased Text**
def generate_paraphrase(text):
    try:
        time.sleep(1.5)
        model = genai.GenerativeModel('gemini-1.5-pro')
        response = model.generate_content(f"Paraphrase the following text in a clearer and more professional manner:\n\n{text}")

        if response.text:
            return response.text.strip()
        else:
            return translate_text("⚠ AI could not generate a paraphrase. Try again with different input.")
    except Exception as e:
        return f"❌ {translate_text('Error')}: {str(e)}"

# **Function to Create a Downloadable Text File**
def create_download_link(paraphrased_text):
    """Creates a download link for the paraphrased text."""
    text_bytes = paraphrased_text.encode()
    b64 = base64.b64encode(text_bytes).decode()
    return f'<a href="data:file/txt;base64,{b64}" download="paraphrased_text.txt">📥 {translate_text("Download Paraphrased Text")}</a>'

# **Main Paraphrasing Page**
def paraphrase():
    st.markdown(f"<h1 style='text-align: center;'>{translate_text('🤖 AI-Powered Paraphrasing')}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; font-size: 18px;'>{translate_text('Rephrase and improve your text effortlessly using AI!')}</p>", unsafe_allow_html=True)
    st.write("---")

    # **Check if PDFs are uploaded**
    if "text_chunks" not in st.session_state or not st.session_state.text_chunks:
        st.warning(translate_text("⚠ Please upload PDFs on the Home page first!"))
        return

    # **Layout: Left (Text Input), Right (Icon)**
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader(translate_text("✍ Enter Text to Paraphrase:"))
        text = st.text_area(translate_text("Type or paste text here..."), placeholder=translate_text("Example: The rapid growth of AI is transforming industries worldwide."))
    
    with col2:
        st.image("/Users/varshininaravula/Downloads/Multi-PDFs_ChatApp_AI-Agent-main/img/paraphrae.jpg", width=200)  # Adjust the path & size

    st.write("---")
    
    # **Generate paraphrase button**
    if st.button(translate_text("🔄 Paraphrase")):
        if not text.strip():
            st.error(translate_text("⚠ Please enter valid text to paraphrase."))
            return

        with st.spinner(translate_text("Paraphrasing... 🔄")):
            paraphrased_text = generate_paraphrase(text)

        # **Display paraphrased text in a styled box**
        st.success(translate_text("✅ AI-Paraphrased Text:"))
        st.markdown(f"<div style='padding:10px; border-radius:8px;'> {paraphrased_text} </div>", unsafe_allow_html=True)

        # **Copy & Download options**
        col_copy, col_download = st.columns([1, 1])
        with col_copy:
            st.text_area(translate_text("📋 Copy Paraphrased Text:"), paraphrased_text, height=150)

        with col_download:
            st.markdown(create_download_link(paraphrased_text), unsafe_allow_html=True)
        # 🔊 Voice Output Section (Text-to-Speech)
        if st.button(translate_text("🔊 Play Answer as Audio")):
            play_text_as_audio(paraphrased_text, language_code=st.session_state.selected_language)

# **Run the App**
if __name__ == "__main__":
    paraphrase()
