# database/crud.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database.models import (
    User,
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
) -> User:
    """Get user by telegram_id or create new one."""
    try:
        result = await db.execute(select(User).where(User.telegram_id == telegram_id))
        user = result.scalar_one_or_none()

        if not user:
            user = User(telegram_id=telegram_id, username=username)
            db.add(user)
            await db.commit()
            await db.refresh(user)

        return user
    except Exception as e:
        logger.error(f"Error getting or creating user: {e}")
        await db.rollback()
        raise


async def update_user_stats(
    db: AsyncSession, telegram_id: int, stat_field: str, increment: int = 1
) -> bool:
    """Update user statistics."""
    try:
        user = await get_or_create_user(db, telegram_id)

        if hasattr(user, stat_field):
            current_value = getattr(user, stat_field, 0)
            setattr(user, stat_field, current_value + increment)
            user.last_activity = datetime.now(timezone.utc)  # type: ignore
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


async def get_user_stats(db: AsyncSession, telegram_id: int) -> Optional[User]:
    """Get user statistics asynchronously."""
    result = await db.execute(select(User).where(User.telegram_id == telegram_id))
    user = result.scalar_one_or_none()
    return user


async def save_conversation_message(
    db: AsyncSession,
    telegram_id: int,
    role: str,
    content: str,
    conversation_type: str,
    persona: Optional[str] = None,
) -> bool:
    """Save conversation message asynchronously."""
    try:
        user = await get_or_create_user(db, telegram_id)

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


from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete, select
from typing import List
from database.models import Conversation
from .crud import get_or_create_user


async def get_conversation_history(
    db: AsyncSession, telegram_id: int, conversation_type: str, limit: int = 10
) -> List[Conversation]:
    """Get conversation history asynchronously."""
    user = await get_or_create_user(db, telegram_id)

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
    db: AsyncSession, telegram_id: int, conversation_type: str
) -> bool:
    """Clear conversation history asynchronously."""
    try:
        user = await get_or_create_user(db, telegram_id)

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
    telegram_id: int,
    topic: str,
    correct_answers: int,
    total_questions: int,
) -> bool:
    """Save quiz result asynchronously."""
    try:
        user = await get_or_create_user(db, telegram_id)

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
        user.quizzes_completed += 1  # type: ignore
        user.last_activity = datetime.now(timezone.utc)  # type: ignore

        await db.commit()
        await db.refresh(quiz_result)
        return True
    except Exception as e:
        logger.error(f"Error saving quiz result: {e}")
        await db.rollback()
        return False


async def get_quiz_stats(
    db: AsyncSession, telegram_id: int, topic: Optional[str] = None
) -> dict:
    """Get quiz statistics asynchronously."""
    user = await get_or_create_user(db, telegram_id)

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
    scores = [float(r.score_percentage) for r in results]  # type: ignore
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
    telegram_id: int,
    original_text: str,
    translated_text: str,
    target_language: str,
    source_language: Optional[str] = None,
) -> bool:
    """Save translation history asynchronously."""
    try:
        user = await get_or_create_user(db, telegram_id)

        translation = TranslationHistory(
            user_id=user.id,
            original_text=original_text,
            translated_text=translated_text,
            source_language=source_language,
            target_language=target_language,
        )

        db.add(translation)

        # Update user stats
        user.translations_made += 1  # type: ignore
        user.last_activity = datetime.now(timezone.utc)  # type: ignore

        await db.commit()
        await db.refresh(translation)
        return True
    except Exception as e:
        logger.error(f"Error saving translation: {e}")
        await db.rollback()
        return False


async def add_vocabulary_word(
    db: AsyncSession, telegram_id: int, word: str, translation: str, language: str
) -> bool:
    """Add word to vocabulary asynchronously."""
    try:
        user = await get_or_create_user(db, telegram_id)

        result = await db.execute(
            select(VocabularyWord).where(
                VocabularyWord.user_id == user.id,
                VocabularyWord.word == word,
                VocabularyWord.language == language,
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
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


async def get_user_vocabulary(
    db: AsyncSession, telegram_id: int, language: Optional[str] = None
) -> List[VocabularyWord]:
    """Get user's vocabulary words asynchronously."""
    user = await get_or_create_user(db, telegram_id)

    stmt = select(VocabularyWord).where(VocabularyWord.user_id == user.id)
    if language:
        stmt = stmt.where(VocabularyWord.language == language)

    stmt = stmt.order_by(VocabularyWord.learned_at.desc())

    result = await db.execute(stmt)
    words = list(result.scalars().all())
    return words
