# Telegram ChatGPT Bot

---

## ⚙️ Technical Stack

- **Python 3.10+**  
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
````

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

```bash
python3 src/main.py
```

---

## 📡 Usage Examples

* `/start` – Initialize the bot
* `/help` – Show available commands

---

## 🏗️ Project Structure

```markdown
src/
├── controllers/
├── middleware/
│   └── logging.py
├── utils/
│   ├── logger.py
│   ├── set_commands.py
│   └── storage.py
└── main.py
```

---
