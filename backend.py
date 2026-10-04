import os
from dotenv import load_dotenv
import certifi

from typing import TypedDict, Annotated
import operator
import uuid

import psycopg
from psycopg.rows import dict_row

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.postgres import PostgresSaver
from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
    AIMessage,
    AnyMessage
)
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint

from tools.websearch_tool import search
from tools.flight_tool import search_flights

load_dotenv()

os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

def get_database_url():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL environment variable is not set.")
    
    if 'sslmode' not in database_url:
        seprator = '&' if '?' in database_url else '?'
        database_url = f"{database_url}{seprator}sslmode=require"
        
    return database_url

llm = ChatHuggingFace(
    llm=HuggingFaceEndpoint(
        repo_id="deepseek-ai/DeepSeek-R1",
        task="conversational",
        timeout=300,
    )
)

#state of the graph

class TripState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    user_query: str
    flight_result: str
    hotel_result: str
    itinerary: str
    llm_calls: int
    
def flight_agent(state: TripState):
    query = state['user_query']
    flight_data = search_flights(query)
    
    return {
        "flight_result": flight_data,
        "messages": [AIMessage(content=f"Flight data retrieved")],
        "llm_calls": state['llm_calls'] + 1
    }
    
def hotel_agent(state: TripState):
    query = f"Best hotels in {state['user_query']}"
    hotel_data = search(query)
    
    return {
        "hotel_result": hotel_data,
        "messages": [AIMessage(content=f"Hotel data retrieved")],
        "llm_calls": state['llm_calls'] + 1
    }
    
def itinerary_agent(state: TripState):
    prompt = f"""
Create a complete travel itinerary.

User Query:
{state['user_query']}

Flight Results:
{state['flight_result']}

Hotel Results:
{state['hotel_result']}

Make the itinerary practical, budget-aware, and easy to follow.
"""

    response = llm.invoke([
        SystemMessage(content="You are an expert travel planner."),
        HumanMessage(content=prompt)
    ])

    return {
        "itinerary": response.content,
        "messages": [response],
        "llm_calls": state.get("llm_calls", 0) + 1
    }
    
def final_agent(state: TripState):
    final_prompt = f"""
Generate the final travel response for the user.

User Request:
{state['user_query']}

Flights:
{state['flight_result']}

Hotels:
{state['hotel_result']}

Itinerary:
{state['itinerary']}

Format the final answer beautifully using these sections:

1. Trip Summary
2. Flight Information
3. Hotel Suggestions
4. Day-by-Day Itinerary
5. Estimated Budget
6. Final Recommendations

Important:
- Be clear and practical.
- Mention that live flight API may not provide ticket prices if pricing is unavailable.
- Keep the response useful for real travel planning.
"""

    response = llm.invoke([
        SystemMessage(content="You are a professional AI travel booking assistant. You will create a final travel response for the user based on their request, flight results, hotel results, and itinerary. Format the response clearly and practically."),
        HumanMessage(content=final_prompt)
    ])

    return {
        "messages": [response],
        "llm_calls": state.get("llm_calls", 0) + 1
    }
    
graph = StateGraph(TripState)

graph.add_node("flight_agent", flight_agent)
graph.add_node("hotel_agent", hotel_agent)
graph.add_node("itinerary_agent", itinerary_agent)
graph.add_node("final_agent", final_agent)

graph.add_edge(START, "flight_agent")
graph.add_edge("flight_agent", "hotel_agent")
graph.add_edge("hotel_agent", "itinerary_agent")
graph.add_edge("itinerary_agent", "final_agent")
graph.add_edge("final_agent", END)

DATABASE_URL = get_database_url()

_conn = psycopg.connect(
    DATABASE_URL,
    autocommit=True,
    row_factory=dict_row
)

checkpointer = PostgresSaver(_conn)
checkpointer.setup()

trip_graph = graph.compile(checkpointer=checkpointer)

def run_trip_planner(user_query: str, thread_id: str | None = None):
    
    if not thread_id:
        thread_id = f"user_{uuid.uuid4().hex}"
        
    config = {
        "configurable":{
            "thread_id": thread_id
        }
    }
    
    result = trip_graph.invoke(
        {
            "messages": [HumanMessage(content=user_query)],
            "user_query": user_query,
            "flight_result": "",
            "hotel_result": "",
            "itinerary": "",
            "llm_calls": 0
        },
        config=config
    )
    
    final_response = result['messages'][-1].content
    
    return {
        "thread_id": thread_id,
        "answer": final_response,
        "flight_results": result.get("flight_results", ""),
        "hotel_results": result.get("hotel_results", ""),
        "itinerary": result.get("itinerary", ""),
        "llm_calls": result.get("llm_calls", 0),
    }
    