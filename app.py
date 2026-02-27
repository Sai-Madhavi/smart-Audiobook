import streamlit as st
import PyPDF2
import pyttsx3
import json
import os
import time
from docx import Document

# ---------------- CONFIG ----------------
PROGRESS_FILE = "progress.json"
SNOOZE_TIME = 900   # 15 minutes (900 seconds)

# ---------------- LOAD / SAVE ----------------
def save_progress(page):
    with open(PROGRESS_FILE, "w") as f:
        json.dump({"last_page": page}, f)

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, "r") as f:
                data = json.load(f)
                return data.get("last_page", 0)
        except:
            return 0
    return 0

# ---------------- TEXT EXTRACTION ----------------
def extract_pdf(file):
    reader = PyPDF2.PdfReader(file)
    pages = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages.append(text)
    return pages

def extract_docx(file):
    doc = Document(file)
    text = "\n".join([para.text for para in doc.paragraphs])
    return [text]

# ---------------- STREAMLIT UI ----------------
st.title("🎧 Smart AI Audiobook Reader (15 Min Snooze)")

uploaded_file = st.file_uploader(
    "Upload PDF or DOCX file",
    type=["pdf", "docx"]
)

if uploaded_file:

    if uploaded_file.type == "application/pdf":
        pages = extract_pdf(uploaded_file)
    else:
        pages = extract_docx(uploaded_file)

    total_pages = len(pages)
    current_page = load_progress()

    st.success(f"Total Pages: {total_pages}")
    st.info(f"Last Read Page: {current_page + 1}")

    if st.button("▶ Start Reading"):

        engine = pyttsx3.init()
        engine.setProperty('rate', 170)

        start_time = time.time()

        for i in range(current_page, total_pages):

            # Snooze Check
            if time.time() - start_time > SNOOZE_TIME:
                st.warning("⏰ Snooze Activated (15 minutes completed)")
                save_progress(i)
                engine.stop()
                break

            text = pages[i]

            st.write(f"📖 Reading Page {i + 1}")

            engine.say(text)
            engine.runAndWait()

            save_progress(i + 1)

        engine.stop()
        st.success("✅ Reading Session Ended")