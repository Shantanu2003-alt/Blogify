import streamlit as st
import json
import os
import difflib
from textblob import TextBlob
import spacy
from fpdf import FPDF
from datetime import datetime

# Load spaCy model for grammar correction
try:
    nlp = spacy.load("en_core_web_sm")
except:
    st.error("SpaCy model 'en_core_web_sm' not found. Please install it using 'python -m spacy download en_core_web_sm'")
    st.stop()

# File to store blog posts
DATA_FILE = "blogs.json"

# Load blog data
def load_blogs():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)

# Save blog data
def save_blogs(blogs):
    with open(DATA_FILE, "w") as f:
        json.dump(blogs, f, indent=2)

# Grammar correction using spaCy
def correct_grammar(text):
    doc = nlp(text)
    corrected = " ".join([token.text for token in doc])
    return corrected

# Sentiment analysis using TextBlob
def analyze_sentiment(text):
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    if polarity > 0.1:
        return "Positive 😊"
    elif polarity < -0.1:
        return "Negative 😠"
    else:
        return "Neutral 😐"

# Check plagiarism with existing posts
def check_plagiarism(text, blogs):
    matched_titles = []
    for blog in blogs:
        ratio = difflib.SequenceMatcher(None, text.lower(), blog['body'].lower()).ratio()
        if ratio > 0.6:
            matched_titles.append((blog['title'], round(ratio * 100, 2)))
    return matched_titles

# Export to PDF
def export_to_pdf(title, body):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=14)
    pdf.multi_cell(190, 10, f"Title: {title}\n\n{body}")
    filename = f"{title.replace(' ', '_')}.pdf"
    pdf.output(filename)
    return filename

# Main Streamlit App
def main():
    st.set_page_config(page_title="📝 Blogify", layout="wide")
    st.title("📝 Blogify – AI-Enhanced Blogging Platform")

    tabs = st.tabs(["✍️ Write Blog", "📚 View Blogs", "📊 Analytics"])

    # --- Tab 1: Write Blog ---
    with tabs[0]:
        st.header("✍️ Compose a New Blog")
        title = st.text_input("Blog Title")
        body = st.text_area("Write your blog content here...", height=300)

        if st.button("🧠 Grammar Correct"):
            corrected = correct_grammar(body)
            st.text_area("Corrected Text", corrected, height=300)

        if st.button("🔍 Analyze Sentiment"):
            sentiment = analyze_sentiment(body)
            st.success(f"Sentiment: {sentiment}")

        blogs = load_blogs()
        if st.button("📎 Check Plagiarism"):
            matches = check_plagiarism(body, blogs)
            if matches:
                st.warning("⚠️ Potential plagiarism detected in:")
                for match in matches:
                    st.write(f"- '{match[0]}' ({match[1]}% similarity)")
            else:
                st.success("✅ No significant plagiarism found!")

        if st.button("💾 Save Blog"):
            if title and body:
                blogs.append({"title": title, "body": body, "timestamp": str(datetime.now())})
                save_blogs(blogs)
                st.success("✅ Blog saved successfully!")
            else:
                st.error("❗ Both title and body are required.")

        if st.button("📤 Export to PDF"):
            if title and body:
                filename = export_to_pdf(title, body)
                st.success(f"✅ Exported to {filename}")
                with open(filename, "rb") as f:
                    st.download_button("⬇️ Download PDF", f, file_name=filename)
            else:
                st.error("❗ Provide title and content before exporting.")

    # --- Tab 2: View Blogs ---
    with tabs[1]:
        st.header("📚 Published Blogs")
        blogs = load_blogs()
        if blogs:
            for blog in reversed(blogs):
                st.subheader(blog["title"])
                st.caption(f"🕒 {blog['timestamp']}")
                st.write(blog["body"])
                st.markdown("---")
        else:
            st.info("No blogs published yet.")

    # --- Tab 3: Analytics ---
    with tabs[2]:
        st.header("📊 Blog Insights")
        blogs = load_blogs()
        st.metric("Total Blogs", len(blogs))
        sentiments = [analyze_sentiment(blog["body"]) for blog in blogs]
        st.write("Sentiment Distribution:")
        st.bar_chart({
            "Positive": sentiments.count("Positive 😊"),
            "Neutral": sentiments.count("Neutral 😐"),
            "Negative": sentiments.count("Negative 😠")
        })

if __name__ == "__main__":
    main()
