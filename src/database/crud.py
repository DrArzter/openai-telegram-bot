# database/crud.py
from sqlalchemy.orm import Session
from database.models import (
    User,
    Conversation,
    QuizResult,
    TranslationHistory,
    VocabularyWord,
)
from datetime import datetime
from typing import List, Optional
from utils.logger import get_logger

logger = get_logger(__name__)


def get_or_create_user(db: Session, telegram_id: int, username: str = None) -> User:
    """Get user by telegram_id or create new one."""
    user = db.query(User).filter(User.telegram_id == telegram_id).first()

    if not user:
        user = User(telegram_id=telegram_id, username=username)
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info(f"Created new user: {telegram_id}")
    else:
        if username and user.username != username:
            user.username = username
            db.commit()

    return user


def update_user_stats(
    db: Session, telegram_id: int, stat_field: str, increment: int = 1
) -> bool:
    """Update user statistics."""
    try:
        user = get_or_create_user(db, telegram_id)

        if hasattr(user, stat_field):
            current_value = getattr(user, stat_field, 0)
            setattr(user, stat_field, current_value + increment)
            user.last_activity = datetime.utcnow()
            db.commit()
            return True
        else:
            logger.error(f"Invalid stat field: {stat_field}")
            return False
    except Exception as e:
        logger.error(f"Error updating user stats: {e}")
        db.rollback()
        return False


def get_user_stats(db: Session, telegram_id: int) -> Optional[User]:
    """Get user statistics."""
    return db.query(User).filter(User.telegram_id == telegram_id).first()


def save_conversation_message(
    db: Session,
    telegram_id: int,
    role: str,
    content: str,
    conversation_type: str,
    persona: str = None,
) -> bool:
    """Save conversation message."""
    try:
        user = get_or_create_user(db, telegram_id)

        conversation = Conversation(
            user_id=user.id,
            role=role,
            content=content,
            conversation_type=conversation_type,
            persona=persona,
        )

        db.add(conversation)
        db.commit()
        return True
    except Exception as e:
        logger.error(f"Error saving conversation: {e}")
        db.rollback()
        return False


def get_conversation_history(
    db: Session, telegram_id: int, conversation_type: str, limit: int = 10
) -> List[Conversation]:
    """Get conversation history."""
    user = get_or_create_user(db, telegram_id)

    return (
        db.query(Conversation)
        .filter(Conversation.user_id == user.id)
        .filter(Conversation.conversation_type == conversation_type)
        .order_by(Conversation.timestamp.desc())
        .limit(limit)
        .all()[::-1]
    )


def clear_conversation_history(
    db: Session, telegram_id: int, conversation_type: str
) -> bool:
    """Clear conversation history."""
    try:
        user = get_or_create_user(db, telegram_id)

        db.query(Conversation).filter(
            Conversation.user_id == user.id,
            Conversation.conversation_type == conversation_type,
        ).delete()

        db.commit()
        return True
    except Exception as e:
        logger.error(f"Error clearing conversation history: {e}")
        db.rollback()
        return False


def save_quiz_result(
    db: Session,
    telegram_id: int,
    topic: str,
    correct_answers: int,
    total_questions: int,
) -> bool:
    """Save quiz result."""
    try:
        user = get_or_create_user(db, telegram_id)

        score_percentage = (
            (correct_answers / total_questions) * 100 if total_questions > 0 else 0
        )

        quiz_result = QuizResult(
            user_id=user.id,
            topic=topic,
            correct_answers=correct_answers,
            total_questions=total_questions,
            score_percentage=score_percentage,
        )

        db.add(quiz_result)

        # Update user stats
        user.quizzes_completed += 1
        user.last_activity = datetime.utcnow()

        db.commit()
        return True
    except Exception as e:
        logger.error(f"Error saving quiz result: {e}")
        db.rollback()
        return False


def get_quiz_stats(db: Session, telegram_id: int, topic: str = None) -> dict:
    """Get quiz statistics."""
    user = get_or_create_user(db, telegram_id)

    query = db.query(QuizResult).filter(QuizResult.user_id == user.id)

    if topic:
        query = query.filter(QuizResult.topic == topic)

    results = query.all()

    if not results:
        return {
            "total_quizzes": 0,
            "average_score": 0,
            "best_score": 0,
            "topics_played": [],
        }

    total_quizzes = len(results)
    average_score = sum(r.score_percentage for r in results) / total_quizzes
    best_score = max(r.score_percentage for r in results)
    topics_played = list(set(r.topic for r in results))

    return {
        "total_quizzes": total_quizzes,
        "average_score": round(average_score, 2),
        "best_score": round(best_score, 2),
        "topics_played": topics_played,
    }


def save_translation(
    db: Session,
    telegram_id: int,
    original_text: str,
    translated_text: str,
    target_language: str,
    source_language: str = None,
) -> bool:
    """Save translation history."""
    try:
        user = get_or_create_user(db, telegram_id)

        translation = TranslationHistory(
            user_id=user.id,
            original_text=original_text,
            translated_text=translated_text,
            source_language=source_language,
            target_language=target_language,
        )

        db.add(translation)

        user.translations_made += 1
        user.last_activity = datetime.utcnow()

        db.commit()
        return True
    except Exception as e:
        logger.error(f"Error saving translation: {e}")
        db.rollback()
        return False


def add_vocabulary_word(
    db: Session, telegram_id: int, word: str, translation: str, language: str
) -> bool:
    """Add word to vocabulary."""
    try:
        user = get_or_create_user(db, telegram_id)

        existing = (
            db.query(VocabularyWord)
            .filter(
                VocabularyWord.user_id == user.id,
                VocabularyWord.word == word,
                VocabularyWord.language == language,
            )
            .first()
        )

        if existing:
            return False

        vocab_word = VocabularyWord(
            user_id=user.id, word=word, translation=translation, language=language
        )

        db.add(vocab_word)
        db.commit()
        return True
    except Exception as e:
        logger.error(f"Error adding vocabulary word: {e}")
        db.rollback()
        return False


def get_user_vocabulary(
    db: Session, telegram_id: int, language: str = None
) -> List[VocabularyWord]:
    """Get user's vocabulary words."""
    user = get_or_create_user(db, telegram_id)

    query = db.query(VocabularyWord).filter(VocabularyWord.user_id == user.id)

    if language:
        query = query.filter(VocabularyWord.language == language)

    return query.order_by(VocabularyWord.learned_at.desc()).all()
