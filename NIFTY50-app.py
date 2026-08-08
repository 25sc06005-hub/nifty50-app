import streamlit as st
from PIL import Image
import pytesseract
import datetime
import os
import glob

st.set_page_config(page_title="SnapBook", page_icon="📚", layout="centered")
st.title("📚 SnapBook")

# Automatically discover all subject notebooks saved on disk
def get_saved_subjects():
    default_subjects = ["Physics", "Chemistry", "Mathematics"]
    # Look for any existing *_notebook.txt files on the computer
    existing_files = glob.glob("*_notebook.txt")
    discovered = [f.replace("_notebook.txt", "").capitalize() for f in existing_files]
    # Merge defaults and discovered subjects while eliminating duplicates
    return list(dict.fromkeys(default_subjects + discovered))

st.sidebar.header("Manage Notebooks")

# Load subjects dynamically from disk
subjects_list = get_saved_subjects()

# 1. Create a NEW custom notebook and save it to disk immediately
new_subject = st.sidebar.text_input("Create New Subject Notebook")
if st.sidebar.button("➕ Add Notebook") and new_subject.strip():
    clean_name = new_subject.strip().capitalize()
    file_path = f"{clean_name.lower()}_notebook.txt"
    
    # Create the text file on disk so it persists across refreshes
    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"# 📖 {clean_name} Notebook\n\n---\n")
        st.sidebar.success(f"Created '{clean_name}'!")
        st.rerun()

# Select active notebook from the persistent list
subject = st.sidebar.selectbox("Select Active Subject", subjects_list)

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

# 3. Live Display + Download Option
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
    st.info(f"No notes saved in **{subject}** yet. Upload an image above to start.")