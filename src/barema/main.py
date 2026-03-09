from barema.core.generate_report import start_process
from barema.core.review_data import review_data
from barema.core.setup import setup_database
from barema.shell import TerminalMenu

if __name__ == "__main__":
    options = [
        ("Vizualizar dados - Desativado", review_data),
        ("Montar banco de dados", setup_database),
        ("Gerar relatório", start_process),
    ]

    menu = TerminalMenu(options)
    menu.run()
