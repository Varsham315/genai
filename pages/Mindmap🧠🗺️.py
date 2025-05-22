import streamlit as st
import google.generativeai as genai
import streamlit.components.v1 as components
import os
import time
from utils2 import translate_text  # Import translation function

# Configure Gemini AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Load Custom CSS
def load_css():
    with open("styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# Generate mindmap markdown using Gemini AI
def create_mindmap_markdown(text):
    """Generate mindmap markdown using Gemini AI."""
    try:
        time.sleep(1.5)  # Prevent excessive API calls
        model = genai.GenerativeModel('gemini-1.5-pro')
        max_chars = 30000
        if len(text) > max_chars:
            text = text[:max_chars] + "..."
            st.warning(translate_text(f"⚠ Text truncated to {max_chars} characters due to length limitations."))
        
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
        - Key point 1
        - Key point 2
        ### Detail 2
        ## Subtopic 2
        ### Detail 3
        ### Detail 4
        Text to analyze: {text}
        Respond only with the markdown mindmap, no additional text.
        """

        response = model.generate_content(prompt.format(text=text))
        
        if not response.text or not response.text.strip():
            st.error(translate_text("⚠ Received empty response from Gemini AI"))
            return None
        
        return response.text.strip()
    except Exception as e:
        st.error(translate_text(f"❌ Error generating mindmap: {str(e)}"))
        return None

# Generate interactive Markmap HTML
def create_markmap_html(markdown_content):
    """Create HTML with enhanced Markmap visualization."""
    markdown_content = markdown_content.replace('`', '\\`').replace('${', '\\${}')
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="UTF-8">
    <style>
    #mindmap {{
        background-color: white;
        color: black;
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
                maxWidth: 600,
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
            document.body.innerHTML = '<p style="color: red;">⚠ Error rendering mindmap. Please check the console for details.</p>';
        }}
    }};
    </script>
    </body>
    </html>
    """
    return html_content

# **Main Function to Generate Mind Map**
def mindmap():
    st.markdown(f"<h1 style='text-align: center;'>{translate_text('🧠 AI-Powered Mind Map')}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; font-size: 18px;'>{translate_text('Visualize your document’s structure and relationships instantly!')}</p>", unsafe_allow_html=True)
    st.write("---")

    # Check if PDFs are uploaded
    if "text_chunks" not in st.session_state or not st.session_state.text_chunks:
        st.warning(translate_text("⚠ Please upload PDFs on the Home page first!"))
        return

    # **"How This Works" Section with Image Beside It**
    col1, col2 = st.columns([3, 1])  # Adjust column width ratio

    with col1:
        st.markdown(f"### {translate_text('🔍 How This Works')}")
        st.markdown(f"""
        - 📌 **{translate_text('AI analyzes your PDFs')}** {translate_text('to extract key topics and structure')}  
        - 🧠 **{translate_text('Generates an interactive mind map')}** {translate_text('for easy visualization')}  
        - 🔗 **{translate_text('Shows connections between concepts')}** {translate_text('for better understanding')}  
        """)
    
    with col2:
        st.image("/Users/varshininaravula/Downloads/Multi-PDFs_ChatApp_AI-Agent-main/img/mindmap.webp", width=200, caption=translate_text("AI-Generated Mind Map"))  # Adjust path & size

    # **Button to Generate Mind Map**
    if st.button(translate_text("✨ Generate Mind Map")):
        with st.spinner(translate_text("🧠 Thinking... Generating Mind Map...")):
            markdown_content = create_mindmap_markdown(" ".join(st.session_state.text_chunks))
            
            if markdown_content:
                html_content = create_markmap_html(markdown_content)
                st.success(translate_text("✅ Mind map generated successfully!"))
                components.html(html_content, height=600)
            else:
                st.error(translate_text("❌ Mind map generation failed. Try again."))

# **Run the App**
if __name__ == "__main__":
    mindmap()
