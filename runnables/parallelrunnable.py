from dotenv import load_dotenv

from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel, RunnableLambda

from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule


# ============================================================
# Environment
# ============================================================

load_dotenv()


# ============================================================
# Rich Console
# ============================================================

console = Console()


# ============================================================
# Model & Output Parser
# ============================================================

model = ChatMistralAI(
    model="mistral-small-2603"
)

parser = StrOutputParser()


# ============================================================
# Two Different Prompts
# ============================================================

short_prompt = ChatPromptTemplate.from_template(
    "Explain {topic} in 10 lines. And don't use markdown"
)

detail_prompt = ChatPromptTemplate.from_template(
    "Explain {topic} in detail. And don't use markdown"
)


# ============================================================
# Input
# ============================================================

topic = "Machine Learning"


# ============================================================
# RunnableParallel
# ============================================================

runnable = RunnableParallel(
    {
        "short": RunnableLambda(lambda x : x['short']) | short_prompt | model | parser,
        "detail": RunnableLambda(lambda x : x['detail']) | detail_prompt | model | parser,
    }
)


# ============================================================
# Invoke
# ============================================================

console.print("\n[bold cyan]Running RunnableParallel...[/bold cyan]\n")

response = runnable.invoke({"short":{"topic": "Machine Learning"},"detail":{"topic":"Deep Learning"}})


# ============================================================
# Display Results
# ============================================================

console.print(
    Panel(
        response["short"],
        title="Short Explanation",
        border_style="green",
        padding=(1, 2),
    )
)

console.print(
    Panel(
        response["detail"],
        title="Detailed Explanation",
        border_style="blue",
        padding=(1, 2),
    )
)

console.print(
    Rule("[bold magenta]Done[/bold magenta]")
)