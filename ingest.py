import os
import shutil
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()
GOOGLE_API_KEY  = os.getenv("API")

# Model in main.py and ingest.py have to be the same
EMBED_MODEL = "models/embedding-001"

def create_knowledge_base():
    if not os.path.exists('./books'):
        os.makedirs('./books')
        return

#checking
    files = [f for f in os.listdir('./books') if f.endswith('.pdf')]
    if not files:
        print("No files in ./books folder")
        return

    
    
    if os.path.exists("./chroma_db"):
        print("Deleting old ChromaDB")
        shutil.rmtree("./chroma_db")

    try:
        # Загрузчик
        loader = DirectoryLoader('./books', glob="./*.pdf", loader_cls=PyPDFLoader)
        documents = loader.load()
        print(f" Downloaded {len(documents)}")
    except Exception as e:
        print(f"Error: {e}")
        return

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, 
        chunk_overlap=200,
        add_start_index=True )
    texts = text_splitter.split_documents(documents)
    print(f" Total fragments{len(texts)}")

    print(f"({EMBED_MODEL}) ")

    try:
        embeddings = GoogleGenerativeAIEmbeddings(
            api_key=GOOGLE_API_KEY,
            model=EMBED_MODEL 
        )
        
        vector_db = Chroma.from_documents(
            documents=texts, 
            embedding=embeddings,
            persist_directory="./chroma_db"  
        )
        print("Database is ready")
        
    except Exception as e:
        print(f"\nError with api {e}")
        

if __name__ == "__main__":
    create_knowledge_base()
