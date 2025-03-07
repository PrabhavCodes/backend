from models.models import llm
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, BaseMessage
from langgraph.graph import StateGraph, START, END, add_messages
from langgraph.prebuilt import ToolNode
from lib.explorer import explore
from typing import TypedDict, Annotated, Sequence
from pydantic import BaseModel, Field

# Define the structured response model
class WikiResponse(BaseModel):
    topic: str = Field(description="The topic of discussion")
    content: str = Field(description="Structured explanation of the content regarding the topic, preserving all details from the input")
    metadata: str = Field(description="Additional metadata surrounding the content and data retrieved from sources")

# Define the state
class WikiState(TypedDict):
    query: str
    final_response: WikiResponse
    messages: Annotated[Sequence[BaseMessage], add_messages]

# Tools and LLM setup
tools = [explore]
llm_augmented = llm.with_structured_output(WikiResponse)
llm_with_tools = llm.bind_tools(tools)

tool_node = ToolNode(tools=tools)

# Wiki LLM node
def wiki_llm_node(state: WikiState):
    response = llm_with_tools.invoke(
        [
            SystemMessage(content="You are an AI agent capable of using tools to fetch relevant information about a user's search query. Provide a detailed explanation including the topic, content, and metadata."),
        ] + state["messages"]
    )
    return {"messages": [response]}

# Refine response node
def wiki_refine_response(state: WikiState):
    final_message = state['messages'][-1]
    
    # Instruction to preserve all data and optionally format as Markdown
    system_prompt = """
    Based on the given content, structure it into a JSON object with fields 'topic', 'content', and 'metadata'. 
    Ensure the 'content' field retains ALL details from the input without summarizing or omitting anything. 
    If the input appears to be in Markdown, preserve its formatting; otherwise, format the content as Markdown for readability.
    """
    
    refined_response = llm_augmented.invoke(
        [
            SystemMessage(content=system_prompt),
            HumanMessage(content=final_message.content)
        ]
    )
    return {"final_response": refined_response, "messages": state["messages"]}

# Routing logic
def route_from_llm(state: WikiState):
    last_message = state["messages"][-1]
    if isinstance(last_message, AIMessage) and hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tool_node"
    elif isinstance(last_message, AIMessage):
        return "wiki_refine_response"
    else:
        return "END"

# Build the graph
builder = StateGraph(WikiState)
builder.add_node("wiki_llm_node", wiki_llm_node)
builder.add_node("tool_node", tool_node)
builder.add_node("wiki_refine_response", wiki_refine_response)
builder.add_edge(START, "wiki_llm_node")

builder.add_conditional_edges(
    "wiki_llm_node",
    route_from_llm,
    {
        "tool_node": "tool_node",
        "wiki_refine_response": "wiki_refine_response",
        "END": END
    }
)
builder.add_edge("tool_node", "wiki_llm_node")
builder.add_edge("wiki_refine_response", END)

graph = builder.compile()

# Execute the graph
# result = graph.stream(
#     {
#         "query": "What are electrons",
#         "messages": [HumanMessage(content="French Revolution")]
#     },
#     stream_mode="values"
# )

# final_state = None
# for s in result:
#     final_state = s
    # Optional: Print intermediate states for debugging
    # if "messages" in s and s["messages"]:
    #     message = s["messages"][-1]
    #     message.pretty_print()

# Output the final response
# if final_state and "final_response" in final_state and final_state["final_response"]:
#     response = final_state["final_response"]
#     print(f"Topic: {response.topic}")
#     print(f"Content:\n{response.content}")
#     print(f"Metadata: {response.metadata}")
# else:
#     print("No explanation generated")

# Optional wiki_chain function
def wiki_chain(query: str):
    result = graph.stream(
        {
            "query": query,
            "messages": [HumanMessage(content=query)]
        },
        stream_mode="values"
    )
    final_state = None
    for s in result:
        final_state = s
    if final_state and "final_response" in final_state and final_state["final_response"]:
        return final_state["final_response"]
    return None
