# ============================================================
# CITY INTELLIGENCE AGENT
# ============================================================
#
# This file contains:
#
# 1. Weather tool
# 2. News tool
# 3. Mistral LLM
# 4. LangChain Agent
# 5. Input Runnable
# 6. Output Runnable
# 7. Markdown cleanup
# 8. Runnable Chain
# 9. run_agent() function for FastAPI
#
# ============================================================


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

from dotenv import load_dotenv

load_dotenv()


# ============================================================
# IMPORT LIBRARIES
# ============================================================

import os
import re
import requests

from langchain.agents import create_agent
from langchain_mistralai import ChatMistralAI
from langchain.tools import tool
from langchain_core.runnables import RunnableLambda

from tavily import TavilyClient


# ============================================================
# WEATHER TOOL
# ============================================================

@tool
def get_weather(city: str) -> str:
    """
    Get the current weather of a city.
    """

    # --------------------------------------------------------
    # Get OpenWeather API key
    # --------------------------------------------------------

    api_key = os.getenv(
        "OPENWEATHER_API_KEY"
    )

    if not api_key:

        return (
            "⚠️ Weather Service\n\n"
            "OpenWeather API key is not configured."
        )


    # --------------------------------------------------------
    # OpenWeather API URL
    # --------------------------------------------------------

    url = (
        "https://api.openweathermap.org/data/2.5/weather"
        f"?q={city}&appid={api_key}&units=metric"
    )


    # --------------------------------------------------------
    # Send request
    # --------------------------------------------------------

    try:

        response = requests.get(
            url,
            timeout=10
        )

    except requests.RequestException as e:

        return (
            "⚠️ Weather Error\n\n"
            f"Unable to fetch weather information: {e}"
        )


    # --------------------------------------------------------
    # Convert response to JSON
    # --------------------------------------------------------

    try:

        data = response.json()

    except ValueError:

        return (
            "⚠️ Weather Error\n\n"
            "Invalid response received from weather service."
        )


    # --------------------------------------------------------
    # Check response
    # --------------------------------------------------------

    if response.status_code != 200:

        return (
            "⚠️ Weather Error\n\n"
            f"{data.get('message', 'Something went wrong')}"
        )


    # --------------------------------------------------------
    # Extract weather information
    # --------------------------------------------------------

    try:

        temperature = data["main"]["temp"]

        feels_like = data["main"]["feels_like"]

        humidity = data["main"]["humidity"]

        description = data["weather"][0]["description"]

        wind_speed = data["wind"]["speed"]

    except (KeyError, IndexError, TypeError):

        return (
            "⚠️ Weather Error\n\n"
            "Weather data could not be read correctly."
        )


    # --------------------------------------------------------
    # Return clean weather information
    # --------------------------------------------------------

    return (
        f"🌤️ Weather in {city.title()}\n\n"

        f"🌡️ Temperature: {temperature} °C\n"
        f"🌡️ Feels like: {feels_like} °C\n"
        f"☁️ Condition: {description.title()}\n"
        f"💧 Humidity: {humidity}%\n"
        f"💨 Wind speed: {wind_speed} m/s"
    )


# ============================================================
# TAVILY CLIENT
# ============================================================

tavily_api_key = os.getenv(
    "TAVILY_API_KEY"
)


if tavily_api_key:

    tavily_client = TavilyClient(
        api_key=tavily_api_key
    )

else:

    tavily_client = None


# ============================================================
# NEWS TOOL
# ============================================================

