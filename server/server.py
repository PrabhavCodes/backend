from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from lib.explorer import explore

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (change as needed)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Root endpoint
@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}

# Pydantic model for /llama endpoint
class Message(BaseModel):
    text: str

# Pydantic model for /ideaExplorer endpoint
class Idea(BaseModel):
    query: str
    max_results: int

# /llama endpoint
@app.post('/llama')
def llama_root(message: Message):
    results = explore(query=message.text, max_results = message.max_results)  # Use message.text for the query
    return {
        "results": results
    }

# /ideaExplorer endpoint
@app.post('/ideaExplorer')
def explore_idea(message: Idea):
    results = explore(query=message.query, max_results=message.max_results)
    return {
        "query": message.query,
        "max_results": message.max_results,
        "results": results
    }

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)