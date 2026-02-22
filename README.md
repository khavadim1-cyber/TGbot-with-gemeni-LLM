# TGbot-with-gemini-LLM

A Telegram bot written in **Python** that integrates **Google Gemini (Generative AI / LLM)** and uses **vector embeddings (ChromaDB)** to answer user questions based on PDF documents.

This project combines a Telegram bot with an LLM-powered knowledge base built from your own documents. Chat memory is saved to JSON file.

---

##  Overview

The bot processes incoming Telegram messages, retrieves relevant information from embedded PDF documents, sends context to the **Gemini LLM API**, and returns AI-generated responses to the user in telegram bot chat.

The workflow consists of two main stages:

1. **Ingesting PDF documents** into a vector database (ChromaDB)
2. **Running the Telegram bot**, which queries this database and the Gemini model

---

## Project Structure

```
TGbot-with-gemini-LLM/
├── main.py             # Main Telegram bot logic
├── ingest.py           # PDF ingestion and vector database creation
├── requirements.txt    # Python dependencies
├── books/              # Folder with PDF files (created manually)
├── chroma_db/          # Vector database (created automatically)
└── README.md           # Project documentation
```

---

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/khavadim1-cyber/TGbot-with-gemini-LLM.git
   cd TGbot-with-gemini-LLM
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

---

##  API Keys & Environment Setup

To run the project, you **must create API keys** and set them as environment variables (or in a `.env` file):

```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
GEMINI_API_KEY=your_gemini_api_key
```

* `TELEGRAM_BOT_TOKEN` — get it from **@BotFather** in Telegram
* `GEMINI_API_KEY` — get it from **Google Generative AI (Gemini)**

---

##  Preparing Documents (IMPORTANT)

Before running the bot, you need to prepare your documents:

1. **Create a folder named `books`** in the project root:

   ```bash
   mkdir books
   ```

2. **Add PDF files** to the `books/` folder
   (these files will be used as the bot’s knowledge base)

Example:

```
books/
├── document1.pdf
├── document2.pdf
```

---

##  Ingest PDFs into Vector Database

After adding PDF files, run:

```bash
python ingest.py
```

This step will:

* Read all PDF files from the `books/` folder
* Generate embeddings
* Create a **ChromaDB vector database**

After successful execution, a new folder will appear:

```
chroma_db/
```

 **Do not delete this folder** — it is required for the bot to work.

---

##  Run the Telegram Bot

Once `chroma_db/` is created, start the bot:

```bash
python main.py
```

The bot is now ready to answer questions using the content of your PDF files.

---


##  Customization

* `ingest.py` — document parsing, embeddings, vector store logic
* `main.py` — Telegram handlers, prompts, bot behavior
* `books/` — replace or add PDFs to update the knowledge base
  (re-run `ingest.py` after changes)

---

##  Contributing

1. Fork the repository
2. Create a new branch (`feature/your-feature`)
3. Commit your changes
4. Open a Pull Request

---

##  License

MIT License

---

##  Contact

If you have questions or suggestions, feel free to open an issue in the repository.
