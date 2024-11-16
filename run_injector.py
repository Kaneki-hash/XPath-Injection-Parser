from xpath_injector import XPathInjector, AutomatedInjector
import argparse
import logging
from rich.console import Console
from rich.progress import Progress
from rich import print as rprint

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        filename='injection_results.log'
    )

def main():
    parser = argparse.ArgumentParser(description='XPath Injection Framework')
    parser.add_argument('--url', required=True, help='Target URL')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--output', '-o', help='Output file for results')
    args = parser.parse_args()

    console = Console()
    setup_logging()

    console.print("[bold blue]XPath Injection Framework[/bold blue]")
    console.print(f"[yellow]Target URL:[/yellow] {args.url}")

    try:
        with Progress() as progress:
            task = progress.add_task("[cyan]Running injection tests...", total=100)
            
            # Инициализация инжектора
            injector = XPathInjector(args.url)
            automated = AutomatedInjector(injector)
            
            # Запуск тестирования
            console.print("\n[green]Starting injection campaign...[/green]")
            automated.run_campaign()
            
            # Генерация отчета
            report = automated.generate_report()
            
            progress.update(task, completed=100)

        # Вывод результатов
        console.print("\n[bold green]Results:[/bold green]")
        console.print(f"Total attempts: {report['total_attempts']}")
        console.print(f"Successful attempts: {report['successful_attempts']}")
        console.print(f"Success rate: {report['success_rate']:.2%}")

        if report['vulnerable_types']:
            console.print("\n[bold red]Vulnerabilities found:[/bold red]")
            for vuln_type in report['vulnerable_types']:
                console.print(f"- {vuln_type.value}")

        if report['extracted_data']:
            console.print("\n[bold yellow]Extracted data:[/bold yellow]")
            for data in report['extracted_data']:
                console.print(f"- {data}")

        # Сохранение результатов в файл
        if args.output:
            with open(args.output, 'w') as f:
                f.write(str(report))
            console.print(f"\n[green]Results saved to {args.output}[/green]")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        logging.error(f"Error during execution: {str(e)}")
        return 1

    return 0

if __name__ == "__main__":
    exit(main())
