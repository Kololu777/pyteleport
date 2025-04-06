from prompt_toolkit import prompt
from rich import print


def single_word_scanf(question: str = "Enter your input:") -> str:
    user_input = prompt(question)
    if len(user_input.split()) > 1:
        print("[bold red]Please enter a single word.[/bold red]")
        return single_word_scanf(question)
    return user_input