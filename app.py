# app.py
import streamlit as st
import google.generativeai as genai
import streamlit.components.v1 as components
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
from deep_translator import GoogleTranslator
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from langchain.chains import load_summarize_chain
from dotenv import load_dotenv
import pyttsx3  # For text-to-speech (pyttsx3)
from gtts import gTTS  # For text-to-speech (Google TTS)
import tempfile  # For temporary file handling
import json
from langchain.schema import Document
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import seaborn as sns
from collections import Counter
from utils import word_dict
from game import HangmanGame
import requests
from serpapi import search
from langchain.text_splitter import CharacterTextSplitter
# Set the page config at the very top of the script
st.set_page_config("Multi PDF Chatbot", page_icon=":scroll:")
def load_css():
    with open(os.path.join(os.path.dirname(__file__), "styles.css")) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
load_css()
# Load environment variables
load_dotenv()
os.getenv("GOOGLE_API_KEY")  # Ensure the key is loaded from .env
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))  # Set up the Google API

# Configure Gemini AI with the API key
def configure_genai():
    """Configure the Gemini AI with the API key."""
    if not os.getenv("GOOGLE_API_KEY"):
        st.error("API Key is missing. Please provide a valid Google API key.")
        return False
    try:
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        return True
    except Exception as e:
        st.error(f"Error configuring Google API: {str(e)}")
        return False

# Extract text from uploaded PDF file
def extract_text_from_pdf(pdf_file):
    """Extract text from uploaded PDF file."""
    try:
        pdf_reader = PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:  # Only add non-empty pages
                text += page_text + "\n"
        if not text.strip():
            st.warning("No text could be extracted from the PDF. Please ensure it's not scanned or image-based.")
            return None
        return text.strip()
    except Exception as e:
        st.error(f"Error reading PDF: {str(e)}")
        return None

# Generate mindmap markdown using Gemini AI
def create_mindmap_markdown(text):
    """Generate mindmap markdown using Gemini AI."""
    try:
        model = genai.GenerativeModel('gemini-pro')
        max_chars = 30000
        if len(text) > max_chars:
            text = text[:max_chars] + "..."
            st.warning(f"Text was truncated to {max_chars} characters due to length limitations.")
        prompt = """
        Create a hierarchical markdown mindmap from the following text.
        Use proper markdown heading syntax (# for main topics, ## for subtopics, ### for details).
        Focus on the main concepts and their relationships.
        Include relevant details and connections between ideas.
        Keep the structure clean and organized.
        Format the output exactly like this example:
        # Main Topic
        ## Subtopic 1
        ### Detail 1
        Key point 1
        Key point 2
        ### Detail 2
        ## Subtopic 2
        ### Detail 3
        ### Detail 4
        Text to analyze: {text}
        Respond only with the markdown mindmap, no additional text.
        """
        response = model.generate_content(prompt.format(text=text))
        if not response.text or not response.text.strip():
            st.error("Received empty response from Gemini AI")
            return None
        return response.text.strip()
    except Exception as e:
        st.error(f"Error generating mindmap: {str(e)}")
        return None

