import asyncio
import logging
import sys
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import Message, ContentType
from aiogram.filters import CommandStart, Command
from langchain_chroma import Chroma
load_dotenv()
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.output_parsers import StrOutputParser 
from langchain_community.chat_message_histories import FileChatMessageHistory

GOOGLE_API_KEY  = os.getenv("API")
TELEGRAM_TOKEN= os.getenv("TOKEN")

#Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)



# Memory
store = {}
def get_session_history(session_id: str):
    os.makedirs("memory", exist_ok=True)
    return FileChatMessageHistory(f"memory/{session_id}.json")

# initialisation
embed_model_name = "models/text-embedding-004" 
embeddings = GoogleGenerativeAIEmbeddings(
    model=embed_model_name,
    google_api_key=GOOGLE_API_KEY
)

db_folder = "./chroma_db"
db = None
if os.path.exists(db_folder):
    try:
        db = Chroma(persist_directory=db_folder, embedding_function=embeddings)
        logger.info(f"DB working: {db_folder}")
    except Exception as e:
        logger.error(f"DB not working: {e}")
else:
    logger.warning("No RAG folder")

# LLM
chat_model_name = "gemini-2.5-pro"

llm = ChatGoogleGenerativeAI(
    model=chat_model_name,
    temperature=0.7,
    google_api_key=GOOGLE_API_KEY,
    safety_settings = {
    "HARM_CATEGORY_HARASSMENT": "BLOCK_NONE",
    "HARM_CATEGORY_HATE_SPEECH": "BLOCK_NONE",
    "HARM_CATEGORY_SEXUALLY_EXPLICIT": "BLOCK_NONE",
    "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_NONE",
    },
    max_output_tokens=500
)

system_prompt_text = """
Type your prompt here
{context}
"""
#Message history
prompt_template = ChatPromptTemplate.from_messages([
    ("system", system_prompt_text),
    MessagesPlaceholder(variable_name="chat_history"), 
    ("user", "{input}")
])


rag_chain = prompt_template | llm | StrOutputParser()

conversation_chain = RunnableWithMessageHistory(
    rag_chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="chat_history",
)

async def generate_response(user_input, user_id):
    context_text = ""
    if db:
        try:
            docs = await asyncio.to_thread(db.similarity_search, user_input, k=3)
            if docs: 
                context_text = "\n".join([d.page_content for d in docs])
        except Exception:
            pass 
    
    response_text = await conversation_chain.ainvoke(
        {"input": user_input, "context": context_text},
        config={"configurable": {"session_id": str(user_id)}}
    )

    return response_text

# BOT
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer("Hello")

@dp.message(F.photo)
async def handle_photo(message: Message):
    await message.answer("I cant see a photo")

@dp.message(F.animation)
async def handle_gif(message: Message):
    await message.answer("I cant see a gif")

@dp.message(F.sticker)
async def handle_sticker(message: Message):
    await message.answer("I cant see a sticker")

@dp.message(F.voice)
async def handle_voice(message: Message):
    await message.answer("I cant see a voice")

@dp.message(Command("clear"))
async def cmd_clear(message: types.Message):
    user_id = str(message.chat.id)
    if user_id in store:
        del store[user_id]
        await message.answer("Memory is cleared.")
    else:
        await message.answer("Memory is empty.")

@dp.message(F.text)
async def handle_message(message: types.Message):
    await bot.send_chat_action(chat_id=message.chat.id, action="typing")
    try:
        ans = await generate_response(message.text, message.chat.id)
        try:
            await message.answer(ans, parse_mode="Markdown")
        except:
            await message.answer(ans)
    except Exception as e:
        logger.error(f"Error: {e}")
        await message.answer(f"Error: {str(e)}")

if __name__ == "__main__":
    try:
        asyncio.run(dp.start_polling(bot))
    except KeyboardInterrupt:
        pass