from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, START, END
from typing import List, TypedDict

from ..utils.extractor import extract_abstract, extract_introduction # Assuming these are in extractor.py

# Load PDFs
pages_1 = [page for page in PyPDFLoader("./research_paper_1.pdf").load_and_split()]
pages_2 = [page for page in PyPDFLoader("./research_paper_2.pdf").load_and_split()]
pages_3 = [page for page in PyPDFLoader("./research_paper_3.pdf").load_and_split()]

# Initialize the LLM
llm = ChatOllama(model="llama3.2:1b", temperature=0.1)

# Define the Report Pydantic model
class Report(BaseModel):
    problem_statement: str = Field(
        description="A detailed description of the research problem addressed by the paper, based on abstract and introduction, at least 40 words."
    )
    research_context: str = Field(
        description="The broader context and background of the research topic as presented in the introduction, explained in at least 40 words."
    )
    study_objectives: str = Field(
        description="The specific goals or aims of the study as outlined in the abstract and introduction, described in at least 40 words."
    )
    key_insights: str = Field(
        description="The main takeaways or findings highlighted in the abstract, providing insight into the paper’s contributions, written in at least 40 words."
    )
    research_significance: str = Field(
        description="The importance or potential impact of the study as inferred from the abstract and introduction, detailed in at least 40 words."
    )

augmented_llm = llm.with_structured_output(Report)
class AnalysisState(TypedDict):
    pages_1: List  # Pages for research_paper_1.pdf
    pages_2: List  # Pages for research_paper_2.pdf
    pages_3: List  # Pages for research_paper_3.pdf
    main_summary: Report  # Summary of research_paper_1.pdf
    summary_a: Report     # Summary of research_paper_2.pdf
    summary_b: Report     # Summary of research_paper_3.pdf
    final_response: str   # Final comparison response
    
analyzer_prompt = PromptTemplate(
    input_variables=["paper_content"],
    template="""
You are an expert at summarizing academic papers. Given the abstract and introduction of a research paper, analyze the content and provide a structured summary.

Here is the paper content:
{paper_content}

Return a JSON object with these fields, ALL AS STRINGS, each at least 40 words long:
- "problem_statement": Describe the research problem in detail.
- "research_context": Explain the broader context from the introduction.
- "study_objectives": State the goals of the study.
- "key_insights": Summarize the main findings or takeaways.
- "research_significance": Highlight the study's importance.

Return ONLY the JSON object, nothing else.
"""
)

comparison_prompt = PromptTemplate(
    input_variables=["main_summary", "summary_a", "summary_b"],
    template="""
You are an expert at comparing research summaries. Given three summaries of research papers (main_summary, summary_a, summary_b), compare main_summary with summary_a and main_summary with summary_b. For each comparison, analyze:
- Strengths of main_summary relative to the other.
- Weaknesses of main_summary relative to the other.
- Relevance of main_summary to the other’s research focus.

Summaries:
- Main Summary: {main_summary}
- Summary A: {summary_a}
- Summary B: {summary_b}

Generate a detailed text response (at least 200 words) with two sections:
1. "Comparison of Main Summary with Summary A"
2. "Comparison of Main Summary with Summary B"
Each section should cover strengths, weaknesses, and relevance. Return the response as a single string.
"""
)
def analyzer_1(state: AnalysisState) -> AnalysisState:
    pages = state["pages_1"]
    abstract = extract_abstract(pages)
    intro = extract_introduction(pages)
    paper_content = f"Abstract: {abstract}\n\nIntroduction: {intro}"
    
    response = augmented_llm.invoke(
        [
            SystemMessage(content=analyzer_prompt.format(paper_content=paper_content)),
            HumanMessage(content="Summarize the paper.")
        ]
    )
    return {"main_summary": response}

def analyzer_2(state: AnalysisState) -> AnalysisState:
    pages = state["pages_2"]
    abstract = extract_abstract(pages)
    intro = extract_introduction(pages)
    paper_content = f"Abstract: {abstract}\n\nIntroduction: {intro}"
    
    response = augmented_llm.invoke(
        [
            SystemMessage(content=analyzer_prompt.format(paper_content=paper_content)),
            HumanMessage(content="Summarize the paper.")
        ]
    )
    return {"summary_a": response}

def analyzer_3(state: AnalysisState) -> AnalysisState:
    pages = state["pages_3"]
    abstract = extract_abstract(pages)
    intro = extract_introduction(pages)
    paper_content = f"Abstract: {abstract}\n\nIntroduction: {intro}"
    
    response = augmented_llm.invoke(
        [
            SystemMessage(content=analyzer_prompt.format(paper_content=paper_content)),
            HumanMessage(content="Summarize the paper.")
        ]
    )
    return {"summary_b": response}

def compare_summaries(state: AnalysisState) -> AnalysisState:
    main_summary = state["main_summary"]
    summary_a = state["summary_a"]
    summary_b = state["summary_b"]
    
    # Convert Report objects to strings for prompt
    main_summary_str = str(main_summary.model_dump())
    summary_a_str = str(summary_a.model_dump())
    summary_b_str = str(summary_b.model_dump())
    
    response = llm.invoke(
        [
            SystemMessage(content=comparison_prompt.format(
                main_summary=main_summary_str,
                summary_a=summary_a_str,
                summary_b=summary_b_str
            )),
            HumanMessage(content="Compare the summaries.")
        ]
    ).content
    
    return {"final_response": response}

builder = StateGraph(AnalysisState)
builder.add_node("analyzer_1", analyzer_1)
builder.add_node("analyzer_2", analyzer_2)
builder.add_node("analyzer_3", analyzer_3)
builder.add_node("compare_summaries", compare_summaries)

builder.add_edge(START, "analyzer_1")
builder.add_edge(START, "analyzer_2")
builder.add_edge(START, "analyzer_3")

builder.add_edge("analyzer_1", "compare_summaries")
builder.add_edge("analyzer_2", "compare_summaries")
builder.add_edge("analyzer_3", "compare_summaries")

builder.add_edge("compare_summaries", END)
graph = builder.compile()

initial_state = {
    "pages_1": pages_1,
    "pages_2": pages_2,
    "pages_3": pages_3,
    "main_summary": None,
    "summary_a": None,
    "summary_b": None,
    "final_response": ""
}

def generate_comparison_report() -> str:
    """
    Invoke the LangGraph workflow and return the final comparison response.
    
    Returns:
        str: The final_response containing comparisons between main_summary and summary_a/b
    """
    response = graph.invoke(initial_state)
    return response["final_response"]

final_response = generate_comparison_report()
print("Final Comparison Response:")
print(final_response)