from pydantic import BaseModel, Field
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper

def explore(query: str, max_results: int = 2):
    wikipedia = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper(top_k_results=max_results))
    return wikipedia.run(query).split("\n\n")

