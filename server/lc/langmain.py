from langchain_ollama import ChatOllama


def langmain(query:str)->str:
    model = ChatOllama(model = 'llama3.2:1b',temperature = 0.3)
    response = model.invoke(query)
    return response.content

