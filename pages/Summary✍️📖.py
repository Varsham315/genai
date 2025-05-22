import streamlit as st
import google.generativeai as genai
import os
import base64
import time
from utils2 import translate_text  # Import translation function

# 🌟 Configure Google Gemini AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# 🎨 Load Custom CSS
def load_css():
    with open("styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# **Function to generate summary**
def generate_summary(text, summary_type):
    try:
        time.sleep(1.5)
        model = genai.GenerativeModel('gemini-1.5-pro')
        response = model.generate_content(f"Summarize this text in a {summary_type} format:\n\n{text}")

        if response.text:
            return response.text.strip()
        else:
            return translate_text("⚠ AI could not generate a summary. Try again with different input.")
    except Exception as e:
        return f"❌ {translate_text('Error')}: {str(e)}"

# **Function to create a downloadable summary file**
def create_download_link(summary_text):
    """Creates a download link for the generated summary."""
    summary_bytes = summary_text.encode()
    b64 = base64.b64encode(summary_bytes).decode()
    return f'<a href="data:file/txt;base64,{b64}" download="summary.txt">📥 {translate_text("Download Summary")}</a>'

# **Main Summarizer Page**
def summary():
    st.markdown(f"<h1 style='text-align: center;'>{translate_text('📚 AI-Powered PDF Summarizer')}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; font-size: 18px;'>{translate_text('Get AI-generated summaries of your PDFs in different formats!')}</p>", unsafe_allow_html=True)
    st.write("---")

    # 📂 Check if PDFs are uploaded
    if "text_chunks" not in st.session_state or not st.session_state.text_chunks:
        st.warning(translate_text("⚠ Please upload PDFs on the Home page first!"))
        return

    # **Two-column layout: Selection + Image**
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader(f"📄 {translate_text('Select Summary Type')}:")
        st.write(f"📝 **{translate_text('Customize your summary length based on your needs.')}**")  
        st.write(f"⚡ **{translate_text('Let AI extract the key insights instantly!')}**")
        summary_type = st.radio("", [translate_text("Short"), translate_text("Medium"), translate_text("Detailed")], horizontal=True)

    with col2:
        st.image("img/summary.jpg", width=200, caption=translate_text("AI Summary"))  # Update with your image path

    # ✨ Generate Summary Button
    if st.button(translate_text("📝 Generate Summary")):
        with st.spinner(translate_text("Generating summary... 📖")):
            pdf_text = " ".join(st.session_state.text_chunks)  # Combine all uploaded PDF text
            summary_text = generate_summary(pdf_text, summary_type)

        # 📌 Display Summary in a Styled Box
        st.success(translate_text("✅ AI Summary:"))
        st.markdown(f"<div style='padding:10px; border-radius:8px;'> {summary_text} </div>", unsafe_allow_html=True)

        # 📥 Copy & Download Options
        col_copy, col_download = st.columns([1, 1])
        with col_copy:
            st.text_area(translate_text("📋 Copy Summary:"), summary_text, height=150)

        with col_download:
            st.markdown(create_download_link(summary_text), unsafe_allow_html=True)

if __name__ == "__main__":
    summary()
