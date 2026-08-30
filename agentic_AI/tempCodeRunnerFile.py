
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

import os
import requests  # Used to send HTTP requests to online APIs

from langchain.agents import create_agent
from langchain_mistralai import ChatMistralAI
from langchain.tools import tool
from langchain_core.messages import HumanMessage, ToolMessage

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

    # Get OpenWeather API key from the .env file
    API_KEY = os.getenv("OPENWEATHER_API_KEY")

    # OpenWeather API URL
    url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?q={city}&appid={API_KEY}&units=metric"
    )

    # Send GET request to OpenWeather API
    response = requests.get(url)

    # Convert API response to Python dictionary
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

# Create Tavily client using API key from .env
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

    # Search for latest news using Tavily
    response = tavily_client.search(
        query=query,
        search_depth="basic",
        max_results=5
    )

    # Get search results
    results = response.get("results", [])

    # Check if no results were found
    if not results:
        return f"No recent news found for {city}."

    # Store formatted news results
    news_list = []

    for r in results:

        # Extract title
        title = r.get("title", "No title")

        # Extract URL
        url = r.get("url", "")

        # Extract content/snippet
        snippet = r.get("content", "")

        # Add news article to the list
        news_list.append(
            f"{title}\n"
            f"{url}\n"
            f"{snippet[:200]}..."
        )

    # Return all news articles
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

#create agent with Langchain
agent = create_agent(
    llm, 
    tools = [get_weather, get_news],
    system_prompt = "You are a helpful city assistant."
)

print("City Agent | type exit to quit")
while True:
    user_input = input("You: ")
    if user_input.lower() == "exit":
        break
    result = agent.invoke(
         {"messages": [{"role": "user", "content": user_input}]}
    )
    print(result)



























































































