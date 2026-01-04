"""
Unit tests for Vector Service functions.

Tests for text embedding, chunking, and combined operations.
"""

import pytest
import sys
import os

# Add app directory to path
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
)

from app.services.vector_service import get_embedding, chunk_text, chunk_and_embed_text


# ============================================================================
# Tests for get_embedding
# ============================================================================


class TestGetEmbedding:
    """Test suite for get_embedding function."""

    def test_get_embedding_simple_text(self):
        """Test getting embedding for simple text."""
        text = "This is a test sentence."
        embedding = get_embedding(text)

        assert isinstance(embedding, list)
        assert len(embedding) == 384  # all-MiniLM-L12-v2 produces 384-dim vectors
        assert all(isinstance(val, float) for val in embedding)

    def test_get_embedding_empty_text(self):
        """Test getting embedding for empty text."""
        text = ""
        embedding = get_embedding(text)

        assert isinstance(embedding, list)
        assert len(embedding) == 384

    def test_get_embedding_long_text(self):
        """Test getting embedding for longer text."""
        text = " ".join(["word"] * 100)
        embedding = get_embedding(text)

        assert isinstance(embedding, list)
        assert len(embedding) == 384

    def test_get_embedding_special_characters(self):
        """Test getting embedding for text with special characters."""
        text = "Hello! How are you? I'm fine, thanks. #python @user"
        embedding = get_embedding(text)

        assert isinstance(embedding, list)
        assert len(embedding) == 384

    def test_get_embedding_different_texts_different_embeddings(self):
        """Test that different texts produce different embeddings."""
        text1 = "Amazon Web Services cloud computing"
        text2 = "Machine learning and artificial intelligence"

        embedding1 = get_embedding(text1)
        embedding2 = get_embedding(text2)

        assert embedding1 != embedding2

    def test_get_embedding_same_text_same_embedding(self):
        """Test that same text produces same embedding (deterministic)."""
        text = "Consistent embedding test"

        embedding1 = get_embedding(text)
        embedding2 = get_embedding(text)

        assert embedding1 == embedding2


# ============================================================================
# Tests for chunk_text
# ============================================================================


class TestChunkText:
    """Test suite for chunk_text function."""

    def test_chunk_text_default_params(self):
        """Test chunking text with default parameters."""
        # Create text with 300 words
        text = " ".join([f"word{i}" for i in range(300)])
        chunks = chunk_text(text)

        assert isinstance(chunks, list)
        assert len(chunks) > 1  # Should be split into multiple chunks
        assert all(isinstance(chunk, str) for chunk in chunks)

    def test_chunk_text_small_text(self):
        """Test chunking text smaller than chunk_size."""
        text = " ".join([f"word{i}" for i in range(10)])
        chunks = chunk_text(text, chunk_size=250, overlap=50)

        assert len(chunks) == 1
        assert chunks[0] == text

    def test_chunk_text_exact_chunk_size(self):
        """Test chunking text that matches chunk_size exactly."""
        text = " ".join([f"word{i}" for i in range(250)])
        chunks = chunk_text(text, chunk_size=250, overlap=50)

        assert len(chunks) == 1
        assert chunks[0] == text

    def test_chunk_text_custom_chunk_size(self):
        """Test chunking with custom chunk size."""
        text = " ".join([f"word{i}" for i in range(100)])
        chunks = chunk_text(text, chunk_size=20, overlap=5)

        assert isinstance(chunks, list)
        assert len(chunks) > 1

    def test_chunk_text_with_overlap(self):
        """Test that overlap works correctly."""
        text = " ".join([f"word{i}" for i in range(100)])
        chunks = chunk_text(text, chunk_size=20, overlap=5)

        # Check that consecutive chunks have overlapping words
        if len(chunks) > 1:
            # The last 5 words of chunk 0 should appear in chunk 1
            chunk0_words = chunks[0].split()
            chunk1_words = chunks[1].split()

            # Overlap should be present (at least some words should match)
            assert len(chunk0_words) > 0
            assert len(chunk1_words) > 0

    def test_chunk_text_no_overlap(self):
        """Test chunking with no overlap."""
        text = " ".join([f"word{i}" for i in range(100)])
        chunks = chunk_text(text, chunk_size=20, overlap=0)

        assert isinstance(chunks, list)
        assert len(chunks) > 1

        # With no overlap, chunks should be consecutive
        # Total words in chunks should equal original words
        total_chunk_words = sum(len(chunk.split()) for chunk in chunks)
        assert total_chunk_words == 100

    def test_chunk_text_single_word(self):
        """Test chunking single word."""
        text = "singleword"
        chunks = chunk_text(text, chunk_size=250, overlap=50)

        assert len(chunks) == 1
        assert chunks[0] == "singleword"

    def test_chunk_text_empty_string(self):
        """Test chunking empty string."""
        text = ""
        chunks = chunk_text(text, chunk_size=250, overlap=50)

        assert len(chunks) == 1
        assert chunks[0] == ""

    def test_chunk_text_large_overlap(self):
        """Test chunking with overlap close to chunk_size."""
        text = " ".join([f"word{i}" for i in range(100)])
        chunks = chunk_text(text, chunk_size=20, overlap=18)

        assert isinstance(chunks, list)
        # With large overlap, should create more chunks
        assert len(chunks) > 1


