from sentence_transformers import SentenceTransformer
from app.config.settings import Settings, VectorTables
import logging

settings = Settings()

logger = logging.getLogger(__name__)


def get_embedding(text: str) -> list[float]:
    model = SentenceTransformer(
        "sentence-transformers/all-MiniLM-L12-v2",
    )
    embedding = model.encode(text)
    return embedding.tolist()


def chunk_text(text, chunk_size=250, overlap=50) -> list[str]:
    if text == "":
        return [""]
    words = text.strip()
    words = words.split()
    if words == []:
        return [""]
    if len(words) <= chunk_size:
        return [text]

    words = list(filter(lambda c: c != "", words))
    chunks = []

    while len(words) > chunk_size:
        chunks.append(" ".join(words[:chunk_size]))
        words = words[chunk_size - overlap :]
    chunks.append(" ".join(words))  # Join the last words to form the last chunk

    return chunks


def chunk_and_embed_text(text: str, chunk_size=250, overlap=50) -> list[list[float]]:
    chunks = chunk_text(text, chunk_size=chunk_size, overlap=overlap)
    embeddings = [get_embedding(chunk) for chunk in chunks]
    return embeddings

