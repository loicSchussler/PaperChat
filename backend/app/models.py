from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
from app.database import Base


class Paper(Base):
    """
    Table pour stocker les articles scientifiques
    """
    __tablename__ = "papers"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    authors = Column(ARRAY(String), nullable=True)
    year = Column(Integer, nullable=True, index=True)
    abstract = Column(Text, nullable=True)
    keywords = Column(ARRAY(String), nullable=True)
    pdf_path = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relation avec les chunks
    chunks = relationship("Chunk", back_populates="paper", cascade="all, delete-orphan")


class Chunk(Base):
    """
    Table pour stocker les segments de texte avec leurs embeddings
    """
    __tablename__ = "chunks"

    id = Column(Integer, primary_key=True, index=True)
    paper_id = Column(Integer, ForeignKey("papers.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    section_name = Column(String, nullable=True)
    chunk_index = Column(Integer, nullable=False)
    embedding = Column(Vector(1536), nullable=True)  # OpenAI text-embedding-3-small = 1536 dimensions
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relation avec le paper
    paper = relationship("Paper", back_populates="chunks")


class QueryLog(Base):
    """
    Table pour logger les requêtes et calculer les coûts
    """
    __tablename__ = "query_logs"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=True)
    nb_sources = Column(Integer, default=0)
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
    cost_usd = Column(Float, default=0.0)
    response_time_ms = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
