from dotenv import load_dotenv

from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.markdown import Markdown


# ============================================================
# Environment Setup
# ============================================================

load_dotenv()


# ============================================================
# Rich Console
# ============================================================

console = Console()


# ============================================================
# Tavily Search Tool
# ============================================================

search_tool = TavilySearchResults(
    max_results=5
)


# ============================================================
# Mistral LLM
# ============================================================

llm = ChatMistralAI(
    model="mistral-small-2603"
)


# ============================================================
# Prompt Template
# ============================================================

prompt = ChatPromptTemplate.from_template(
    """
You are a helpful AI news assistant.

Summarize the following news into clear and concise
bullet points.

Do not use markdown headings.

News:
{news}
"""
)


# ============================================================
# LangChain Pipeline
# ============================================================

chain = prompt | llm | StrOutputParser()


# ============================================================
# Search Latest AI News
# ============================================================

console.print()

console.print(
    Rule("[bold cyan]🌐 AI NEWS ASSISTANT[/bold cyan]")
)

console.print()

console.print(
    "[yellow]🔎 Searching for the latest AI news...[/yellow]"
)

news_result = search_tool.invoke(
    "Latest AI news"
)


# ============================================================
# Generate Summary
# ============================================================

console.print(
    "[yellow]🤖 Mistral is summarizing the results...[/yellow]"
)

result = chain.invoke(
    {
        "news": news_result
    }
)


# ============================================================
# Display Result
# ============================================================

console.print()

console.print(
    Panel(
        Markdown(result),
        title="[bold green]📰 Latest AI News[/bold green]",
        subtitle="[dim]Powered by Tavily + Mistral[/dim]",
        border_style="green",
        padding=(1, 2),
    )
)

console.print()

console.print(
    Rule("[bold magenta]✨ News Summary Complete[/bold magenta]")
)

console.print()

print(search_tool.name)
print(search_tool.description)
print(search_tool.args)