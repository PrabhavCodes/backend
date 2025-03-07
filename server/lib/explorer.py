from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_core.tools import tool

@tool(
    name_or_callable="Wikipedia Explorer",
    description="Useful for retreiving relevant pages from Wikipedia",
    response_format="content"
)
def explore(query: str):
    wikipedia = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper(
        top_k_results=3,
        load_all_available_meta=True,
        doc_content_chars_max=6000
    ))
    return wikipedia.run(query).split("\n\n")