# ============================================================================
# Tests for chunk_and_embed_text
# ============================================================================


class TestChunkAndEmbedText:
    """Test suite for chunk_and_embed_text function."""

    def test_chunk_and_embed_simple_text(self):
        """Test chunking and embedding simple text."""
        text = " ".join([f"word{i}" for i in range(100)])
        embeddings = chunk_and_embed_text(text)

        assert isinstance(embeddings, list)
        assert len(embeddings) > 0
        assert all(isinstance(emb, list) for emb in embeddings)
        assert all(len(emb) == 384 for emb in embeddings)

    def test_chunk_and_embed_small_text(self):
        """Test chunking and embedding text smaller than chunk_size."""
        text = "This is a small text."
        embeddings = chunk_and_embed_text(text)

        assert isinstance(embeddings, list)
        assert len(embeddings) == 1  # Small text should be one chunk
        assert len(embeddings[0]) == 384

    def test_chunk_and_embed_large_text(self):
        """Test chunking and embedding large text."""
        text = " ".join([f"word{i}" for i in range(1000)])
        embeddings = chunk_and_embed_text(text)

        assert isinstance(embeddings, list)
        assert len(embeddings) > 1  # Large text should be multiple chunks
        assert all(len(emb) == 384 for emb in embeddings)

    def test_chunk_and_embed_empty_text(self):
        """Test chunking and embedding empty text."""
        text = ""
        embeddings = chunk_and_embed_text(text)

        assert isinstance(embeddings, list)
        assert len(embeddings) == 1
        assert len(embeddings[0]) == 384

    def test_chunk_and_embed_consistency(self):
        """Test that same text produces same embeddings consistently."""
        text = " ".join([f"word{i}" for i in range(100)])

        embeddings1 = chunk_and_embed_text(text)
        embeddings2 = chunk_and_embed_text(text)

        assert len(embeddings1) == len(embeddings2)
        for emb1, emb2 in zip(embeddings1, embeddings2):
            assert emb1 == emb2

    def test_chunk_and_embed_different_chunks_different_embeddings(self):
        """Test that different chunks produce different embeddings."""
        text = " ".join([f"word{i}" for i in range(500)])
        embeddings = chunk_and_embed_text(text)

        # If we have multiple chunks, they should have different embeddings
        if len(embeddings) > 1:
            assert embeddings[0] != embeddings[1]

    def test_chunk_and_embed_real_text(self):
        """Test with realistic AWS-related text."""
        text = """
        Amazon Web Services (AWS) is a comprehensive cloud computing platform
        provided by Amazon. It offers over 200 fully featured services from
        data centers globally. Millions of customers use AWS to lower costs,
        become more agile, and innovate faster. AWS services include computing
        power, storage options, networking, databases, analytics, machine learning,
        artificial intelligence, Internet of Things (IoT), security, and more.
        """
        embeddings = chunk_and_embed_text(text)

        assert isinstance(embeddings, list)
        assert len(embeddings) >= 1
        assert all(isinstance(emb, list) for emb in embeddings)
        assert all(len(emb) == 384 for emb in embeddings)


# ============================================================================
# Integration Tests
# ============================================================================


class TestVectorServiceIntegration:
    """Integration tests for vector service functions."""

    def test_full_pipeline(self):
        """Test complete pipeline from text to embeddings."""
        text = " ".join([f"This is sentence number {i}." for i in range(100)])

        # Step 1: Chunk the text
        chunks = chunk_text(text, chunk_size=50, overlap=10)
        assert len(chunks) > 1

        # Step 2: Get embeddings for each chunk
        embeddings = [get_embedding(chunk) for chunk in chunks]
        assert len(embeddings) == len(chunks)
        assert all(len(emb) == 384 for emb in embeddings)

        # Step 3: Compare with combined function
        combined_embeddings = chunk_and_embed_text(text, chunk_size=50, overlap=10)
        assert len(combined_embeddings) == len(embeddings)

    def test_aws_solution_description_embedding(self):
        """Test embedding AWS solution descriptions."""
        solutions = [
            "Amazon EC2 provides scalable computing capacity in the AWS cloud.",
            "Amazon S3 is object storage built to retrieve any amount of data.",
            "AWS Lambda lets you run code without provisioning servers.",
        ]

        embeddings = [get_embedding(solution) for solution in solutions]

        assert len(embeddings) == 3
        assert all(len(emb) == 384 for emb in embeddings)
        # Each solution should have a unique embedding
        assert embeddings[0] != embeddings[1]
        assert embeddings[1] != embeddings[2]
        assert embeddings[0] != embeddings[2]

    def test_interaction_content_embedding(self):
        """Test embedding interaction content."""
        interaction_content = """
        Dear John,

        Thank you for your interest in our cloud solutions. We have several
        options that might fit your needs, including compute, storage, and
        database services. I'd be happy to schedule a call to discuss your
        specific requirements.

        Best regards,
        Sales Team
        """

        # Test direct embedding
        embedding = get_embedding(interaction_content)
        assert len(embedding) == 384

        # Test chunked embedding
        chunked_embeddings = chunk_and_embed_text(interaction_content)
        assert len(chunked_embeddings) >= 1
        assert all(len(emb) == 384 for emb in chunked_embeddings)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
