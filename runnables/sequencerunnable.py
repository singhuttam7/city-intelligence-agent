from dotenv import load_dotenv

from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule


# ============================================================
# Environment Setup
# ============================================================

load_dotenv()


# ============================================================
# Rich Console
# ============================================================

console = Console()


# ============================================================
# 1. Prompt Template
# ============================================================

prompt = ChatPromptTemplate.from_template(
    "Explain {topic} in simple words. And don't use markdowns"
)


# ============================================================
# 2. Model
# ============================================================

model = ChatMistralAI(
    model="mistral-small-2603"
)


# ============================================================
# 3. Output Parser
# ============================================================

parser = StrOutputParser()


# ============================================================
# Manual Step-by-Step Flow
# ============================================================

"""
formatted_prompt = prompt.format_messages(
    topic="Machine Learning"
)

# Call the model manually
response = model.invoke(formatted_prompt)

# Parse the output manually
final_output = parser.parse(response.content)

print(final_output)
"""


# ============================================================
# Sequential Runnable
# ============================================================

chain = prompt | model | parser


# ============================================================
# Invoke Chain
# ============================================================

result = chain.invoke(
    {
        "topic": "Machine Learning"
    }
)


# ============================================================
# Display Result
# ============================================================

console.print()
console.print(
    Rule("[bold cyan]LangChain Runnable Sequence[/bold cyan]")
)

console.print(
    Panel(
        result,
        title="[bold green]Machine Learning[/bold green]",
        border_style="green",
        padding=(1, 2),
    )
)

console.print()