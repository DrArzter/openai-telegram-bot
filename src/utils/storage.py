import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from utils.logger import get_logger

logger = get_logger(__name__)

# Data files
CONVERSATIONS_FILE = "conversations.json"
USER_STATS_FILE = "user_stats.json"
QUIZ_RESULTS_FILE = "quiz_results.json"


def load_json_file(filename: str) -> List[Dict[str, Any]]:
    """
    Load data from JSON file.

    Args:
        filename: Name of the JSON file

    Returns:
        List of data from file or empty list if file doesn't exist
    """
    if not os.path.exists(filename):
        logger.info(f"File {filename} not found, creating empty list")
        return []

    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
            logger.info(f"Loaded {len(data)} records from {filename}")
            return data
    except (json.JSONDecodeError, FileNotFoundError) as e:
        logger.error(f"Error loading {filename}: {e}")
        return []


def save_json_file(filename: str, data: List[Dict[str, Any]]) -> bool:
    """
    Save data to JSON file.

    Args:
        filename: Name of the JSON file
        data: Data to save

    Returns:
        True if saved successfully
    """
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"Saved {len(data)} records to {filename}")
        return True
    except Exception as e:
        logger.error(f"Error saving {filename}: {e}")
        return False


# === CONVERSATION MANAGEMENT ===


def save_conversation_message(
    user_id: int,
    role: str,
    content: str,
    conversation_type: str = "general",
    persona: Optional[str] = None,
) -> bool:
    """
    Save a conversation message.

    Args:
        user_id: User ID
        role: Message role (user/assistant/system)
        content: Message content
        conversation_type: Type of conversation (general, personality, quiz, etc.)
        persona: Persona name if applicable

    Returns:
        True if saved successfully
    """
    conversations = load_json_file(CONVERSATIONS_FILE)

    message = {
        "user_id": user_id,
        "role": role,
        "content": content,
        "conversation_type": conversation_type,
        "persona": persona,
        "timestamp": datetime.now().isoformat(),
    }

    conversations.append(message)
    result = save_json_file(CONVERSATIONS_FILE, conversations)

    if result:
        logger.info(
            f"Saved conversation message for user {user_id}, type: {conversation_type}"
        )

    return result


