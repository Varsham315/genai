import streamlit as st
import os
from PyPDF2 import PdfReader
from dotenv import load_dotenv
import google.generativeai as genai
from deep_translator import GoogleTranslator
from gtts import gTTS
import tempfile
from langchain.text_splitter import RecursiveCharacterTextSplitter, CharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

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

# Audio function
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

# FAISS-related functions with improved error handling
def get_text_chunks(text):
    try:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=10000,
            chunk_overlap=1000,
            separators=["\n\n", "\n", ".", " ", ""]
        )
        chunks = text_splitter.split_text(text)
        return chunks
    except Exception as e:
        st.error(f"Error splitting text: {str(e)}")
        return []

def get_vector_store(text_chunks):
    try:
        if not text_chunks:
            raise ValueError("No text chunks provided for vector store creation")
            
        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=GOOGLE_API_KEY
        )
        
        # Verify embeddings work with a small test
        test_embedding = embeddings.embed_query("test")
        if not test_embedding:
            raise ValueError("Embedding test failed")
            
        vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
        return vector_store
    except Exception as e:
        st.error(f"Error creating vector store: {str(e)}")
        return None

def get_conversational_chain():
    try:
        prompt_template = """
        Answer the question as detailed as possible from the provided context. Make sure to provide all the details.
        If the answer is not in the provided context, just say, "The answer is not available in the context." Do not provide a wrong answer.
        Context: {context}
        Question: {question}
        Answer:
        """
        model = ChatGoogleGenerativeAI(
            model="gemini-pro",
            temperature=0.3,
            google_api_key=GOOGLE_API_KEY
        )
        prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
        chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)
        return chain
    except Exception as e:
        st.error(f"Error creating conversational chain: {str(e)}")
        return None

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
if "vector_store" not in st.session_state:
    st.session_state.vector_store = None

uploaded_files = st.file_uploader(translate_text("📂 Upload Your PDFs"), type=["pdf"], accept_multiple_files=True)

if uploaded_files:
    extracted_texts = extract_text_from_pdfs(uploaded_files)
    if extracted_texts:
        st.session_state.text_chunks = extracted_texts
        # Process text with FAISS
        combined_text = " ".join(extracted_texts)
        chunks = get_text_chunks(combined_text)
        
        if chunks:  # Only proceed if we got valid chunks
            with st.spinner(translate_text("Creating vector store (this may take a moment)...")):
                vector_store = get_vector_store(chunks)
                if vector_store:
                    st.session_state.vector_store = vector_store
                    st.success(translate_text("✅ Vector store created successfully!"))
                else:
                    st.error(translate_text("❌ Failed to create vector store"))

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