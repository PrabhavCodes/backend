from pydantic import BaseModel, Field
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper

def explore(query: str, max_results: int = 2, load_all_available_meta: bool = False, doc_chars_max: int = 4000):
    wikipedia = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper(top_k_results=max_results, load_all_available_meta=True, doc_content_chars_max=doc_chars_max))
    return wikipedia.run(query).split("\n\n")

