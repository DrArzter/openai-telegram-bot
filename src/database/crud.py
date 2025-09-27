# database/crud.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete
from database.models import (
    User as DBUser,
    Conversation,
    QuizResult,
    TranslationHistory,
    VocabularyWord,
)
from datetime import datetime, timezone
from typing import List, Optional
from utils.logger import get_logger

logger = get_logger(__name__)


async def get_or_create_user(
    db: AsyncSession, telegram_id: int, username: Optional[str] = None
) -> DBUser:
    """Get user by telegram_id or create new one."""
    try:
        result = await db.execute(
            select(DBUser).where(DBUser.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            user = DBUser(telegram_id=telegram_id, username=username)
            db.add(user)
            await db.commit()
            await db.refresh(user)

        return user
    except Exception as e:
        logger.error(f"Error getting or creating user: {e}")
        await db.rollback()
        raise


async def update_user_stats(
    db: AsyncSession, user: DBUser, stat_field: str, increment: int = 1
) -> bool:
    """Update user statistics."""
    try:
        if hasattr(user, stat_field):
            current_value = getattr(user, stat_field, 0)
            setattr(user, stat_field, current_value + increment)
            user.last_activity = datetime.now(timezone.utc)
            await db.commit()
            await db.refresh(user)
            return True
        else:
            logger.error(f"Invalid stat field: {stat_field}")
            return False
    except Exception as e:
        logger.error(f"Error updating user stats: {e}")
        await db.rollback()
        return False


async def get_user_stats(db: AsyncSession, telegram_id: int) -> Optional[DBUser]:
    """Get user statistics by telegram_id asynchronously."""
    result = await db.execute(select(DBUser).where(DBUser.telegram_id == telegram_id))
    return result.scalar_one_or_none()


async def save_conversation_message(
    db: AsyncSession,
    user: DBUser,
    role: str,
    content: str,
    conversation_type: str,
    persona: Optional[str] = None,
) -> bool:
    """Save conversation message asynchronously."""
    try:
        conversation = Conversation(
            user_id=user.id,
            role=role,
            content=content,
            conversation_type=conversation_type,
            persona=persona,
        )
        db.add(conversation)
        await db.commit()
        await db.refresh(conversation)
        return True
    except Exception as e:
        logger.error(f"Error saving conversation: {e}")
        await db.rollback()
        return False


async def get_conversation_history(
    db: AsyncSession, user: DBUser, conversation_type: str, limit: int = 10
) -> List[Conversation]:
    """Get conversation history asynchronously."""
    result = await db.execute(
        select(Conversation)
        .where(Conversation.user_id == user.id)
        .where(Conversation.conversation_type == conversation_type)
        .order_by(Conversation.timestamp.desc())
        .limit(limit)
    )
    conversations = list(result.scalars().all())
    return conversations[::-1]


async def clear_conversation_history(
    db: AsyncSession, user: DBUser, conversation_type: str
) -> bool:
    """Clear conversation history asynchronously."""
    try:
        await db.execute(
            delete(Conversation).where(
                Conversation.user_id == user.id,
                Conversation.conversation_type == conversation_type,
            )
        )
        await db.commit()
        return True
    except Exception as e:
        logger.error(f"Error clearing conversation history: {e}")
        await db.rollback()
        return False


async def save_quiz_result(
    db: AsyncSession,
    user: DBUser,
    topic: str,
    correct_answers: int,
    total_questions: int,
) -> bool:
    """Save quiz result asynchronously."""
    try:
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
        await db.commit()
        await db.refresh(quiz_result)
        return True
    except Exception as e:
        logger.error(f"Error saving quiz result: {e}")
        await db.rollback()
        return False


async def get_quiz_stats(
    db: AsyncSession, user: DBUser, topic: Optional[str] = None
) -> dict:
    """Get quiz statistics asynchronously."""
    stmt = select(QuizResult).where(QuizResult.user_id == user.id)
    if topic:
        stmt = stmt.where(QuizResult.topic == topic)

    result = await db.execute(stmt)
    results = result.scalars().all()

    if not results:
        return {
            "total_quizzes": 0,
            "average_score": 0,
            "best_score": 0,
            "topics_played": [],
        }

    total_quizzes = len(results)
    scores = [float(r.score_percentage) for r in results]
    average_score = round(sum(scores) / len(scores), 2)
    best_score = round(max(scores), 2)
    topics_played = list({r.topic for r in results})

    return {
        "total_quizzes": total_quizzes,
        "average_score": average_score,
        "best_score": best_score,
        "topics_played": topics_played,
    }


async def save_translation(
    db: AsyncSession,
    user: DBUser,
    original_text: str,
    translated_text: str,
    target_language: str,
    source_language: Optional[str] = None,
) -> bool:
    """Save translation history asynchronously."""
    try:
        translation = TranslationHistory(
            user_id=user.id,
            original_text=original_text,
            translated_text=translated_text,
            source_language=source_language,
            target_language=target_language,
        )
        db.add(translation)
        await update_user_stats(db, user, "translations_made")
        await db.commit()
        await db.refresh(translation)
        return True
    except Exception as e:
        logger.error(f"Error saving translation: {e}")
        await db.rollback()
        return False


async def add_vocabulary_word(
    db: AsyncSession, user: DBUser, word: str, translation: str, language: str
) -> bool:
    """Add word to vocabulary asynchronously."""
    try:
        result = await db.execute(
            select(VocabularyWord).where(
                VocabularyWord.user_id == user.id,
                VocabularyWord.word == word,
                VocabularyWord.language == language,
            )
        )
        if result.scalar_one_or_none():
            return False

        vocab_word = VocabularyWord(
            user_id=user.id, word=word, translation=translation, language=language
        )
        db.add(vocab_word)
        await db.commit()
        await db.refresh(vocab_word)
        return True
    except Exception as e:
        logger.error(f"Error adding vocabulary word: {e}")
        await db.rollback()
        return False


async def update_vocabulary_word_stats(
    db: AsyncSession, word_id: int, was_correct: bool
) -> Optional[VocabularyWord]:
    """Updates the practice statistics for a vocabulary word."""
    try:
        result = await db.execute(
            select(VocabularyWord).where(VocabularyWord.id == word_id)
        )
        word = result.scalar_one_or_none()
        if not word:
            return None

        word.times_practiced += 1
        word.last_practiced = datetime.now(timezone.utc)
        if was_correct:
            word.times_correct += 1

        await db.commit()
        await db.refresh(word)
        return word
    except Exception as e:
        logger.error(f"Error updating vocabulary word stats: {e}")
        await db.rollback()
        return None


async def get_user_vocabulary(
    db: AsyncSession, user: DBUser, language: Optional[str] = None
) -> List[VocabularyWord]:
    """Get user's vocabulary words asynchronously."""
    stmt = select(VocabularyWord).where(VocabularyWord.user_id == user.id)
    if language:
        stmt = stmt.where(VocabularyWord.language == language)

    stmt = stmt.order_by(VocabularyWord.learned_at.desc())
    result = await db.execute(stmt)
    return list(result.scalars().all())
