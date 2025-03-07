from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from lib.explorer import explore
from lib.wiki_chain import wiki_chain

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

class Idea(BaseModel):
    query: str

# /ideaExplorer endpoint
@app.post('/ideaExplorer')
def explore_idea(message: Idea):
    results = wiki_chain(query=message.query)
    return {"results": results}

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)