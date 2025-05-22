import streamlit as st
import os
import requests
import google.generativeai as genai
import time
from utils2 import translate_text  # Import translation function

# 🎨 Load Custom CSS
def load_css():
    with open("styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# 🌍 Configure Gemini AI (for extracting topics)
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# 🔍 Function to Fetch Relevant Links using SerpAPI
def fetch_serpapi_links(query, num_results=5):
    api_key = os.getenv("SERPAPI_API_KEY")
    if not api_key:
        st.error(translate_text("⚠ SerpAPI key is missing!"))
        return []

    url = "https://serpapi.com/search"
    params = {
        "engine": "google",
        "q": query,
        "num": num_results,
        "api_key": api_key
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        results = response.json().get("organic_results", [])
        return results
    else:
        st.error(translate_text(f"⚠ API Error: {response.status_code} - {response.text}"))
        return []

# 📌 Extract Key Topics Using AI
def extract_key_topics():
    try:
        time.sleep(1.5)  # Prevent excessive API calls
        model = genai.GenerativeModel('gemini-1.5-pro')
        response = model.generate_content(f"Extract the top 3 key topics from this text: {st.session_state.text_chunks}")
        topics = [topic.strip() for topic in response.text.split(",")]
        return topics
    except Exception as e:
        st.error(translate_text(f"❌ Error extracting topics: {str(e)}"))
        return []

# 🔗 Main Function for Relevant Google Search Links
def relevant_links():
    st.markdown(f"<h1 style='text-align: center;'>{translate_text('🔗 AI-Powered Google Search Links')}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; font-size: 18px;'>{translate_text('Find useful search results based on your PDFs!')}</p>", unsafe_allow_html=True)
    st.write("---")

    # 📂 Check if PDFs are uploaded
    if "text_chunks" not in st.session_state or not st.session_state.text_chunks:
        st.warning(translate_text("⚠ Please upload PDFs on the Home page first!"))
        return

    # 🖼 Two-column layout: Explanation + Image
    col1, col2 = st.columns([3, 1])

    with col1:
        st.markdown(f"### {translate_text('🔍 How This Works')}")
        st.markdown(f"""
        - 📌 **{translate_text('AI extracts key topics from your PDFs')}**  
        - 🔗 **{translate_text('Finds the most relevant Google search results')}**  
        - 🌎 **{translate_text('Provides clickable links & summaries')}**  
        """)

    with col2:
        st.image("img/links.jpg", width=200, caption=translate_text("Google AI Search"))  # Update with your image path

    # ✨ Generate Relevant Links Button
    if st.button(translate_text("🔍 Find Google Search Links")):
        with st.spinner(translate_text("🔍 Extracting topics from PDFs...")):
            topics = extract_key_topics()

        if not topics:
            st.error(translate_text("⚠ AI could not determine relevant topics. Try again with another PDF."))
            return

        st.success(f"✅ {translate_text('Key Topics Identified')}: {', '.join(topics)}")

        with st.spinner(translate_text("🔍 Searching Google...")):
            all_links = []
            for topic in topics:
                links = fetch_serpapi_links(query=topic, num_results=3)
                all_links.extend(links)

        # 📌 Display the Links in Card Format
        if all_links:
            st.success(translate_text("✅ Google Search Results Generated! Explore below:"))
            for link in all_links:
                title = link["title"]
                url = link["link"]
                description = link.get("snippet", translate_text("No description available."))

                st.markdown(
                    f"""
                    <div class="link-card">
                        <a class="link-title" href="{url}" target="_blank">🔗 {translate_text(title)}</a>
                        <p class="link-desc">{translate_text(description)}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.error(translate_text("⚠ No relevant Google links found. Try again with different PDFs."))

if __name__ == "__main__":
    relevant_links()
