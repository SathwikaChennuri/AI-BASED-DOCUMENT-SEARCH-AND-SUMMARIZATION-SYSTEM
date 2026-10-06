import streamlit as st
import re
from collections import Counter

from pypdf import PdfReader
from docx import Document


# =====================================================
# PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="AI Document Search & Summarization",
    page_icon="📄",
    layout="wide"
)

st.title("📄 AI-Based Document Search & Summarization System")

st.write(
    "Upload documents, search important information, "
    "and generate a concise summary."
)


# =====================================================
# TEXT EXTRACTION
# =====================================================

def extract_text(file):

    filename = file.name.lower()

    # PDF
    if filename.endswith(".pdf"):

        reader = PdfReader(file)

        text = ""

        for page in reader.pages:

            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

        return text

    # DOCX
    elif filename.endswith(".docx"):

        document = Document(file)

        text = ""

        for paragraph in document.paragraphs:

            text += paragraph.text + "\n"

        return text

    # TXT
    elif filename.endswith(".txt"):

        return file.read().decode(
            "utf-8",
            errors="ignore"
        )

    return ""


# =====================================================
# TEXT CLEANING
# =====================================================

def clean_text(text):

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# =====================================================
# SPLIT INTO SENTENCES
# =====================================================

def split_sentences(text):

    sentences = re.split(
        r"(?<=[.!?])\s+",
        text
    )

    return [
        sentence.strip()
        for sentence in sentences
        if len(sentence.strip()) > 20
    ]


# =====================================================
# SEARCH ENGINE
# =====================================================

def search_document(text, query):

    sentences = split_sentences(text)

    query_words = set(
        re.findall(
            r"\b[a-zA-Z]{3,}\b",
            query.lower()
        )
    )

    results = []

    for sentence in sentences:

        sentence_words = set(
            re.findall(
                r"\b[a-zA-Z]{3,}\b",
                sentence.lower()
            )
        )

        common_words = (
            query_words & sentence_words
        )

        score = len(common_words)

        if score > 0:

            results.append(
                (score, sentence)
            )

    results.sort(
        key=lambda x: x[0],
        reverse=True
    )

    return [
        sentence
        for score, sentence in results[:10]
    ]


# =====================================================
# EXTRACTIVE SUMMARIZATION
# =====================================================

def summarize_text(text, sentence_count=5):

    sentences = split_sentences(text)

    if not sentences:
        return "No readable text was found."

    if len(sentences) <= sentence_count:

        return " ".join(sentences)

    # Remove common words
    stop_words = {
        "the", "is", "a", "an", "and",
        "of", "to", "in", "for", "on",
        "with", "as", "by", "this",
        "that", "are", "was", "were",
        "be", "from", "or", "it",
        "at", "which", "these", "their"
    }

    words = re.findall(
        r"\b[a-zA-Z]{3,}\b",
        text.lower()
    )

    words = [
        word
        for word in words
        if word not in stop_words
    ]

    frequency = Counter(words)

    sentence_scores = []

    for index, sentence in enumerate(sentences):

        sentence_words = re.findall(
            r"\b[a-zA-Z]{3,}\b",
            sentence.lower()
        )

        score = sum(
            frequency[word]
            for word in sentence_words
        )

        sentence_scores.append(
            (score, index, sentence)
        )

    # Select important sentences
    best_sentences = sorted(
        sentence_scores,
        reverse=True
    )[:sentence_count]

    # Keep original document order
    best_sentences.sort(
        key=lambda x: x[1]
    )

    return " ".join(
        sentence
        for score, index, sentence
        in best_sentences
    )


# =====================================================
# FILE UPLOAD
# =====================================================

uploaded_files = st.file_uploader(
    "Upload your documents",
    type=["pdf", "docx", "txt"],
    accept_multiple_files=True
)


# =====================================================
# PROCESS DOCUMENTS
# =====================================================

if uploaded_files:

    all_documents = {}

    for file in uploaded_files:

        try:

            text = extract_text(file)

            text = clean_text(text)

            if text:

                all_documents[file.name] = text

            else:

                st.warning(
                    f"No readable text found in {file.name}"
                )

        except Exception as error:

            st.error(
                f"Error reading {file.name}: {error}"
            )


    if all_documents:

        st.success(
            f"{len(all_documents)} document(s) loaded successfully."
        )


        # =================================================
        # DOCUMENT INFORMATION
        # =================================================

        st.subheader("📚 Uploaded Documents")

        for filename, text in all_documents.items():

            word_count = len(text.split())

            st.write(
                f"📄 **{filename}** — "
                f"{word_count} words"
            )


        # =================================================
        # SEARCH
        # =================================================

        st.divider()

        st.subheader("🔎 Search Documents")

        query = st.text_input(
            "Enter your question or keyword",
            placeholder="Example: What are the advantages of cloud computing?"
        )


        if st.button("🔍 Search"):

            if not query.strip():

                st.warning(
                    "Please enter a search query."
                )

            else:

                found = False

                for filename, text in all_documents.items():

                    results = search_document(
                        text,
                        query
                    )

                    if results:

                        found = True

                        st.markdown(
                            f"### 📄 {filename}"
                        )

                        for number, result in enumerate(
                            results,
                            start=1
                        ):

                            st.info(
                                f"**Result {number}:**\n\n"
                                f"{result}"
                            )


                if not found:

                    st.warning(
                        "No relevant information found."
                    )


        # =================================================
        # SUMMARIZATION
        # =================================================

        st.divider()

        st.subheader("📝 Document Summarization")


        selected_document = st.selectbox(
            "Select a document to summarize",
            list(all_documents.keys())
        )


        summary_length = st.slider(
            "Number of important sentences",
            min_value=3,
            max_value=10,
            value=5
        )


        if st.button("✨ Generate Summary"):

            document_text = all_documents[
                selected_document
            ]

            with st.spinner(
                "Generating summary..."
            ):

                summary = summarize_text(
                    document_text,
                    summary_length
                )

            st.success("Summary generated!")

            st.markdown("### 📌 Summary")

            st.write(summary)


else:

    st.info(
        "👆 Upload a PDF, DOCX, or TXT document to get started."
    )


# =====================================================
# FOOTER
# =====================================================

st.divider()

st.caption(
    "AI-Based Document Search & Summarization System"
)