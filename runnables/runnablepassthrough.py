from dotenv import load_dotenv

from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import (
    RunnableLambda,
    RunnableParallel,
    RunnablePassthrough,
)

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
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
# Model & Parser
# ============================================================

model = ChatMistralAI(
    model="mistral-small-2603"
)

parser = StrOutputParser()


# ============================================================
# Code Generation Prompt
# ============================================================

code_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a code generator."),
        ("human", "{topic}"),
    ]
)


# ============================================================
# Code Explanation Prompt
# ============================================================

explain_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful assistant who explains "
            "code in simple terms.Don't use markdown only use bullets",
        ),
        (
            "human",
            "Explain the following code in simple words:\n{code}",
        ),
    ]
)


# ============================================================
# Step 1: Generate Code
# ============================================================

seq = code_prompt | model | parser


# ============================================================
# Step 2: Run in Parallel
# ============================================================

seq2 = RunnableParallel(
    {
        "generated_code": RunnablePassthrough(),
        "explanation": explain_prompt | model | parser,
    }
)


# ============================================================
# Complete Chain
# ============================================================

chain = seq | seq2


# ============================================================
# Invoke Chain
# ============================================================

response = chain.invoke(
    {
        "topic": "Write a code of palindrome in Python"
    }
)


# ============================================================
# Beautiful Output
# ============================================================

console.print()

console.print(
    Rule(
        "[bold cyan]🤖 LangChain Code Generator[/bold cyan]"
    )
)

console.print()

# Generated Code
console.print(
    Panel(
        Syntax(
            response["generated_code"],
            "python",
            theme="monokai",
            line_numbers=True,
            word_wrap=True,
        ),
        title="[bold green]💻 Generated Python Code[/bold green]",
        border_style="green",
        padding=(1, 2),
    )
)

console.print()

# Explanation
console.print(
    Panel(
        response["explanation"],
        title="[bold yellow]📖 Code Explanation[/bold yellow]",
        border_style="yellow",
        padding=(1, 2),
    )
)

console.print()

console.print(
    Rule("[bold magenta]✨ Generation Complete[/bold magenta]")
)

console.print()