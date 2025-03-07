from langchain_ollama import ChatOllama

llm = ChatOllama(model="llama3.2:1b", temperature=0.2, stream=True)