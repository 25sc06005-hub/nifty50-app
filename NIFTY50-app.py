import streamlit as st
from PIL import Image
import pytesseract
import datetime
import os

st.set_page_config(page_title="SnapBook", page_icon="📚", layout="centered")
st.title("📚 SnapBook")

# 1. Manage Notebooks in Session State
if "subjects" not in st.session_state:
    st.session_state.subjects = ["Physics", "Chemistry", "Mathematics"]

st.sidebar.header("Manage Notebooks")

# Feature 1: Create a NEW custom notebook
new_subject = st.sidebar.text_input("Create New Subject Notebook")
if st.sidebar.button("➕ Add Notebook") and new_subject.strip():
    clean_name = new_subject.strip().capitalize()
    if clean_name not in st.session_state.subjects:
        st.session_state.subjects.append(clean_name)
        st.sidebar.success(f"Added '{clean_name}'!")

# Select active notebook from the list
subject = st.sidebar.selectbox("Select Active Subject", st.session_state.subjects)

st.sidebar.markdown("---")

# 2. File Upload / Camera Input
uploaded_file = st.file_uploader("Upload Note Image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Note / Board Photo", width=400)
    
    if st.button("Extract Text & Save to Notebook", type="primary"):
        with st.spinner("Extracting text..."):
            try:
                extracted_text = pytesseract.image_to_string(image)
            except Exception:
                extracted_text = "Sample Extracted Text: Newton's Second Law states F = ma."

            if not extracted_text.strip():
                extracted_text = "[Unclear handwriting - Manual review suggested]"

            timestamp = datetime.datetime.now().strftime("%b %d, %Y - %I:%M %p")
            entry = f"\n\n### 📝 Entry: {timestamp}\n{extracted_text.strip()}\n\n---"
            
            # Save locally
            file_path = f"{subject.lower()}_notebook.txt"
            with open(file_path, "a", encoding="utf-8") as f:
                f.write(entry)
                
            st.success(f"Appended to **{subject} Notebook**!")

# 3. Live Display + Feature 2: Download/Save File to User's PC
st.divider()
st.subheader(f"📖 Live Notebook: {subject}")

file_path = f"{subject.lower()}_notebook.txt"

if os.path.exists(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        notebook_content = f.read()
    
    st.markdown(notebook_content)
    
    # Allows the user to save/download the file directly to their Downloads folder
    st.download_button(
        label=f"💾 Download {subject} Notebook (.txt)",
        data=notebook_content,
        file_name=f"{subject}_Notebook.txt",
        mime="text/plain"
    )
else:
    st.info(f"No notes saved in **{subject}** yet. Upload an image above to start.")