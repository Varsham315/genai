🚀 SmartPDF-AI Tool
**SmartPDF-AI** is an intelligent, multilingual document analysis platform designed to make
reading and understanding PDFs smarter and more interactive. Powered by **Google Gemini
Pro**, **LangChain**, **FAISS**, and **Streamlit**, the tool offers summarization, question
answering, paraphrasing, visualization, and much more — all within an intuitive web interface.
Whether you're a student, researcher, or professional, SmartPDF-AI helps transform complex
documents into structured insights with just a few clicks.
✨ Key Features
- 📂 Upload and process multiple PDFs at once
- ❓ Ask context-based questions and get instant answers
- 📄 Summarize content into short, medium, or detailed formats
- 🔄 Rephrase complex text for better clarity
- 🎓 Automatically generate quizzes for study and testing
- 🧠 Create interactive mind maps
- 📊 Visualize data using word clouds and bar charts
- 🔈 Listen to responses using built-in text-to-speech
- 🌍 Translate content and interact in multiple languages
- 📚 Get relevant book recommendations based on topics
- 🔗 Access helpful web resources
- 🎮 Play Hangman to revise key terms in a fun way
🧠 Technologies Used
**Google Gemini Pro** – for generative tasks like Q&A and summarization
**LangChain** – for chaining AI tasks intelligently
**FAISS** – for fast vector-based similarity search
**Streamlit** – for the user-friendly web interface
**gTTS / pyttsx3** – for voice playback
**PyPDF2** – for extracting text from PDFs
**WordCloud / Matplotlib / Seaborn** – for data visualization
**Deep Translator** – for real-time language translation
🔧 How to Run the SmartPDF-AI Tool
1. **Download the Project:**
Clone this repository or download the ZIP file:
cd smartpdf-ai
2. **Install Required Libraries:**
Make sure you have Python 3.8+ installed.
Install all dependencies:
pip install -r requirements.txt
3. **Set Up Environment Variables:**
Create a `.env` file in the root directory and add your Google API key:
GOOGLE_API_KEY=your_google_api_key_here
4. **Run the Application:**
- Start the Streamlit app by running:
streamlit run app.py
5. **Upload Your PDFs and Explore Features:**
- Once the app launches in your browser, upload PDF files using the homepage.
- Navigate between features (Q&A, Summary, Paraphrasing, Mind Maps, etc.) using the sidebar.
📌 Ideal Use Cases
- 📘 Academic research paper analysis
- 🧑⚖ Legal document summarization and search
- 🏢 Business report insights and presentations
- 🎓 Educational study guides, quizzes, and audio content
- 🌍 Multilingual translation and learning support
