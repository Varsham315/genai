import streamlit as st
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from collections import Counter
import seaborn as sns
from utils2 import translate_text  # Import translation function

def load_css():
    with open("styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# **Function to generate WordCloud and bar chart from text data**
def generate_visual_summary(text_chunks):
    combined_text = " ".join(text_chunks)
    word_count = Counter(combined_text.split())

    # Remove common stopwords
    stopwords = set(["the", "and", "of", "to", "in", "a", "for", "is", "on", "with", "that", "by", "it", "as", "are","from","user","users","cloud","use","also","using","into","Like"])
    filtered_word_count = {word: count for word, count in word_count.items() if word.lower() not in stopwords and len(word) > 2}

    if not filtered_word_count:
        return None, None

    # **Create WordCloud**
    wordcloud = WordCloud(width=800, height=400, background_color="white").generate_from_frequencies(filtered_word_count)
    fig1, ax1 = plt.subplots(figsize=(10, 6))
    ax1.imshow(wordcloud, interpolation="bilinear")
    ax1.axis("off")
    ax1.set_title(translate_text("📌 WordCloud of PDF Content"), fontsize=18, color="#4CAF50")

    # **Create Bar Chart for the most common words**
    most_common_words = Counter(filtered_word_count).most_common(10)
    if most_common_words:
        words, counts = zip(*most_common_words)
        fig2, ax2 = plt.subplots(figsize=(10, 6))
        sns.barplot(x=list(counts), y=list(words), palette="mako", ax=ax2)
        ax2.set_title(translate_text("📊 Top 10 Most Frequent Words"), fontsize=18, color="#4CAF50")
        ax2.set_xlabel(translate_text("Frequency"), fontsize=14, color="#333")
        ax2.set_ylabel(translate_text("Words"), fontsize=14, color="#333")
        ax2.grid(axis="x", linestyle="--", alpha=0.7)
    else:
        fig2 = None

    return fig1, fig2

# **Streamlit Page**
def visual():
    # **Page Title & Description**
    st.markdown(f"<h1 style='text-align: center;'>{translate_text('📊 Visual Summary of PDFs')}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; font-size: 18px;'>{translate_text('Gain insights into your PDF content with AI-powered visualizations!')}</p>", unsafe_allow_html=True)
    st.write("---")

    # **Check if PDFs are uploaded**
    if "text_chunks" not in st.session_state or not st.session_state.text_chunks:
        st.warning(translate_text("⚠ Please upload PDFs on the Home page first!"))
        return

    # **Two-column layout: Explanation + Image**
    col1, col2 = st.columns([3, 1])  # Left (text), Right (image)

    with col1:
        st.markdown(f"### {translate_text('🔍 How This Works')}")
        st.write(f"""
        - 📌 **{translate_text('WordCloud')}** → {translate_text('Highlights the most common words in your document')}  
        - 📊 **{translate_text('Top 10 Word Frequency')}** → {translate_text('Shows the most frequently occurring words')}  
        - 📈 **{translate_text('Understand PDF Trends')}** → {translate_text('Quickly grasp the key topics in your document')}  
        """)

    with col2:
        st.image("img/wordcloud.jpg", width=200, caption=translate_text("AI-Generated Insights"))  # Update with your image path

    # **Button to Generate Visuals**
    if st.button(translate_text("✨ Generate Visual Summary")):
        with st.spinner(translate_text("🔍 Analyzing text and generating visuals...")):
            fig1, fig2 = generate_visual_summary(st.session_state.text_chunks)

        if fig1:
            st.success(translate_text("✅ Visual Summary Generated!"))
            st.pyplot(fig1)  # Display WordCloud
            if fig2:
                st.pyplot(fig2)  # Display Bar Chart
            else:
                st.warning(translate_text("⚠ Not enough data to generate a bar chart."))
        else:
            st.error(translate_text("❌ Could not generate visualizations. Text data may be insufficient."))

# **Run the App**
if __name__ == "__main__":
    visual()
