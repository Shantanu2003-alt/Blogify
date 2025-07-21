import streamlit as st
from textblob import TextBlob
import language_tool_python
from fpdf import FPDF
from fuzzywuzzy import fuzz
import os

POSTS_FOLDER = "posts"
os.makedirs(POSTS_FOLDER, exist_ok=True)

tool = language_tool_python.LanguageTool('en-US')

def correct_grammar(text):
    matches = tool.check(text)
    corrected = language_tool_python.utils.correct(text, matches)
    return corrected

def analyze_sentiment(text):
    blob = TextBlob(text)
    return blob.sentiment.polarity, blob.sentiment.subjectivity

def check_plagiarism(content):
    plagiarism_scores = []
    for filename in os.listdir(POSTS_FOLDER):
        with open(os.path.join(POSTS_FOLDER, filename), "r", encoding="utf-8") as f:
            existing = f.read()
            score = fuzz.token_set_ratio(content, existing)
            plagiarism_scores.append(score)
    return max(plagiarism_scores) if plagiarism_scores else 0

def save_post(title, content):
    safe_title = title.replace(" ", "_") + ".txt"
    with open(os.path.join(POSTS_FOLDER, safe_title), "w", encoding="utf-8") as f:
        f.write(content)

def export_to_pdf(title, content):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, f"Title: {title}\n\n{content}")
    pdf.output(os.path.join(POSTS_FOLDER, title.replace(" ", "_") + ".pdf"))

# Streamlit App UI
st.set_page_config(page_title="AI Blog Writer", layout="wide")

st.title("📝 AI Blog Platform with Local NLP")

tab1, tab2 = st.tabs(["🖊️ Write Blog", "📚 View Published"])

with tab1:
    st.subheader("Create your blog post")
    title = st.text_input("Enter blog title")
    content = st.text_area("Write your blog content here", height=300)

    col1, col2, col3 = st.columns(3)

    if col1.button("✍️ Grammar Correction"):
        corrected = correct_grammar(content)
        st.text_area("Corrected Text", corrected, height=300)

    if col2.button("🧠 Sentiment Analysis"):
        polarity, subjectivity = analyze_sentiment(content)
        st.success(f"Polarity: {polarity:.2f} | Subjectivity: {subjectivity:.2f}")

    if col3.button("🔎 Check Plagiarism"):
        score = check_plagiarism(content)
        if score > 70:
            st.error(f"⚠️ High similarity detected! ({score}%)")
        else:
            st.success(f"✅ Low similarity. ({score}%)")

    if st.button("📥 Save & Export"):
        if title and content:
            save_post(title, content)
            export_to_pdf(title, content)
            st.success("Blog saved and exported to PDF!")
        else:
            st.warning("Please enter both title and content.")

with tab2:
    st.subheader("Published Blog Posts")
    files = [f for f in os.listdir(POSTS_FOLDER) if f.endswith(".txt")]
    for f in files:
        with open(os.path.join(POSTS_FOLDER, f), "r", encoding="utf-8") as file:
            st.markdown(f"### {f[:-4].replace('_', ' ')}")
            st.code(file.read())