def get_conversation_history(
    user_id: int, conversation_type: str = "general", limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Get conversation history for a user.

    Args:
        user_id: User ID
        conversation_type: Type of conversation to retrieve
        limit: Maximum number of messages to return

    Returns:
        List of conversation messages
    """
    conversations = load_json_file(CONVERSATIONS_FILE)

    user_conversations = [
        msg
        for msg in conversations
        if msg["user_id"] == user_id and msg["conversation_type"] == conversation_type
    ]

    # Sort by timestamp (most recent last) and limit
    user_conversations.sort(key=lambda x: x["timestamp"])
    return user_conversations[-limit:] if user_conversations else []


def clear_conversation_history(
    user_id: int, conversation_type: str = "general"
) -> bool:
    """
    Clear conversation history for a user and conversation type.

    Args:
        user_id: User ID
        conversation_type: Type of conversation to clear

    Returns:
        True if cleared successfully
    """
    conversations = load_json_file(CONVERSATIONS_FILE)

    # Keep only messages that don't match the criteria
    filtered_conversations = [
        msg
        for msg in conversations
        if not (
            msg["user_id"] == user_id and msg["conversation_type"] == conversation_type
        )
    ]

    result = save_json_file(CONVERSATIONS_FILE, filtered_conversations)

    if result:
        logger.info(
            f"Cleared {conversation_type} conversation history for user {user_id}"
        )

    return result


# === USER STATISTICS ===


def get_user_stats(user_id: int) -> Dict[str, Any]:
    """
    Get user statistics.

    Args:
        user_id: User ID

    Returns:
        Dictionary with user stats
    """
    stats = load_json_file(USER_STATS_FILE)

    user_stat = next((stat for stat in stats if stat["user_id"] == user_id), None)

    if not user_stat:
        # Create new user stats
        user_stat = {
            "user_id": user_id,
            "total_messages": 0,
            "random_facts_requested": 0,
            "gpt_queries": 0,
            "personality_chats": 0,
            "quizzes_completed": 0,
            "translations_made": 0,
            "created_at": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat(),
        }

        stats.append(user_stat)
        save_json_file(USER_STATS_FILE, stats)
        logger.info(f"Created new stats for user {user_id}")

    return user_stat


def update_user_stats(user_id: int, stat_type: str, increment: int = 1) -> bool:
    """
    Update user statistics.

    Args:
        user_id: User ID
        stat_type: Type of statistic to update
        increment: Amount to increment by

    Returns:
        True if updated successfully
    """
    stats = load_json_file(USER_STATS_FILE)

    for stat in stats:
        if stat["user_id"] == user_id:
            if stat_type in stat:
                stat[stat_type] += increment
                stat["last_activity"] = datetime.now().isoformat()

                result = save_json_file(USER_STATS_FILE, stats)
                if result:
                    logger.info(f"Updated {stat_type} for user {user_id}")
                return result

    logger.warning(f"User {user_id} not found for stats update")
    return False


# === QUIZ MANAGEMENT ===


def save_quiz_result(
    user_id: int, topic: str, correct_answers: int, total_questions: int
) -> bool:
    """
    Save quiz result.

    Args:
        user_id: User ID
        topic: Quiz topic
        correct_answers: Number of correct answers
        total_questions: Total number of questions

    Returns:
        True if saved successfully
    """
    quiz_results = load_json_file(QUIZ_RESULTS_FILE)

    result = {
        "user_id": user_id,
        "topic": topic,
        "correct_answers": correct_answers,
        "total_questions": total_questions,
        "score_percentage": (
            (correct_answers / total_questions) * 100 if total_questions > 0 else 0
        ),
        "timestamp": datetime.now().isoformat(),
    }

    quiz_results.append(result)
    save_result = save_json_file(QUIZ_RESULTS_FILE, quiz_results)

    if save_result:
        logger.info(
            f"Saved quiz result for user {user_id}: {correct_answers}/{total_questions} on {topic}"
        )

    return save_result


def get_quiz_stats(user_id: int, topic: Optional[str] = None) -> Dict[str, Any]:
    """
    Get quiz statistics for a user.

    Args:
        user_id: User ID
        topic: Specific topic (optional)

    Returns:
        Dictionary with quiz statistics
    """
    quiz_results = load_json_file(QUIZ_RESULTS_FILE)

    user_results = [result for result in quiz_results if result["user_id"] == user_id]

    if topic:
        user_results = [result for result in user_results if result["topic"] == topic]

    if not user_results:
        return {
            "total_quizzes": 0,
            "average_score": 0,
            "best_score": 0,
            "topics_played": [],
        }

    total_quizzes = len(user_results)
    average_score = (
        sum(result["score_percentage"] for result in user_results) / total_quizzes
    )
    best_score = max(result["score_percentage"] for result in user_results)
    topics_played = list(set(result["topic"] for result in user_results))

    return {
        "total_quizzes": total_quizzes,
        "average_score": round(average_score, 2),
        "best_score": round(best_score, 2),
        "topics_played": topics_played,
    }


# === UTILITY FUNCTIONS ===


def get_total_stats() -> Dict[str, Any]:
    """
    Get overall bot usage statistics.

    Returns:
        Dictionary with total statistics
    """
    conversations = load_json_file(CONVERSATIONS_FILE)
    user_stats = load_json_file(USER_STATS_FILE)
    quiz_results = load_json_file(QUIZ_RESULTS_FILE)

    return {
        "total_users": len(user_stats),
        "total_messages": len(conversations),
        "total_quizzes": len(quiz_results),
        "active_conversations": len(set(msg["user_id"] for msg in conversations)),
    }
