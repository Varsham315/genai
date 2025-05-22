import streamlit as st
import os
from PyPDF2 import PdfReader
from dotenv import load_dotenv
import google.generativeai as genai
from deep_translator import GoogleTranslator
from gtts import gTTS
import tempfile

# 📌 Set Up Page Configuration
st.set_page_config(page_title="Multi-PDF AI Tool", page_icon="📚", layout="wide")

# 🌎 Language Selection
languages = {
    "English": "en",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Chinese": "zh-cn",
    "Hindi": "hi"
}

# Store selected language in session state
if "selected_language" not in st.session_state:
    st.session_state.selected_language = "en"

selected_lang = st.sidebar.selectbox("🌍 Select Language:", list(languages.keys()))
st.session_state.selected_language = languages[selected_lang]

# 🔄 Function to Translate Text
def translate_text(text):
    if st.session_state.selected_language == "en":
        return text  # No translation needed for English
    try:
        return GoogleTranslator(source="auto", target=st.session_state.selected_language).translate(text)
    except Exception as e:
        return f"⚠ Translation Error: {str(e)}"

# 🎨 Load Custom CSS
def load_css():
    with open("styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# 🌍 Load API Key
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    st.error(translate_text("❌ Google API Key is missing! Please set it in the .env file."))
else:
    genai.configure(api_key=GOOGLE_API_KEY)
#audio
def play_text_as_audio(text, language_code="en"):
    try:
        tts = gTTS(text=text, lang=language_code)
        with tempfile.NamedTemporaryFile(delete=True, suffix=".mp3") as tmp_file:
            tts.save(tmp_file.name)
            audio_file = open(tmp_file.name, "rb")
            st.audio(audio_file.read(), format="audio/mp3")
    except Exception as e:
        st.error(f"❌ Error generating audio: {str(e)}")


# 📂 Function to Extract Text from PDFs
def extract_text_from_pdfs(uploaded_files):
    extracted_texts = []
    for pdf_file in uploaded_files:
        try:
            pdf_reader = PdfReader(pdf_file)
            text = "\n".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])
            if text.strip():
                extracted_texts.append(text.strip())
            else:
                st.warning(translate_text(f"⚠ Could not extract text from {pdf_file.name}. It may be an image-based PDF."))
        except Exception as e:
            st.error(translate_text(f"❌ Error reading {pdf_file.name}: {str(e)}"))
    return extracted_texts

# 🚀 Attractive Heading
st.markdown(f"<h1 style='text-align: center; color: #FFD700;'>{translate_text('🚀 SmartPDF AI Tool')}</h1>", unsafe_allow_html=True)

# 🖼 Sidebar Content (Image & Title)
st.sidebar.image("img/Robot.jpg", caption=translate_text("AI Assistant"), width=200)
st.sidebar.title(translate_text("🚀 SmartPDF AI Tool"))
st.sidebar.markdown(translate_text("**Enhance your PDFs with AI-powered features!**"))

# 📂 Upload PDF Section
st.write("---")
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown(translate_text("🔍 **What You Can Do With This Tool:**"), unsafe_allow_html=True)
    st.markdown(translate_text("""
    ✅ Extract text from multiple PDFs  
    🤖 Get AI-powered answers instantly  
    📝 Summarize lengthy documents  
    🎓 Generate quizzes from content  
    🧠 Create AI-powered mind maps  
    📖 Get book recommendations  
    """), unsafe_allow_html=True)

with col2:
    st.image("img/pdf.jpg", width=250, caption=translate_text("Meet Your AI Assistant 🤖"))

# 📝 Store Uploaded PDFs in Session
if "text_chunks" not in st.session_state:
    st.session_state.text_chunks = []

uploaded_files = st.file_uploader(translate_text("📂 Upload Your PDFs"), type=["pdf"], accept_multiple_files=True)

if uploaded_files:
    extracted_texts = extract_text_from_pdfs(uploaded_files)
    if extracted_texts:
        st.session_state.text_chunks = extracted_texts  
        st.success(translate_text(f"✅ Extracted text from {len(uploaded_files)} PDFs successfully!"))

# 🔗 Feature Navigation
menu_options = {
    "🏠 Home": None,
    "❓ Q&A": "pages/ContextQ&A❓💡.py",
    "🤖 Chat": "pages/Paraphrase✨🔄.py",
    "📚 Summary": "pages/Summary✍️📖.py",
    "📝 Quiz": "pages/QuizMaker🎓📝.py",
    "🧠 Mind Map": "pages/Mindmap🧠🗺️.py",
    "📊 Visual": "pages/VisualCloud 📊📜.py",
    "📖 Books": "pages/BooksFinder📚🔍.py",
    "🔗 Links": "pages/RelevantLinks🔗🌎.py",
    "🎮 Hangman": "pages/HangmanGame🎮📝.py"
}

selected_page = st.sidebar.selectbox(translate_text("📌 Navigate to Feature:"), list(menu_options.keys()))

# 🏃 Run Selected Feature Page
if selected_page != "🏠 Home" and selected_page in menu_options:
    os.system(f"streamlit run {menu_options[selected_page]}")
