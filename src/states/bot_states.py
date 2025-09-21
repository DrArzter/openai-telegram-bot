# states/bot_states.py
from aiogram.fsm.state import State, StatesGroup

class GPTStates(StatesGroup):
    """States for /gpt command - direct ChatGPT interface."""
    waiting_for_question = State()

class PersonalityStates(StatesGroup):
    """States for /talk command - conversation with personalities."""
    choosing_personality = State()
    chatting_with_personality = State()

class QuizStates(StatesGroup):
    """States for /quiz command - quiz functionality."""
    choosing_topic = State()
    waiting_for_answer = State()
    showing_result = State()

class TranslatorStates(StatesGroup):
    """States for translator functionality."""
    choosing_language = State()
    waiting_for_text = State()

class VisionStates(StatesGroup):
    """States for image recognition functionality."""
    waiting_for_image = State()

class ResumeStates(StatesGroup):
    """States for resume builder functionality."""
    collecting_education = State()
    collecting_experience = State()
    collecting_skills = State()
    generating_resume = State()

class VocabularyStates(StatesGroup):
    """States for vocabulary trainer functionality."""
    learning_mode = State()
    test_mode = State()
    waiting_for_translation = State()

class RecommendationStates(StatesGroup):
    """States for movie/book recommendations."""
    choosing_category = State()  # movies, books, music
    choosing_genre = State()
    showing_recommendations = State()
    collecting_dislikes = State()