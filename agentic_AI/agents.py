
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

import os
import requests  # Used to send HTTP requests to online APIs

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


# ============================================================
# Create Tool Dictionary
# ============================================================

# Store tools in a dictionary so that we can
# find and execute a tool using its name.
tools = {
    "get_weather": get_weather,
    "get_news": get_news
}


# ============================================================
# Bind Tools to LLM
# ============================================================

# Tell the LLM which tools are available
llm_with_tools = llm.bind_tools(
    [get_weather, get_news]
)


# ============================================================
# Agent Loop
# ============================================================

# Store conversation history
messages = []


print("\n" + "=" * 60)
print("[bold cyan]🌐 CITY INTELLIGENCE SYSTEM[/bold cyan]")
print("=" * 60)

print("[dim]Ask about weather or latest news.[/dim]")
print("[dim]Type 'exit' to quit.[/dim]\n")


while True:

    # Get input from the user
    user_input = input("[bold yellow]You:[/bold yellow] ")

    # Exit the program
    if user_input.lower() == "exit":
        print("\n[bold red]Goodbye! 👋[/bold red]")
        break

    # Add user message to conversation history
    messages.append(
        HumanMessage(content=user_input)
    )


    # ========================================================
    # Inner Agent Loop
    # ========================================================

    while True:

        # Send conversation to LLM
        result = llm_with_tools.invoke(messages)

        # Add LLM response to conversation history
        messages.append(result)


        # ====================================================
        # If LLM does NOT request a tool
        # ====================================================

        if not result.tool_calls:

            print(
                f"\n[bold green]🤖 Assistant:[/bold green] "
                f"{result.content}\n"
            )

            # Finish this user's request
            break


        # ====================================================
        # If LLM requests one or more tools
        # ====================================================

        for tool_call in result.tool_calls:

            # Get tool name
            tool_name = tool_call["name"]

            # Get arguments generated by the LLM
            tool_args = tool_call["args"]

            print(
                f"\n[bold magenta]🔧 Tool requested:[/bold magenta] "
                f"{tool_name}"
            )

            print(
                f"[dim]Arguments: {tool_args}[/dim]"
            )


            # =================================================
            # Human-in-the-loop
            # =================================================

            confirm = input(
                "[bold yellow]Approve tool call? (yes/no):[/bold yellow] "
            )


            # =================================================
            # Tool call denied
            # =================================================

            if confirm.lower() != "yes":

                print(
                    "[bold red]❌ Tool call denied.[/bold red]\n"
                )

                tool_result = (
                    "The user denied permission to execute this tool."
                )


            # =================================================
            # Tool call approved
            # =================================================

            else:

                print(
                    "[bold green]✅ Tool call approved.[/bold green]"
                )

                # Execute the requested tool
                tool_result = tools[tool_name].invoke(
                    tool_args
                )


            # =================================================
            # Send tool result back to LLM
            # =================================================

            messages.append(
                ToolMessage(
                    content=str(tool_result),
                    tool_call_id=tool_call["id"]
                )
            )

