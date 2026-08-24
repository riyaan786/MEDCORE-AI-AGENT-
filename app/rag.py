from pathlib import Path
import re


KNOWLEDGE_DIR = (
    Path(__file__).parent.parent
    / "data"
    / "hospital_knowledge"
)


def load_documents():

    documents = []

    for file_path in KNOWLEDGE_DIR.glob("*.md"):

        text = file_path.read_text(
            encoding="utf-8"
        )

        documents.append({
            "source": file_path.name,
            "text": text,
        })

    return documents


def tokenize(text):

    return set(
        re.findall(
            r"\b[a-zA-Z0-9]+\b",
            text.lower(),
        )
    )


def retrieve(query, top_k=3):

    documents = load_documents()

    query_words = tokenize(query)

    scored_documents = []

    for document in documents:

        document_words = tokenize(
            document["text"]
        )

        score = len(
            query_words.intersection(
                document_words
            )
        )

        scored_documents.append(
            (
                score,
                document,
            )
        )

    scored_documents.sort(
        key=lambda item: item[0],
        reverse=True,
    )

    results = []

    for score, document in scored_documents[:top_k]:

        if score > 0:

            results.append({
                "source": document["source"],
                "text": document["text"],
                "score": score,
            })

    return results