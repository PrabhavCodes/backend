from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_core.tools import tool

@tool(
    name_or_callable="Wikipedia Explorer",
    description="Useful for retreiving relevant pages from Wikipedia",
    response_format="content"
)
def explore(query: str, max_results: int = 2, load_all_available_meta: bool = True, doc_chars_max: int = 8000):
    wikipedia = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper(top_k_results=max_results, load_all_available_meta=load_all_available_meta, doc_content_chars_max=doc_chars_max))
    return wikipedia.run(query).split("\n\n")

