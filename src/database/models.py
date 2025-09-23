# database/models.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

Base = declarative_base()


class User(Base):
    """User statistics and info."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    username = Column(String(255), nullable=True)
    total_messages = Column(Integer, default=0)
    random_facts_requested = Column(Integer, default=0)
    gpt_queries = Column(Integer, default=0)
    personality_chats = Column(Integer, default=0)
    quizzes_completed = Column(Integer, default=0)
    translations_made = Column(Integer, default=0)
    image_descriptions_generated = Column(Integer, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_activity = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    conversations = relationship("Conversation", back_populates="user")
    quiz_results = relationship("QuizResult", back_populates="user")


class Conversation(Base):
    """Conversation messages history."""

    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    conversation_type = Column(String(100), nullable=False)
    persona = Column(String(100), nullable=True)

    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="conversations")


class QuizResult(Base):
    """Quiz results and statistics."""

    __tablename__ = "quiz_results"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    topic = Column(String(100), nullable=False)
    correct_answers = Column(Integer, nullable=False)
    total_questions = Column(Integer, nullable=False)
    score_percentage = Column(Float, nullable=False)

    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="quiz_results")


class TranslationHistory(Base):
    """Translation requests history."""

    __tablename__ = "translation_history"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    original_text = Column(Text, nullable=False)
    translated_text = Column(Text, nullable=False)
    source_language = Column(String(10), nullable=True)
    target_language = Column(String(10), nullable=False)

    timestamp = Column(DateTime(timezone=True), server_default=func.now())


class VocabularyWord(Base):
    """Vocabulary trainer words."""

    __tablename__ = "vocabulary_words"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    word = Column(String(255), nullable=False)
    translation = Column(String(255), nullable=False)
    language = Column(String(10), nullable=False)
    times_practiced = Column(Integer, default=0)
    times_correct = Column(Integer, default=0)

    learned_at = Column(DateTime(timezone=True), server_default=func.now())
    last_practiced = Column(DateTime(timezone=True), nullable=True)
