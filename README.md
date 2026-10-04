# AI Travel Planner with LangGraph

A multi-agent travel planning system built with **LangGraph**, **FastAPI**, and **Hugging Face** models. This application creates complete travel itineraries by orchestrating specialized agents for flights, hotels, itinerary planning, and final response generation, served through a modern web interface.

## Features

- **Multi-Agent Architecture**: Sequential agents for flights, hotels, itinerary, and final response
- **Persistent State Management**: PostgreSQL-backed checkpointing for conversation threads
- **Production-Ready**: Observability & Tracing with LangSmith
- **LLM Integration**: Uses DeepSeek-R1 model via Hugging Face Inference API
- **Tool Integration**: Web search and flight search capabilities
- **Thread-Based Sessions**: Unique thread IDs for maintaining conversation context
- **Modern UI**: Responsive frontend with custom styling and interactive JavaScript

## Architecture

```
User Query → Flight Agent → Hotel Agent → Itinerary Agent → Final Agent → Response
                ↓              ↓              ↓                ↓
           Flight Data    Hotel Data    Itinerary Plan    Formatted Response
```

## Prerequisites

- Python 3.10+
- PostgreSQL database
- Hugging Face API token
- LangSmith API key (for tracing and monitoring)
- Required Python packages (see `requirements.txt`)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Shreshhthh/Multi-Agent--Trip-planner.git
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

Create a `.env` file in the project root:

```env
# Hugging Face API
HUGGINGFACEHUB_API_TOKEN=your_huggingface_token_here

# Database Configuration
DATABASE_URL=postgresql://user:password@host:port/database_name

# Other Required API Keys
AVIATIONSTACK_API_KEY=your_aviationstack_key_here
TAVILY_API_KEY=your_tavily_key_here
LANGSMITH_API_KEY=your_langsmith_key_here
```

**Getting Your Hugging Face Token:**

1. Go to https://huggingface.co/settings/tokens
2. Create a new token with `read` permissions
3. Copy and paste it into your `.env` file

**Getting Your LangSmith API Key:**

1. Go to https://smith.langchain.com/settings
2. Create an API key
3. Add it to your `.env` file

**Getting Your Tavily API Key:**

1. Go to https://app.tavily.com/api-keys
2. Create a new API key
3. Add it to your `.env` file

**Getting Your AviationStack API Key:**

1. Go to https://aviationstack.com/
2. Sign up and get your API key
3. Add it to your `.env` file

## Project Structure

```
.
├── app.py                  # FastAPI application entry point & routes
├── backend.py              # LangGraph state graph & agent definitions
├── tools/
│   ├── __init__.py
│   ├── websearch_tool.py   # Web search functionality
│   └── flight_tool.py      # Flight search functionality
├── static/
│   ├── style.css           # Custom CSS styling
│   └── script.js           # Frontend JavaScript logic
├── templates/
│   └── index.html          # Main HTML template
├── .env                    # Environment variables (do not commit)
├── requirements.txt        # Python dependencies
└── README.md               # Documentation
```

## Usage

### Running the Application

```bash
python app.py
```

The FastAPI server will start at `http://localhost:8000`.

### API Endpoints

#### POST /plan-trip

Plan a complete trip with flights, hotels, and itinerary.

**Request:**

```json
{
  "query": "Plan a 3-day trip from Delhi to Goa in December under ₹30,000",
  "thread_id": "optional_custom_thread_id"
}
```

**Response:**

```json
{
  "thread_id": "user_a1b2c3d4e5f6",
  "answer": "Complete formatted travel response...",
  "flight_results": "Flight search results...",
  "hotel_results": "Hotel search results...",
  "itinerary": "Day-by-day itinerary...",
  "llm_calls": 4
}
```

#### GET /health

Health check endpoint.

**Response:**

```json
{
  "status": "healthy",
  "database": "connected"
}
```

## Configuration Details

### LangGraph State

The `TripState` maintains:

- `messages`: Conversation history with all agent responses
- `user_query`: Original user travel request
- `flight_result`: Flight search results
- `hotel_result`: Hotel search results
- `itinerary`: Generated day-by-day itinerary
- `llm_calls`: Counter for LLM API calls (useful for cost tracking)

### Agent Flow

1. **Flight Agent**: Calls `search_flights()` with user query
2. **Hotel Agent**: Searches for best hotels using web search
3. **Itinerary Agent**: Creates practical day-by-day plan using LLM
4. **Final Agent**: Formats complete response with all sections

## Requirements File

```txt
fastapi==0.109.0
uvicorn==0.27.0
langgraph==0.0.40
langchain-core==0.1.30
langchain-huggingface==0.0.3
python-dotenv==1.0.0
certifi==2024.2.2
psycopg==3.1.18
psycopg-binary==3.1.18
pydantic==2.5.3
httpx==0.26.0
huggingface-hub==0.20.3
jinja2==3.1.3
langsmith==0.1.0
tavily-python==0.3.0
```

## LangSmith Dashboard

Monitor and debug your travel planner with LangSmith observability:

- **Execution Traces**: Complete step-by-step execution of each trip planning request
- **Latency Metrics**: Time taken by each agent and LLM call
- **Token Usage**: Track LLM token consumption for cost analysis
- **Error Tracking**: Identify and debug failed requests

**Access your dashboard:** https://smith.langchain.com

---

**Built with** ❤️ **using LangGraph, FastAPI, and Hugging Face**
