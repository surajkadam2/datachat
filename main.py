from rich.console import Console
from rich.table import Table
from rich import box
import os

from explainer import explain_results
from safety import is_input_safe
from prompt import ask_data_question
from db import run_query, get_schema
from logger import log_question, log_error
from config import APP_NAME, APP_VERSION, CLI_PROMPT

console = Console()

SYSTEM_COMMANDS = ['cls', 'clear', 'exit', 'help', 'explain', 'retry', 'edit']

def print_welcome():
    console.print(f"\n[bold cyan]💬 {APP_NAME}[/bold cyan] [green]{APP_VERSION}[/green]")
    console.print("[dim]Ask questions about your database in natural language[/dim]\n")

    console.print("[bold]Example questions:[/bold]")
    console.print("• How many customers are from Germany?")
    console.print("• Show top 10 orders by amount")
    console.print("• List customers who signed up last month\n")

    console.print("[yellow]Type 'help' to see available commands[/yellow]\n")


def print_help():
    console.print("\n[bold cyan]Available Commands:[/bold cyan]")
    console.print("• [green]exit[/green]    → Quit the application")
    console.print("• [green]help[/green]    → Show this help message")
    console.print("• [green]explain[/green] → Show last generated SQL + timing")
    console.print("• [green]retry[/green]   → Retry last question with feedback")
    console.print("• [green]edit[/green]    → Edit last question and re-run\n")


def display_results(rows, sql, gemini_time, execution_time):
    if not rows:
        console.print("[yellow]No results found.[/yellow]")
        return

    table = Table(box=box.MINIMAL_DOUBLE_HEAD)

    # Auto-detect columns
    columns = rows[0].keys()
    for col in columns:
        table.add_column(str(col), style="cyan", overflow="fold")

    # Add rows
    for row in rows:
        table.add_row(*[str(row[col]) for col in columns])

    console.print(table)

    # Footer info
    console.print(
        f"\n[dim]Rows: {len(rows)} | AI Time: {gemini_time:.2f}s | DB Time: {execution_time:.2f}s[/dim]"
    )


def main():
    print_welcome()

    schema = get_schema()

    last_question = None
    last_sql = None
    last_gemini_time = None
    last_execution_time = None

    history = []  # ✅ NEW: conversation memory

    while True:
        try:
            user_input = console.input(f"[bold blue]{CLI_PROMPT}:[/bold blue] ").strip()

            if not user_input:
                console.print("[yellow]Please ask a complete question.[/yellow]")
                continue

            # Commands
            if user_input.lower() == "exit":
                console.print("[bold red]Goodbye![/bold red]")
                break

            if user_input.lower() == "help":
                print_help()
                continue

            if user_input.lower() == "explain":
                if last_sql:
                    console.print(f"\n[cyan]Last SQL:[/cyan]\n{last_sql}")
                    console.print(
                        f"[dim]AI Time: {last_gemini_time:.2f}s | DB Time: {last_execution_time:.2f}s[/dim]\n"
                    )
                else:
                    console.print("[yellow]No previous query to explain.[/yellow]")
                continue

            if user_input.lower() == "edit":
                if not last_question:
                    console.print("[yellow]No previous question to edit.[/yellow]")
                    continue
                user_input = console.input(
                    f"[bold blue]Edit question ({last_question}):[/bold blue] "
                ).strip()
                if not user_input:
                    continue

            if user_input.lower() == "retry":
                if not last_question:
                    console.print("[yellow]No previous question to retry.[/yellow]")
                    continue
                feedback = console.input(
                    "[bold blue]What was wrong with the result?[/bold blue] "
                )
                user_input = f"{last_question}\nFix this issue: {feedback}"

            if user_input.lower() in ['cls', 'clear']:
                os.system('cls' if os.name == 'nt' else 'clear')
                continue  

            if len(user_input.strip().split()) < 2:
                console.print("[yellow]Please ask a complete question.[/yellow]")
                continue  

            # Safety check
            if not is_input_safe(user_input):
                console.print("[bold red]⚠ Unsafe input detected. Try again.[/bold red]")
                continue

            log_question(user_input)

            # Ask AI
            result = ask_data_question(user_input, schema, history)

            if not result["success"]:
                console.print(f"[bold red]Error:[/bold red] {result['error']}")
                continue

            # Catch NOT_A_DB_QUESTION signal BEFORE executing
            if result['sql'].strip().upper() == 'NOT_A_DB_QUESTION':
                console.print("[yellow]That doesn't look like a database question.[/yellow]")
                console.print("[yellow]Try: 'Show me top customers by revenue'[/yellow]")
                continue
            
          
            if result['sql'].strip().startswith('EXTRACTED:'):
                lines = result['sql'].strip().split('\n')
                print(f"DEBUG lines: {lines}")  # ← add this
                extracted = lines[0].replace('EXTRACTED:', '').strip()
                actual_sql = '\n'.join(lines[1:]).replace('SQL:', '').strip()
                print(f"DEBUG actual_sql: {actual_sql}")  # ← and this

                console.print(f"[yellow]⚠ We found a question in your input: '{extracted}'[/yellow]")
                console.print(f"[yellow]  Answering that for you...[/yellow]")

            sql = actual_sql if result['sql'].strip().startswith('EXTRACTED:') else result['sql']
            gemini_time = result["gemini_time"]

            # Run query
            db_result = run_query(sql)

            rows = db_result["rows"]
            execution_time = db_result["execution_time"]

            # Save state
            last_question = user_input
            last_sql = sql
            last_gemini_time = gemini_time
            last_execution_time = execution_time

            # ✅ Update history
            history.append({
                "question": user_input,
                "sql": sql
            })

            # ✅ Sliding window (max 5)
            if len(history) > 5:
                history.pop(0)

            # Display
            display_results(rows, sql, gemini_time, execution_time)

            # Add plain English explanation
            explanation = explain_results(
               question=user_input,
               rows=rows,
               sql=result['sql']
            )
            console.print(f"\n[green]💬 {explanation}[/green]\n")

        except Exception as e:
            log_error(str(e))
            #console.print(f"[bold red]Error:[/bold red] {str(e)}")
            console.print(f"[red]Query too slow: {e}[/red]")
            console.print("[yellow]Tip: Try a more specific question[/yellow]")
            continue  # ← loop continues, don't crash


if __name__ == "__main__":
    main()