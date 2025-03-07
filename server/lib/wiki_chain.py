from ..models.models import llm
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, BaseMessage
from langgraph.graph import StateGraph, START, END, add_messages
from langgraph.prebuilt import ToolNode
from ..lib.explorer import explore
from typing import TypedDict, Annotated, Sequence
from pydantic import BaseModel, Field

class WikiResponse(BaseModel):
    topic: str = Field(description="The topic of discussion")
    content: str = Field(description="Structured explaination of the content regarding the topic")
    metadata: str = Field(description="Additional Metadata surrounding the content and data retrieved from the wikipedia pages")

class WikiState(TypedDict):
    query: str
    final_response: WikiResponse
    messages: Annotated[Sequence[BaseMessage], add_messages]

tools = [explore]
llm_augmented = llm.with_structured_output(WikiResponse)
llm_with_tools = llm.bind_tools(tools)

tool_node = ToolNode(tools=tools)

def wiki_llm_node(state: WikiState):
    response = llm_with_tools.invoke(
        [
            SystemMessage(content="You are an AI agent capable of using tools to fetch relevant information about a user's search query, remember to include information about the topic, content and metadata in the explaination."),
        ] + state["messages"]
    )
    return {"messages": [response]}

def wiki_refine_response(state: WikiState):
    final_message = state['messages'][-1]
    refined_response = llm_augmented.invoke(
        [
            SystemMessage(content="Based on the given content, structure the content into a JSON object containing the topic, content and metadata. Make that the content of the response contains the same amount of data as the input"),
            HumanMessage(content=final_message.content)
        ]
    )
    return {"final_response": refined_response, "messages": state["messages"]}

def route_from_llm(state: WikiState):
    last_message = state["messages"][-1]
    
    if isinstance(last_message, AIMessage) and hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tool_node"
    elif isinstance(last_message, AIMessage):
        return "wiki_refine_response"
    else:
        return "END"
    

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

result = graph.stream(
    {
        "messages": [HumanMessage(content="What are electrons")]
    },
    stream_mode="values"
)

final_state = None

for s in result:
    final_state = s
    if "messages" in s and s["messages"]:
        message = s["messages"][-1]
        message.pretty_print()

if final_state and "final_response" in final_state and final_state["final_response"]:
    print(final_state["final_response"])
else:
    print("No explaination generated")

def wiki_chain(query: str):
    pass