@tool
def get_news(city: str) -> str:
    """
    Get the latest news about a city.
    """

    # --------------------------------------------------------
    # Check Tavily configuration
    # --------------------------------------------------------

    if tavily_client is None:

        return (
            "⚠️ News Service\n\n"
            "Tavily API key is not configured."
        )


    # --------------------------------------------------------
    # Create search query
    # --------------------------------------------------------

    query = f"latest news in {city}"


    # --------------------------------------------------------
    # Search using Tavily
    # --------------------------------------------------------

    try:

        response = tavily_client.search(
            query=query,
            search_depth="basic",
            max_results=5
        )

    except Exception as e:

        return (
            "⚠️ News Error\n\n"
            f"Unable to fetch news: {e}"
        )


    # --------------------------------------------------------
    # Get search results
    # --------------------------------------------------------

    results = response.get(
        "results",
        []
    )


    # --------------------------------------------------------
    # Check results
    # --------------------------------------------------------

    if not results:

        return (
            f"🗞️ Latest News in {city.title()}\n\n"
            "No recent news was found."
        )


    # --------------------------------------------------------
    # Format news
    # --------------------------------------------------------

    news_list = []


    for index, result in enumerate(
        results,
        start=1
    ):

        # ----------------------------------------------------
        # Article title
        # ----------------------------------------------------

        title = result.get(
            "title",
            "No title"
        )


        # ----------------------------------------------------
        # Article URL
        # ----------------------------------------------------

        url = result.get(
            "url",
            ""
        )


        # ----------------------------------------------------
        # Article content
        # ----------------------------------------------------

        snippet = result.get(
            "content",
            ""
        )


        # ----------------------------------------------------
        # Clean snippet
        # ----------------------------------------------------

        snippet = snippet.strip()


        # Limit description

        if len(snippet) > 350:

            snippet = snippet[:350].rstrip() + "..."


        # ----------------------------------------------------
        # Create article
        # ----------------------------------------------------

        article = (
            f"📰 {index}. {title}\n\n"
            f"{snippet}\n\n"
            f"🔗 Source: {url}"
        )


        news_list.append(
            article
        )


    # --------------------------------------------------------
    # Return news
    # --------------------------------------------------------

    return (
        f"🗞️ Latest News in {city.title()}\n\n"
        + "\n\n".join(news_list)
    )


# ============================================================
# CREATE MISTRAL LLM
# ============================================================

llm = ChatMistralAI(

    model="mistral-small-2603",

    temperature=0
)


# ============================================================
# CREATE LANGCHAIN AGENT
# ============================================================

agent = create_agent(

    model=llm,

    tools=[
        get_weather,
        get_news
    ],

    system_prompt=(
        "You are a helpful City Intelligence Assistant.\n\n"

        "You can provide current weather information "
        "and latest news about cities.\n\n"

        "Use the available tools whenever the user's "
        "question requires current information.\n\n"

        "Do not use a tool when it is unnecessary.\n\n"

        "IMPORTANT RESPONSE RULES:\n\n"

        "1. Do not use Markdown formatting.\n"

        "2. Do not use #, ##, ### or other Markdown headings.\n"

        "3. Do not use ** for bold text.\n"

        "4. Do not use Markdown tables.\n"

        "5. Do not use Markdown links.\n"

        "6. Do not use horizontal rules such as ---.\n"

        "7. Use simple text with clean line breaks.\n"

        "8. You may use emojis.\n"

        "9. Keep answers concise and easy to read.\n\n"

        "For weather, prefer this format:\n\n"

        "🌤️ Weather in City\n\n"
        "🌡️ Temperature: XX °C\n"
        "🌡️ Feels like: XX °C\n"
        "☁️ Condition: Clear Sky\n"
        "💧 Humidity: XX%\n"
        "💨 Wind speed: XX m/s\n\n"

        "For news, prefer this format:\n\n"

        "🗞️ Latest News in City\n\n"
        "📰 1. News title\n\n"
        "Short description.\n\n"
        "🔗 Source: URL\n\n"

        "Never mention internal tools or tool calls."
    )
)


# ============================================================
# INPUT RUNNABLE
# ============================================================

def prepare_input(user_input: str):
    """
    Clean the user's input and convert it into
    the message format expected by the agent.
    """

    # Remove leading/trailing spaces

    user_input = user_input.strip()


    # Replace multiple spaces with one space

    user_input = " ".join(
        user_input.split()
    )


    # Return agent input

    return {

        "messages": [

            {
                "role": "user",
                "content": user_input
            }

        ]

    }


# ------------------------------------------------------------
# Convert function into Runnable
# ------------------------------------------------------------

input_runnable = RunnableLambda(
    prepare_input
)


# ============================================================
# CLEAN AI RESPONSE
# ============================================================

