from tools.websearch_tool import search
from tools.flight_tool import search_flights
from backend import run_trip_planner

user_input = input("Enter travel request: ")

response = run_trip_planner(
    user_query=user_input,
    thread_id="test_user"
)

print("\nFINAL RESPONSE:\n")
print(response["answer"])