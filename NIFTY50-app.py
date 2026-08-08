import streamlit as st
import google.generativeai as genai
from PIL import Image
import datetime
import os
import glob

st.set_page_config(page_title="SnapBook AI", page_icon="📚", layout="centered")
st.title("📚 SnapBook AI")
st.caption("AI-powered classroom note extractor & notebook manager")

# 1. API Key Setup in Sidebar
st.sidebar.header("🔑 AI Engine Setup")
api_key = st.sidebar.text_input("Enter Free Gemini API Key", type="password")
st.sidebar.caption("Get a free key in 30 secs at [aistudio.google.com](https://aistudio.google.com)")

# 2. Manage Notebooks
def get_saved_subjects():
    default_subjects = ["Physics", "Chemistry", "Mathematics"]
    existing_files = glob.glob("*_notebook.txt")
    discovered = [f.replace("_notebook.txt", "").capitalize() for f in existing_files]
    return list(dict.fromkeys(default_subjects + discovered))

st.sidebar.markdown("---")
st.sidebar.header("📁 Notebooks")
subjects_list = get_saved_subjects()

new_subject = st.sidebar.text_input("Create New Subject Notebook")
if st.sidebar.button("➕ Add Notebook") and new_subject.strip():
    clean_name = new_subject.strip().capitalize()
    file_path = f"{clean_name.lower()}_notebook.txt"
    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"# 📖 {clean_name} Notebook\n\n---\n")
        st.sidebar.success(f"Created '{clean_name}'!")
        st.rerun()

subject = st.sidebar.selectbox("Select Active Subject", subjects_list)

# 3. Image Upload & AI Text Extraction
uploaded_file = st.file_uploader("Upload Blackboard / Peer Note Photo", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", width=400)
    
    if st.button("Extract Text with AI & Save", type="primary"):
        if not api_key:
            st.error("Please enter your free Gemini API Key in the sidebar!")
        else:
            with st.spinner("AI is reading handwriting and cleaning up notes..."):
                try:
                    # Configure Gemini AI
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    
                    prompt = (
                        "Extract all written text from this image accurately. "
                        "If it is a blackboard or handwritten note, fix obvious typos, "
                        "format math formulas clearly, and arrange the content into clean paragraphs."
                    )
                    
                    response = model.generate_content([prompt, image])
                    extracted_text = response.text

                except Exception as e:
                    extracted_text = f"Error processing image with AI: {str(e)}"

                # Save to file
                timestamp = datetime.datetime.now().strftime("%b %d, %Y - %I:%M %p")
                entry = f"\n\n### 📝 Entry: {timestamp}\n{extracted_text.strip()}\n\n---"
                
                file_path = f"{subject.lower()}_notebook.txt"
                with open(file_path, "a", encoding="utf-8") as f:
                    f.write(entry)
                    
                st.success(f"AI appended text to **{subject} Notebook**!")

# 4. Live Display & Download
st.divider()
st.subheader(f"📖 Live Notebook: {subject}")

file_path = f"{subject.lower()}_notebook.txt"

if os.path.exists(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        notebook_content = f.read()
    
    st.markdown(notebook_content)
    
    st.download_button(
        label=f"💾 Download {subject} Notebook (.txt)",
        data=notebook_content,
        file_name=f"{subject}_Notebook.txt",
        mime="text/plain"
    )
else:
    st.info(f"No notes saved in **{subject}** yet.")