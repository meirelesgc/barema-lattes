import os

from barema.services.queries import (
    fat_articles,
    fat_books,
    fat_cultivar,
    fat_patent,
    fat_software,
)


def report_production_csv():
    output_dir = "data/csv"
    os.makedirs(output_dir, exist_ok=True)

    reports_to_process = [
        ("fat_articles", fat_articles),
        ("fat_books", fat_books),
        ("fat_software", fat_software),
        ("fat_patent", fat_patent),
        ("fat_cultivar", fat_cultivar),
    ]

    for filename, get_func in reports_to_process:
        print(f"Processando {filename}...")

        df = get_func()

        csv_path = f"{output_dir}/{filename}.csv"
        xlsx_path = f"{output_dir}/{filename}.xlsx"

        df.write_csv(csv_path)
        df.write_excel(xlsx_path)

        print(f"Salvo: {csv_path} e {xlsx_path}")
