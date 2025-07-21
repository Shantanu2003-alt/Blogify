import streamlit as st
import json
import os
import difflib
from textblob import TextBlob
import spacy
from fpdf import FPDF

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# File to store blog posts
DATA_FILE = "blogs.json"

# Load existing posts
def load_posts():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []

# Save post to file
def save_post(title, body, sentiment, originality):
    posts = load_posts()
    posts.append({"title": title, "body": body, "sentiment": sentiment, "originality": originality})
    with open(DATA_FILE, "w") as f:
        json.dump(posts, f, indent=2)

# Grammar correction using spaCy
def correct_grammar(text):
    doc = nlp(text)
    corrected = []
    for sent in doc.sents:
        blob = TextBlob(sent.text)
        corrected.append(str(blob.correct()))
    return " ".join(corrected)

# Sentiment analysis
def get_sentiment(text):
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    if polarity > 0.2:
        return "Positive"
    elif polarity < -0.2:
        return "Negative"
    else:
        return "Neutral"

# Advanced plagiarism checker using difflib
def check_plagiarism(new_text, old_posts):
    scores = []
    for post in old_posts:
        score = difflib.SequenceMatcher(None, new_text.lower(), post["body"].lower()).ratio()
        scores.append(score)
    return 1 - max(scores) if scores else 1.0

# Export blog post to PDF
def export_to_pdf(title, content):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, f"Title: {title}\n\n{content}")
    filename = f"{title[:10].replace(' ', '_')}.pdf"
    pdf.output(filename)
    return filename

# Streamlit UI
st.set_page_config(page_title="AI Blog Platform", layout="wide")

st.title("📝 AI Blog Platform with Writing Assistant, Plagiarism Checker & PDF Export")

tabs = st.tabs(["✍️ Write Blog", "📚 My Blogs", "📤 Export PDF"])

with tabs[0]:
    st.header("Compose New Blog")

    title = st.text_input("Blog Title", max_chars=100)
    body = st.text_area("Write your blog here...", height=350)

    if st.button("💡 Suggest Improvements"):
        corrected = correct_grammar(body)
        st.subheader("✍️ Suggested Version:")
        st.info(corrected)

    if st.button("🧠 Analyze & Save Blog"):
        if not title or not body:
            st.warning("Please fill both title and content!")
        else:
            posts = load_posts()
            sentiment = get_sentiment(body)
            originality_score = check_plagiarism(body, posts)
            save_post(title, body, sentiment, originality_score)

            st.success("✅ Blog saved successfully!")
            st.metric("🧠 Sentiment", sentiment)
            st.metric("🔍 Originality Score", f"{originality_score*100:.2f}%")

with tabs[1]:
    st.header("📚 Your Saved Blogs")
    posts = load_posts()
    if not posts:
        st.info("No blogs yet. Start writing!")
    else:
        for idx, post in enumerate(posts[::-1]):
            with st.expander(f"📄 {post['title']}"):
                st.markdown(post["body"])
                st.caption(f"🧠 Sentiment: {post['sentiment']} | 🔍 Originality: {post['originality']*100:.2f}%")

with tabs[2]:
    st.header("📤 Export Blog Post to PDF")

    titles = [post["title"] for post in load_posts()]
    if not titles:
        st.info("No saved blogs to export.")
    else:
        selected = st.selectbox("Select blog to export:", titles)
        post = next(p for p in load_posts() if p["title"] == selected)
        if st.button("📥 Export to PDF"):
            filename = export_to_pdf(post["title"], post["body"])
            with open(filename, "rb") as f:
                st.download_button("📥 Download PDF", f, file_name=filename)

