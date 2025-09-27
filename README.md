# Telegram ChatGPT Bot

A simple Telegram bot that uses the ChatGPT API to generate responses to user queries. Built as a learning project. Command handling is encapsulated in controllers, utilities cover shared logic, and middlewares extend bot behavior.

---

## ⚙️ Technical Stack

- **Python 3.11**
- **Aiogram**
- **python-dotenv**
- **openai**

---

## 🚀 Setup & Verification

Follow these steps to set up the project locally.  
The project was tested with **Arch Linux**, but should work on other Linux distributions if `python3` and `pip3` are available in `PATH`.

### 1. Clone the Repository

```bash
git clone https://github.com/DrArzter/telegram-bot
cd telegram-bot
```

### 2. Install Dependencies

```bash
pip3 install -r requirements.txt
```

### 3. Configure Environment Variables

```bash
cp .env.example .env
```

Then add your **Telegram Bot Token** inside `.env` as well as **OpenAI API Key**.

### 4. Run the Bot

via python (not recommended):

```bash
python3 src/main.py
```

via docker:

```bash
docker-compose up -d --build
```

---

## 📡 Usage Examples

- `/start` – Initialize the bot
- `/help` – Show available commands
- `/random` – Get a random fact
- `/gpt` – Ask ChatGPT directly
- `/talk` – Talk to Famous Personalities
- `/image` – Generate a caption for an image
- `/quiz` – Take a Quiz
- `/translate` – Translate text
- `/vocabulary` – Learn vocabulary

---

## 🏗️ Project Structure

```markdown
src/
├── callbacks/
├── database/
├── handlers/
├── keyboards/
├── lexicon/
├── middleware/
├── services/
├── states/
├── utils/
└── main.py
```

---