def create_markmap_html(markdown_content):
    """Create HTML with enhanced Markmap visualization."""
    markdown_content = markdown_content.replace('`', '\\`').replace('${', '\\${')
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="UTF-8">
    <style>
    #mindmap {{
        width: 100%;
        height: 600px;
        margin: 0;
        padding: 0;
    }}
    </style>
    <script src="https://cdn.jsdelivr.net/npm/d3@6"></script>
    <script src="https://cdn.jsdelivr.net/npm/markmap-view"></script>
    <script src="https://cdn.jsdelivr.net/npm/markmap-lib@0.14.3/dist/browser/index.min.js"></script>
    </head>
    <body>
    <svg id="mindmap"></svg>
    <script>
    window.onload = async () => {{
        try {{
            const markdown = `{markdown_content}`;
            const transformer = new markmap.Transformer();
            const {{root}} = transformer.transform(markdown);
            const mm = new markmap.Markmap(document.querySelector('#mindmap'), {{
                maxWidth: 300,
                color: (node) => {{
                    const level = node.depth;
                    return ['#2196f3', '#4caf50', '#ff9800', '#f44336'][level % 4];
                }},
                paddingX: 16,
                autoFit: true,
                initialExpandLevel: 2,
                duration: 500,
            }});
            mm.setData(root);
            mm.fit();
        }} catch (error) {{
            console.error('Error rendering mindmap:', error);
            document.body.innerHTML = '<p style="color: red;">Error rendering mindmap. Please check the console for details.</p>';
        }}
    }};
    </script>
    </body>
    </html>
    """
    return html_content

# Initialize the translator
translator = GoogleTranslator()

# Function for audio playback using pyttsx3 (Offline)
def play_audio_with_pyttsx3(response_text):
    engine = pyttsx3.init()
    engine.say(response_text)
    engine.runAndWait()

# Function for audio playback using gTTS (Online)
def play_audio_with_gtts(response_text):
    tts = gTTS(response_text)
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")  # Temporary file for audio
    temp_file.close()
    tts.save(temp_file.name)
    st.audio(temp_file.name, format="audio/mp3")

# Extract text from PDF files
def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

# Split large text into manageable chunks
def get_text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
    chunks = text_splitter.split_text(text)
    return chunks

# Create vector store for fast similarity search
def get_vector_store(text_chunks):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
    vector_store.save_local("faiss_index")

# Define a conversational chain with the Google AI model
def get_conversational_chain():
    prompt_template = """
    Answer the question as detailed as possible from the provided context. Make sure to provide all the details.
    If the answer is not in the provided context, just say, "The answer is not available in the context." Do not provide a wrong answer.
    Context: {context}
    Question: {question}
    Answer:
    """
    model = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.3)
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)
    return chain

def load_google_api_key():
    dotenv_path = "google.env"
    load_dotenv(dotenv_path)
    google_api_key = os.getenv("GOOGLE_API_KEY")
    if not google_api_key:
        raise ValueError(f"Unable to retrieve GOOGLE_API_KEY from {dotenv_path}")
    return google_api_key

def process_text(text):
    # Split the text into chunks using Langchain's CharacterTextSplitter
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(text)

    # Convert the chunks of text into embeddings to form a knowledge base
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")  # Use Google's embedding model
    knowledgeBase = FAISS.from_texts(chunks, embeddings)
    return knowledgeBase

def generate_summary_with_gemini(text, summary_type):
    # Configure Google Generative AI with the API key
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    model = genai.GenerativeModel('gemini-pro')

    # Define prompts based on the summary type
    if summary_type == "Short":
        prompt = f"""
        Summarize the content of the uploaded PDF file in approximately 1-2 sentences. 
        Focus on capturing the main idea of the document. Use concise language.
        The text is: ````{text}````
        """
    elif summary_type == "Medium":
        prompt = f"""
        Summarize the content of the uploaded PDF file in approximately 3-5 sentences. 
        Focus on capturing the main ideas and key points discussed in the document. 
        Ensure clarity and coherence in the summary.
        The text is: ````{text}````
        """
    elif summary_type == "Detailed":
        prompt = f"""
        Provide a detailed summary of the uploaded PDF file in approximately 6-10 sentences. 
        Include all important sections, key points, and supporting details. 
        Ensure the summary is comprehensive and well-structured.
        The text is: ````{text}````
        """

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        st.error(f"Error generating summary: {e}")
        return ""
# Handle user input: Translate question, perform similarity search, and respond
def user_input(user_question, selected_language):
    translated_question = GoogleTranslator(source=selected_language, target="en").translate(user_question)
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    new_db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
    docs = new_db.similarity_search(translated_question)
    chain = get_conversational_chain()
    response = chain({"input_documents": docs, "question": translated_question}, return_only_outputs=True)
    response_text = response["output_text"]
    print(response_text)
    reverse_translator = GoogleTranslator(source="en", target=selected_language)
    translated_response = reverse_translator.translate(response_text)
    st.write(f"Reply ({selected_language}): ", translated_response)
    st.write("🔊 Click below to listen:")
    if st.button("Play Response (Pyttsx3)"):
        play_audio_with_pyttsx3(translated_response)
    if st.button("Play Response (gTTS)"):
        play_audio_with_gtts(translated_response)

# Split large text into manageable chunks
def get_text_chunks(text):
    #text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    text_splitter = RecursiveCharacterTextSplitter()

    chunks = text_splitter.split_text(text)
    return chunks

# Extract key topics from the text using Gemini AI
def extract_key_topics(text_chunks):
    """Extract key topics or themes from the text using Gemini AI."""
    combined_text = " ".join(text_chunks)
    model = genai.GenerativeModel('gemini-pro')
    prompt = """
    Extract the top 5 key topics or themes from the following text.
    Respond with a comma-separated list of topics.
    Text: {text}
    """
    response = model.generate_content(prompt.format(text=combined_text))
    topics = [topic.strip() for topic in response.text.split(",")]
    return topics

# Filter sentences that are relevant to the given topics
def filter_sentences_by_topics(text_chunks, topics):
    """Filter sentences that are relevant to the given topics."""
    relevant_sentences = []
    for chunk in text_chunks:
        sentences = chunk.split(".")
        for sentence in sentences:
            sentence = sentence.strip()
            if any(topic.lower() in sentence.lower() for topic in topics):
                relevant_sentences.append(sentence)
    return relevant_sentences

TEMPLATE = """
{
  "questions": [
    {
      "id": 1,
      "question": "What is the purpose of assembler directives?",
      "options": [
        "A. To define segments and allocate space for variables",
        "B. To represent specific machine instructions",
        "C. To simplify the programmer's task",
        "D. To provide information to the assembler"
      ],
      "correct_answer": "D. To provide information to the assembler"
    },
    {
      "id": 2,
      "question": "What are opcodes?",
      "options": [
        "A. Instructions for integer addition and subtraction",
        "B. Instructions for memory access",
        "C. Instructions for directing the assembler",
        "D. Mnemonic codes representing specific machine instructions"
      ],
      "correct_answer": "D. Mnemonic codes representing specific machine instructions"
    }
  ]
}
"""
def get_questions(text, num_questions=30):
    prompt = f"""
    Act as a teacher and create {num_questions} multiple-choice questions (MCQs) based on the text delimited by four backticks.
    The response must be formatted in JSON. Each question contains id, question, options as a list, and correct_answer.
    This is an example of the response: {TEMPLATE}
    The text is: ````{text}````
    """
    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        # Parse the JSON response
        return json.loads(response.text)
    except Exception as e:
        st.error(f"Error generating questions: {e}")
        return {"questions": []}

# Display questions function
def display_questions(questions):
    # Display questions
    for question in questions:
        # Convert question id to string
        question_id = str(question["id"])
        st.write(
            f"## Q{question_id}: {question['question']}",
        )
        # Display options as bullet points
        options_text = ""
        options = question["options"]
        for option in options:
            options_text += f"- {option}\n"
        st.write(options_text)
        # Display answer in expander
        with st.expander("Show answer", expanded=False):
            st.write(question["correct_answer"])
        st.divider()
    st.subheader("End of questions")

# Generate a visual summary dynamically (continued)
def generate_visual_summary(text_chunks):
    combined_text = " ".join(text_chunks)
    word_count = Counter(combined_text.split())
    stopwords = set(["the", "and", "of", "to", "in", "a", "for", "is", "on", "with", "that", "by", "it", "as", "are", "this", "from", "only", "at"])
    filtered_word_count = {word: count for word, count in word_count.items() if word.lower() not in stopwords and len(word) > 2}
    wordcloud = WordCloud(width=800, height=400, background_color="white").generate_from_frequencies(filtered_word_count)
    fig1, ax1 = plt.subplots(figsize=(10, 6))
    ax1.imshow(wordcloud, interpolation="bilinear")
    ax1.axis("off")
    ax1.set_title("WordCloud of PDF Content", fontsize=18)
    most_common_words = Counter(filtered_word_count).most_common(10)
    words, counts = zip(*most_common_words)
    fig2, ax2 = plt.subplots(figsize=(10, 6))
    sns.barplot(x=list(counts), y=list(words), palette="viridis", ax=ax2)
    ax2.set_title("Top 10 Most Frequent Words", fontsize=18)
    ax2.set_xlabel("Frequency", fontsize=14)
    ax2.set_ylabel("Words", fontsize=14)
    return fig1, fig2

# Paraphrase text using Gemini AI
def paraphrase_text(input_text):
    try:
        paraphrasing_model = ChatGoogleGenerativeAI(
            model="gemini-pro",
            temperature=0.3,
            max_output_tokens=300
        )
        response = paraphrasing_model.predict(text=input_text)
        return response
    except Exception as e:
        print(f"Error during paraphrasing: {e}")
        return None

# Hangman game implementation (continued)
def hangman_game():
    st.markdown("Guess the word letter by letter. You have a limited number of incorrect guesses. Good luck!")
    if "game" not in st.session_state:
        st.session_state.game = HangmanGame(word_dict)
        st.session_state.message = ""
        st.session_state.game_over = False
    game = st.session_state.game
    if not st.session_state.game_over:
        st.write(f"**Hint:** {game.hint}")
        st.write("**Word:** " + " ".join(game.display_current_state()))
        st.write(f"**Incorrect guesses left:** {game.max_incorrect_guesses - game.incorrect_guesses}")
        st.write(f"**Guessed letters:** {', '.join(game.guessed_letters) if game.guessed_letters else 'None'}")
        st.write(st.session_state.message)
        guess = st.text_input("Enter your guess (a single letter):", key="guess_input").lower()
        if st.button("Submit Guess"):
            if len(guess) != 1 or not guess.isalpha():
                st.session_state.message = "⚠ Invalid input. Please enter a single letter."
            elif guess in game.guessed_letters:
                st.session_state.message = f"⚠ You already guessed '{guess}'. Try another letter."
            else:
                if guess in game.word:
                    st.session_state.message = f"✅ Good guess! '{guess}' is in the word."
                    game.guessed_letters.add(guess)
                    if game.is_game_won():
                        st.session_state.message = f"🎉 Congratulations! You guessed the word: {game.word}"
                        st.session_state.game_over = True
                else:
                    game.incorrect_guesses += 1
                    game.guessed_letters.add(guess)
                    st.session_state.message = f"❌ Incorrect guess. '{guess}' is not in the word."
                    if game.is_game_lost():
                        st.session_state.message = f"😢 You lost! The word was: {game.word}"
                        st.session_state.game_over = True
    else:
        st.write(st.session_state.message)
        if st.button("Play Again"):
            st.session_state.game = HangmanGame(word_dict)
            st.session_state.message = ""
            st.session_state.game_over = False

def fetch_book_recommendations(topics):
    """
    Fetch book recommendations dynamically using Google Books API.
    :param topics: List of topics extracted from the PDF content.
    :return: List of recommended books with title, authors, and description.
    """
    try:
        api_key = os.getenv("GOOGLE_BOOKS_API_KEY")  # Load API key from environment
        if not api_key:
            st.error("Google Books API key is missing. Please provide a valid API key.")
            return []
        recommended_books = []
        for topic in topics:
            # Query Google Books API
            url = f"https://www.googleapis.com/books/v1/volumes?q={topic}&maxResults=5&key={api_key}"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                if "items" in data:
                    for item in data["items"]:
                        book_info = item.get("volumeInfo", {})
                        title = book_info.get("title", "No Title")
                        authors = ", ".join(book_info.get("authors", ["Unknown Author"]))
                        description = book_info.get("description", "No description available.")
                        recommended_books.append({
                            "title": title,
                            "authors": authors,
                            "description": description
                        })
                else:
                    st.warning(f"No books found for topic: {topic}")
            else:
                st.error(f"Failed to fetch books for topic: {topic}. Status code: {response.status_code}")
        # Remove duplicate books
        unique_books = []
        seen_titles = set()
        for book in recommended_books:
            if book["title"] not in seen_titles:
                unique_books.append(book)
                seen_titles.add(book["title"])
        return unique_books
    except Exception as e:
        st.error(f"Error fetching book recommendations: {str(e)}")
        return []

def recommend_books(text_chunks):
    """
    Recommend books based on the content of the uploaded PDF.
    :param text_chunks: List of text chunks extracted from the PDF.
    :return: List of recommended books.
    """
    try:
        # Combine all text chunks into a single string
        combined_text = " ".join(text_chunks)
        # Use Gemini AI to extract key topics
        model = genai.GenerativeModel('gemini-pro')
        prompt = """
        Extract the top 3 key topics or themes from the following text. 
        Respond with a comma-separated list of topics.
        Text: {text}
        """
        response = model.generate_content(prompt.format(text=combined_text))
        topics = [topic.strip() for topic in response.text.split(",")]
        # Fetch dynamic book recommendations using Google Books API
        recommended_books = fetch_book_recommendations(topics)
        return recommended_books
    except Exception as e:
        st.error(f"Error recommending books: {str(e)}")
        return []

def fetch_relevant_links(query, num_results=5):
    """
    Fetch relevant links using SerpAPI's search method.
    :param query: The search query.
    :param num_results: Number of results to fetch.
    :return: List of dictionaries containing title, link, and snippet.
    """
    try:
        api_key = os.getenv("SERPAPI_API_KEY")  # Load SerpAPI key from environment
        if not api_key:
            st.error("SerpAPI key is missing. Please provide a valid API key.")
            return []
        params = {
            "engine": "duckduckgo",  # Use DuckDuckGo as the search engine
            "q": query,
            "num": num_results,
            "api_key": api_key
        }
        # Perform the search
        results = search(**params).get("organic_results", [])
        formatted_results = []
        for result in results:
            formatted_results.append({
                "title": result.get("title", "No Title"),
                "link": result.get("link", "#"),
                "snippet": result.get("snippet", "No description available.")
            })
        return formatted_results
    except Exception as e:
        st.error(f"Error fetching search results: {str(e)}")
        return []

# Main function to run the app (continued)
def main():
    st.header("Multi-PDF's 📚 - Chat Agent 🤖 ")
    with st.sidebar:
        st.write("---")
        st.image("img/pdf.jpg")
        st.title("🌐 💬 Select Language")
        language_options = {
            "English": "en",
            "French": "fr",
            "Spanish": "es",
            "Hindi": "hi",
            "Chinese": "zh-cn",
            "Portuguese": "pt",
        }
        selected_language = st.sidebar.selectbox("Select Language", options=list(language_options.keys()))
        selected_language_code = language_options[selected_language]
        if "raw_text" not in st.session_state:
            st.session_state.raw_text = None
        if "text_chunks" not in st.session_state:
            st.session_state.text_chunks = None
        if "quiz_questions" not in st.session_state:
            st.session_state.quiz_questions = None
        st.write("---")
        st.title("📁 PDF File's Section")
        pdf_docs = st.file_uploader("Upload your PDF Files and Click on the Submit & Process Button", accept_multiple_files=True)
        if st.button("Submit & Process"):
            with st.spinner("Processing..."):
                raw_text = get_pdf_text(pdf_docs)
                text_chunks = get_text_chunks(raw_text)
                get_vector_store(text_chunks)
                st.session_state.raw_text = raw_text
                st.session_state.text_chunks = text_chunks
                st.success("Processing complete! You can now interact with the chatbot, generate summaries, or create quiz questions.")
        st.write("---")
        st.title("📊 Visual Summary")
        if st.button("Generate Visual Summary"):
            with st.spinner("Creating Visuals..."):
                if st.session_state.text_chunks:
                    fig1, fig2 = generate_visual_summary(st.session_state.text_chunks)
                    st.pyplot(fig1)  # Display WordCloud
                    st.pyplot(fig2)  # Display Bar Chart
                    st.success("Visual summary generated!")
                else:
                    st.error("Please process PDFs first.")
        st.write("---")
        st.image("img/Robot.jpg")

    st.write("---")
    st.title("🎨 contextGPT")
    user_text = st.text_area("Enter text to get your answer")
    if st.button("generate Response"):
        with st.spinner("Paraphrasing..."):
            paraphrased = paraphrase_text(user_text)
            if paraphrased:
                st.write("**response Text:**")
                st.write(paraphrased)
                st.success("text generated!")
            else:
                st.error("Error during paraphrasing. Please try again.")
    st.write("---")
    st.title("💬 Ask Me a Question")
    user_question = st.text_input(f"Ask a Question ({selected_language})")
    if user_question:
        with st.spinner("Generating answer..."):
            user_input(user_question, selected_language_code)

    # PDF Summarizer Section
    st.write("---")
    st.title("📄 PDF Summarizer")
    summary_type = st.radio(
        "Select Summary Type:",
        options=["Short", "Medium", "Detailed"],
        index=1  # Default to "Medium"
    )
    if st.button("Generate Summary"):
        if st.session_state.text_chunks:
            with st.spinner("Generating summary..."):
                combined_text = " ".join(st.session_state.text_chunks)
                summary = generate_summary_with_gemini(combined_text, summary_type)
                if summary:
                    st.subheader(f'{summary_type} Summary Results:')
                    st.write(summary)
        else:
            st.error("Please process PDFs first.")

    # Quiz Generator Section
    st.write("---")
    st.title("🎯 Quiz Generator")
    number_of_questions = st.slider(
        "Select the number of questions",
        min_value=1,
        max_value=30,
        value=10,  # Default value
        step=1
    )
    if st.button("Generate Questions"):
        if st.session_state.text_chunks:
            with st.spinner("Generating questions..."):
                combined_text = " ".join(st.session_state.text_chunks)
                questions = get_questions(combined_text, number_of_questions)["questions"]
            display_questions(questions)
        else:
            st.error("Please process PDFs first.")

    st.write("---")
    st.title("🎮 Hangman Game")
    hangman_game()

    st.write("---")
    st.title("📊 PDF to Interactive Mindmap Converter")
    if not configure_genai():
        return
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    if uploaded_file is not None:
        with st.spinner("🔄 Processing PDF and generating mindmap..."):
            text = extract_text_from_pdf(uploaded_file)
            if text:
                st.info(f"Successfully extracted {len(text)} characters from PDF")
                markdown_content = create_mindmap_markdown(text)
                if markdown_content:
                    tab1, tab2 = st.tabs(["📊 Mindmap", "📝 Markdown"])
                    with tab1:
                        st.subheader("Interactive Mindmap")
                        html_content = create_markmap_html(markdown_content)
                        components.html(html_content, height=700, scrolling=True)
                    with tab2:
                        st.text_area("Markdown Content", markdown_content, height=400)
                        st.download_button(
                            label="⬇ Download Markdown",
                            data=markdown_content,
                            file_name="mindmap.md",
                            mime="text/markdown"
                        )

    # Book Recommendations Section
    st.write("---")
    st.title("📚 Book Recommendations")
    if st.button("Get Book Recommendations"):
        with st.spinner("Analyzing content and recommending books..."):
            if st.session_state.text_chunks:
                recommended_books = recommend_books(st.session_state.text_chunks)
                if recommended_books:
                    st.write("### Recommended Books:")
                    for book in recommended_books:
                        st.write(f"- **{book['title']}** by {book['authors']}")
                        st.caption(book['description'])
                else:
                    st.error("No book recommendations found based on the content.")
            else:
                st.error("Please process PDF files first before getting book recommendations.")

    # Generate Relevant Links Section
    st.write("---")
    st.title("🔗 Generate Relevant Links")
    if st.button("Generate Links"):
        with st.spinner("Fetching relevant links..."):
            if st.session_state.text_chunks:
                combined_text = " ".join(st.session_state.text_chunks)
                model = genai.GenerativeModel('gemini-pro')
                prompt = """
                Extract the top 3 key topics or themes from the following text.
                Respond with a comma-separated list of topics.
                Text: {text}
                """
                response = model.generate_content(prompt.format(text=combined_text))
                topics = [topic.strip() for topic in response.text.split(",")]
                all_links = []
                for topic in topics:
                    links = fetch_relevant_links(query=topic, num_results=3)
                    all_links.extend(links)
                if all_links:
                    st.write("### Relevant Links:")
                    for link in all_links:
                        st.write(f"- **[{link['title']}]({link['link']})**")
                        st.caption(link['snippet'])
                else:
                    st.error("No relevant links found.")
            else:
                st.error("Please process PDF files first before generating links.")

    # Footer
    st.markdown("""
    Made with ❤ for Learning and Engaging 
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()