## 🤖 LangChain + Gentoro CLI Chatbot

This is a simple command-line chatbot powered by **LangChain**, **OpenAI**, and **Gentoro Tools**. It handles tool-augmented prompts using `.bind_tools()` and responds to a single user query before exiting.

---

### 🛠 Features

- Uses `gpt-4o-mini` via LangChain
- Auto-detects tool usage via Gentoro
- Runs tools dynamically and responds accordingly
- Command-line interface, exits after one answer

---

### 📦 Requirements

- Python 3.11+
- `pip install -r requirements.txt`

```text
langchain-openai
langchain-core
python-dotenv
Gentoro
```

---

### 🔧 Setup

1. **Clone the repo**

```bash
git clone https://github.com/gentoro-GT/python-sdk-examples.git
cd python-sdk-examples
```

2. **Set your environment variables**

Create a `.env` file:

```env
OPENAI_API_KEY=your-openai-key
GENTORO_BRIDGE_UID=your-gentoro-bridge-uid
GENTORO_BASE_URL= your-gentoro-base-url
GENTORO_AUTH_MOD_BASE_URL=your-gentoro-auth-url
GENTORO_API_KEY= your-gentoro-api-key
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

---

### 🚀 Run the Chatbot

```bash
python main.py
```

Sample output:

```
🤖 LangChain Chatbot w/ Gentoro Tools via .bind_tools Ready!

You: what’s the weather in NYC?
AI: The current weather in NYC is sunny with a high of 63°F.
```


