
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

import os
import requests

from langchain.agents import create_agent
from langchain.agents.middleware import wrap_tool_call

from langchain_mistralai import ChatMistralAI
from langchain.tools import tool

from langchain_core.messages import ToolMessage
from langchain_core.runnables import RunnableLambda

from tavily import TavilyClient
from rich import print


# ============================================================
# Creating Tools
# ============================================================


# ------------------------------------------------------------
# Weather Tool
# ------------------------------------------------------------

@tool
def get_weather(city: str) -> str:
    """
    Get the current weather of a city.
    """

    # Get OpenWeather API key
    API_KEY = os.getenv("OPENWEATHER_API_KEY")

    # OpenWeather API URL
    url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?q={city}&appid={API_KEY}&units=metric"
    )

    # Send GET request to OpenWeather API
    response = requests.get(url)

    # Convert API response into Python dictionary
    data = response.json()

    # Check whether the API request was successful
    if response.status_code != 200:
        return f"Error: {data.get('message', 'Something went wrong')}"

    # Extract temperature
    temp = data["main"]["temp"]

    # Extract weather description
    desc = data["weather"][0]["description"]

    # Return weather information
    return f"Weather in {city}: {desc}, {temp} °C"


# ------------------------------------------------------------
# Tavily News Tool
# ------------------------------------------------------------

# Create Tavily client
tavily_client = TavilyClient(
    api_key=os.getenv("TAVILY_API_KEY")
)


@tool
def get_news(city: str) -> str:
    """
    Get the latest news about a city.
    """

    # Create search query
    query = f"latest news in {city}"

    # Search using Tavily
    response = tavily_client.search(
        query=query,
        search_depth="basic",
        max_results=5
    )

    # Get search results
    results = response.get("results", [])

    # Check whether results exist
    if not results:
        return f"No recent news found for {city}."

    # Store formatted news
    news_list = []

    for r in results:

        # Extract title
        title = r.get("title", "No title")

        # Extract URL
        url = r.get("url", "")

        # Extract article content
        snippet = r.get("content", "")

        news_list.append(
            f"{title}\n"
            f"{url}\n"
            f"{snippet[:200]}..."
        )

    # Return formatted news
    return (
        f"Latest news in {city}:\n\n"
        + "\n\n".join(news_list)
    )


# ============================================================
# Create LLM
# ============================================================

llm = ChatMistralAI(
    model="mistral-small-2603",
    temperature=0
)


# ============================================================
# Human Approval Middleware
# ============================================================

@wrap_tool_call
def human_approval(request, handler):
    """
    Ask for human approval before every tool call.
    """

    # Get tool name requested by the LLM
    tool_name = request.tool_call["name"]

    # Ask user for approval
    confirm = input(
        f"Agent wants to call '{tool_name}'. "
        "Approve? (yes/no): "
    )

    # If user denies the tool call
    if confirm.lower() != "yes":

        print("[bold red]❌ Tool call denied.[/bold red]")

        return ToolMessage(
            content="Tool call denied by user.",
            tool_call_id=request.tool_call["id"]
        )

    # User approved the tool
    print("[bold green]✅ Tool call approved.[/bold green]")

    # Execute the tool
    return handler(request)


# ============================================================
# Create Agent
# ============================================================

agent = create_agent(
    model=llm,

    # Give the agent access to these tools
    tools=[
        get_weather,
        get_news
    ],

    # System instructions
    system_prompt=(
        "You are a helpful city assistant. "
        "Use the available tools when necessary."
    ),

    # Add human approval middleware
    middleware=[
        human_approval
    ]
)


# ============================================================
# Runnables
# ============================================================


# ------------------------------------------------------------
# Input Runnable
# ------------------------------------------------------------

def prepare_input(user_input: str):
    """
    Prepare and clean user input before sending it
    to the agent.
    """

    # Remove unnecessary spaces
    user_input = user_input.strip()

    # Convert multiple spaces into a single space
    user_input = " ".join(user_input.split())

    return {
        "messages": [
            {
                "role": "user",
                "content": user_input
            }
        ]
    }


# Convert the Python function into a Runnable
input_runnable = RunnableLambda(prepare_input)


# ------------------------------------------------------------
# Output Runnable
# ------------------------------------------------------------

def extract_final_answer(result):
    """
    Extract only the final message from the agent result.
    """

    # Get the last message
    final_message = result["messages"][-1]

    # Return only its content
    return final_message.content


# Convert the function into a Runnable
output_runnable = RunnableLambda(extract_final_answer)


# ============================================================
# Build Runnable Chain
# ============================================================

# Runnable flow:
#
# User input
#     ↓
# input_runnable
#     ↓
# Agent
#     ↓
# output_runnable
#     ↓
# Final answer
#
agent_chain = (
    input_runnable
    | agent
    | output_runnable
)


# ============================================================
# Chat Interface
# ============================================================

print("\n[bold cyan]🌐 CITY INTELLIGENCE AGENT[/bold cyan]")
print("[dim]Ask about weather, news, and city information.[/dim]")
print("[dim]Type 'exit' to quit.[/dim]\n")


while True:

    # Get user input
    user_input = input("You: ")

    # Exit program
    if user_input.lower() == "exit":
        print("[bold red]Goodbye! 👋[/bold red]")
        break

    # Run the complete Runnable chain
    final_answer = agent_chain.invoke(user_input)

    # Display final answer
    print(
        f"\n[bold green]🤖 Assistant:[/bold green] "
        f"{final_answer}\n"
    )