def clean_ai_response(text: str) -> str:
    """
    Remove unwanted Markdown formatting from
    the final AI response.
    """

    # --------------------------------------------------------
    # Remove Markdown headings
    #
    # ### Delhi News
    #
    # becomes:
    #
    # Delhi News
    # --------------------------------------------------------

    text = re.sub(
        r"^\s*#{1,6}\s*",
        "",
        text,
        flags=re.MULTILINE
    )


    # --------------------------------------------------------
    # Remove bold formatting
    #
    # **Delhi**
    #
    # becomes:
    #
    # Delhi
    # --------------------------------------------------------

    text = re.sub(
        r"\*\*(.*?)\*\*",
        r"\1",
        text,
        flags=re.DOTALL
    )


    # --------------------------------------------------------
    # Remove italic formatting
    #
    # *Delhi*
    #
    # becomes:
    #
    # Delhi
    # --------------------------------------------------------

    text = re.sub(
        r"(?<!\*)\*([^*\n]+)\*(?!\*)",
        r"\1",
        text
    )


    # --------------------------------------------------------
    # Convert Markdown links
    #
    # [Read more](https://example.com)
    #
    # becomes:
    #
    # 🔗 Read more: https://example.com
    # --------------------------------------------------------

    text = re.sub(
        r"\[([^\]]+)\]\((https?://[^)]+)\)",
        r"🔗 \1: \2",
        text
    )


    # --------------------------------------------------------
    # Remove horizontal rules
    #
    # ---
    # ***
    # ___
    # --------------------------------------------------------

    text = re.sub(
        r"^\s*(---+|\*\*\*+|___+)\s*$",
        "",
        text,
        flags=re.MULTILINE
    )


    # --------------------------------------------------------
    # Convert Markdown bullet points
    #
    # - item
    #
    # becomes:
    #
    # • item
    # --------------------------------------------------------

    text = re.sub(
        r"^\s*[-*]\s+",
        "• ",
        text,
        flags=re.MULTILINE
    )


    # --------------------------------------------------------
    # Remove code fences
    # --------------------------------------------------------

    text = text.replace(
        "```",
        ""
    )


    # --------------------------------------------------------
    # Remove inline backticks
    # --------------------------------------------------------

    text = text.replace(
        "`",
        ""
    )


    # --------------------------------------------------------
    # Clean excessive spaces
    # --------------------------------------------------------

    text = re.sub(
        r"[ \t]+",
        " ",
        text
    )


    # --------------------------------------------------------
    # Clean each line
    # --------------------------------------------------------

    lines = []

    for line in text.splitlines():

        line = line.strip()

        lines.append(line)


    # --------------------------------------------------------
    # Rebuild text
    # --------------------------------------------------------

    text = "\n".join(
        lines
    )


    # --------------------------------------------------------
    # Remove excessive blank lines
    # --------------------------------------------------------

    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text
    )


    # --------------------------------------------------------
    # Final cleanup
    # --------------------------------------------------------

    return text.strip()


# ============================================================
# OUTPUT RUNNABLE
# ============================================================

def extract_final_answer(result):
    """
    Extract the final AI response and clean
    unwanted Markdown formatting.
    """

    # Get final message

    final_message = result[
        "messages"
    ][-1]


    # Get content

    answer = final_message.content


    # --------------------------------------------------------
    # Some models can return structured content.
    # Convert it safely to text.
    # --------------------------------------------------------

    if not isinstance(answer, str):

        answer = str(answer)


    # --------------------------------------------------------
    # Clean Markdown
    # --------------------------------------------------------

    answer = clean_ai_response(
        answer
    )


    return answer


# ------------------------------------------------------------
# Convert function into Runnable
# ------------------------------------------------------------

output_runnable = RunnableLambda(
    extract_final_answer
)


# ============================================================
# BUILD RUNNABLE CHAIN
# ============================================================

agent_chain = (
    input_runnable
    | agent
    | output_runnable
)


# ============================================================
# FUNCTION USED BY FASTAPI
# ============================================================

def run_agent(user_input: str):
    """
    Run the complete Runnable chain.
    """

    final_answer = agent_chain.invoke(
        user_input
    )

    return final_answer