import streamlit as st
import os
import requests
import google.generativeai as genai
import time
from utils2 import translate_text  # Import translation function
# Configure Google Gemini AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
# Load custom CSS
def load_css():
    with open("styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
load_css()
# Function to fetch book recommendations from Google Books API
def fetch_book_recommendations(topics):
    api_key = os.getenv("GOOGLE_BOOKS_API_KEY")
    if not api_key:
        st.error(translate_text("❌ Google Books API key is missing!"))
        return []    
    recommended_books = []
    for topic in topics:
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
                    thumbnail = book_info.get("imageLinks", {}).get("thumbnail", "img/books.jpg")
                    buy_link = book_info.get("infoLink", "#")

                    recommended_books.append({
                        "title": title,
                        "authors": authors,
                        "description": description,
                        "thumbnail": thumbnail,
                        "buy_link": buy_link
                    })
        else:
            st.error(translate_text(f"⚠ Failed to fetch books for topic: {topic} (Status code: {response.status_code})"))

    return recommended_books

# Function to extract key topics using AI
def extract_key_topics():
    try:
        time.sleep(1.5)
        model = genai.GenerativeModel('gemini-1.5-pro')
        response = model.generate_content(f"Extract the top 3 key topics or themes from this text: {st.session_state.text_chunks}")
        topics = [topic.strip() for topic in response.text.split(",")]
        return topics
    except Exception as e:
        st.error(translate_text(f"❌ Error extracting topics: {str(e)}"))
        return []

# Main Book Recommendation Page
def recommend_books():
    # **Page Heading**
    st.markdown(f"<h1 style='text-align: center;'>{translate_text('📖 AI-Recommended Books')}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; font-size: 18px;'>{translate_text('🚀 Let AI guide you to the best books for expanding your knowledge!')}</p>", unsafe_allow_html=True)
    st.write("---")

    # **Subheading with Image Side-by-Side**
    col1, col2 = st.columns([3, 1])  # Adjust the ratio (text : image size)
    
    with col1:
        st.markdown(f"### {translate_text('Find Your Next Read with AI-Powered Suggestions')}")
        st.markdown(f"<p style='text-align: center; font-size: 18px;'>{translate_text('Get book suggestions based on the topics found in your PDFs!')}</p>", unsafe_allow_html=True)

    with col2:
        st.image("img/books.jpg", width=250)  # Adjust path & size

    # **Check if PDFs are uploaded**
    if "text_chunks" not in st.session_state or not st.session_state.text_chunks:
        st.warning(translate_text("⚠ Please upload PDFs on the Home page first!"))
        return

    # **Extract topics**
    with st.spinner(translate_text("🔍 Extracting key topics...")):
        topics = extract_key_topics()
    
    if not topics:
        st.error(translate_text("⚠ AI could not determine relevant topics. Try uploading another PDF."))
        return

    st.success(translate_text(f"✅ Key Topics Identified: {', '.join(topics)}"))

    # **Fetch book recommendations**
    with st.spinner(translate_text("📚 Finding the best books for you...")):
        books = fetch_book_recommendations(topics)

    if books:
        st.subheader(translate_text("📚 Recommended Books"))
        cols = st.columns(2)  # Display books in two columns
        
        for i, book in enumerate(books):
            with cols[i % 2]:  # Alternate columns
                st.image(book["thumbnail"], width=120)
                st.markdown(f"### 📖 {translate_text(book['title'])}")
                st.write(f"**{translate_text('Author(s)')}:** {translate_text(book['authors'])}")
                st.write(f"📄 {translate_text(book['description'][:200])}...")  # Show only a snippet
                
                # Purchase links
                col_buy, col_more = st.columns(2)
                with col_buy:
                    st.markdown(f"[🛍️ {translate_text('Buy on Google Books')}]({book['buy_link']})", unsafe_allow_html=True)
                with col_more:
                    st.markdown(f"[🔎 {translate_text('Search on Amazon')}]"
                                f"(https://www.amazon.com/s?k={book['title'].replace(' ', '+')})",
                                unsafe_allow_html=True)

                st.write("---")
    else:
        st.error(translate_text("⚠ No books found based on the extracted topics."))

if __name__ == "__main__":
    recommend_books()
