import os
from datetime import datetime

import polars as pl
from tqdm import tqdm

from barema.services.ai_evaluation import evaluation
from barema.services.ai_extraction import extract_data
from barema.services.queries import (
    get_articles,
    get_assets_ip,
    get_books,
    get_cultivar,
    get_foment_level,
    get_guidance_postdoc,
    get_msc_completed,
    get_msc_ongoing,
    get_no_reg_software,
    get_other_technical_production,
    get_patents,
    get_phd_completed,
    get_phd_ongoing,
    get_phd_time,
    get_projects_with_companies,
    get_radio_or_tv_program,
    get_research_projects,
    get_research_report,
    get_researchers,
    get_scientific_projects,
    get_short_course_taught,
    get_social_media_website_blog,
    get_software,
)
from barema.services.report_utils import (
    add_evaluation_window,
    add_phd_level,
    merge_data,
    process_and_merge_production,
)

current_year = datetime.now().year


def researcher_profile_csv(base_year=current_year):
    researchers = get_researchers()
    print(f"Total de linhas (inicial): {researchers.height}")

    # Tempo doutorado
    phd_time = get_phd_time()
    researchers = merge_data(researchers, phd_time)
    print(f"Total de linhas (após phd_time): {researchers.height}")

    # Nivel do pesquisador
    phd_level = add_phd_level(phd_time)
    researchers = merge_data(researchers, phd_level)
    print(f"Total de linhas (após phd_level): {researchers.height}")

    # Bolsa
    foment_level = get_foment_level()
    researchers = merge_data(researchers, foment_level)
    print(f"Total de linhas (após foment_level): {researchers.height}")

    # Gerar CSV
    researchers.write_csv("data/csv/researcher_profile.csv")
    researchers.write_excel("data/csv/researcher_profile.xlsx")


def technological_production_and_innovation_csv(base_year=current_year):
    researchers = get_researchers()
    print(f"Total de linhas (inicial): {researchers.height}")

    # Bolsa
    foment_level = get_foment_level()
    researchers = merge_data(researchers, foment_level)
    print(f"Total de linhas (após foment_level): {researchers.height}")

    # 5 ou 10 Anos
    researchers = add_evaluation_window(researchers)
    print(f"Total de linhas (após add_evaluation_window): {researchers.height}")

    productions_to_process = [
        (get_articles, "total_articles"),
        (get_books, "total_books"),
        (get_software, "total_software"),
        (get_no_reg_software, "total_no_reg_software"),
        (get_patents, "total_patents"),
        (get_cultivar, "total_cultivar"),
        (get_assets_ip, "total_assets_ip"),
        (get_research_report, "total_research_report"),
        (get_short_course_taught, "total_short_course_taught"),
        (get_radio_or_tv_program, "total_radio_or_tv_program"),
        (get_social_media_website_blog, "total_social_media_website_blog"),
        (get_other_technical_production, "total_other_technical_production"),
    ]
    for get_func, col_name in productions_to_process:
        researchers = process_and_merge_production(
            researchers, get_func, col_name, base_year
        )
        print(f"Total de linhas (após {col_name}): {researchers.height}")

    # Gerar CSV
    researchers.write_csv("data/csv/technological_production_and_innovation.csv")
    researchers.write_excel("data/csv/technological_production_and_innovation.xlsx")


def transfer_of_technology_csv():
    def get_processed_ids(path):
        if not os.path.exists(path):
            return set()
        df = pl.read_csv(path, schema_overrides={"lattes_id": pl.String})
        return set(df["lattes_id"].to_list())

    researchers = get_researchers()
    print(f"Total de linhas (inicial): {researchers.height}")

    # Bolsa
    foment_level = get_foment_level()
    researchers = merge_data(researchers, foment_level)
    print(f"Total de linhas (após foment_level): {researchers.height}")

    # 5 ou 10 Anos
    researchers = add_evaluation_window(researchers)
    print(f"Total de linhas (após add_evaluation_window): {researchers.height}")

    researchers = researchers.with_columns(pl.col("lattes_id").cast(pl.String))

    output_path = "data/csv/transfer_of_technology.csv"
    processed = get_processed_ids(output_path)

    rows = list(researchers.iter_rows(named=True))

    for row in tqdm(
        rows, desc="Extraindo Transferência de Tecnologia", total=len(rows)
    ):
        lattes_id = str(row["lattes_id"])

        if lattes_id in processed:
            continue

        resultado = extract_data(lattes_id)

        linha = {**row, **resultado}

        df = pl.DataFrame([linha]).with_columns(pl.col("lattes_id").cast(pl.String))

        if not os.path.exists(output_path):
            df.write_csv(output_path)
        else:
            with open(output_path, "a", encoding="utf-8") as f:
                df.write_csv(f, include_header=False)

    if os.path.exists(output_path):
        df_final = pl.read_csv(output_path, schema_overrides={"lattes_id": pl.String})
        df_final.write_excel("data/csv/transfer_of_technology.xlsx")
        print(f"Total de linhas (após transfer_of_technology): {df_final.height}")


def participation_in_project_csv(base_year=current_year):
    researchers = get_researchers()
    print(f"Total de linhas (inicial): {researchers.height}")

    # Bolsa
    foment_level = get_foment_level()
    researchers = merge_data(researchers, foment_level)
    print(f"Total de linhas (após foment_level): {researchers.height}")

    # 5 ou 10 Anos
    researchers = add_evaluation_window(researchers)
    print(f"Total de linhas (após add_evaluation_window): {researchers.height}")

    productions_to_process = [
        (get_scientific_projects, "total_scientific_projects"),
        (get_projects_with_companies, "total_projects_with_companies"),
        (get_research_projects, "total_research_projects"),
    ]
    for get_func, col_name in productions_to_process:
        researchers = process_and_merge_production(
            researchers, get_func, col_name, base_year
        )
        print(f"Total de linhas (após {col_name}): {researchers.height}")

    researchers.write_csv("data/csv/participation_in_project.csv")
    researchers.write_excel("data/csv/participation_in_project.xlsx")


def human_resources_csv(base_year=current_year):
    researchers = get_researchers()
    print(f"Total de linhas (inicial): {researchers.height}")

    # Bolsa
    foment_level = get_foment_level()
    researchers = merge_data(researchers, foment_level)
    print(f"Total de linhas (após foment_level): {researchers.height}")

    # 5 ou 10 Anos
    researchers = add_evaluation_window(researchers)
    print(f"Total de linhas (após add_evaluation_window): {researchers.height}")

    productions_to_process = [
        (get_guidance_postdoc, "total_guidance_postdoc"),
        (get_phd_completed, "total_phd_completed"),
        (get_phd_ongoing, "total_phd_ongoing"),
        (get_msc_completed, "total_msc_completed"),
        (get_msc_ongoing, "total_msc_ongoing"),
    ]
    for get_func, col_name in productions_to_process:
        researchers = process_and_merge_production(
            researchers, get_func, col_name, base_year
        )
        print(f"Total de linhas (após {col_name}): {researchers.height}")

    researchers.write_csv("data/csv/human_resources.csv")
    researchers.write_excel("data/csv/human_resources.xlsx")


def project_analysis_csv(base_year=current_year):
    def get_processed_ids(path):
        if not os.path.exists(path):
            return set()

        df = pl.read_csv(path, schema_overrides={"lattes_id": pl.String})
        return set(df["lattes_id"].to_list())

    researchers = get_researchers()

    foment_level = get_foment_level()
    researchers = merge_data(researchers, foment_level)

    researchers = add_evaluation_window(researchers)

    researchers = researchers.with_columns(pl.col("lattes_id").cast(pl.String))

    output_path = "data/csv/project_analysis.csv"

    processed = get_processed_ids(output_path)

    rows = list(researchers.iter_rows(named=True))

    for row in tqdm(rows, desc="Analisando projetos", total=len(rows)):
        lattes_id = str(row["lattes_id"])

        if lattes_id in processed:
            continue

        resultado = evaluation(lattes_id)

        linha = {**row, **resultado}

        df = pl.DataFrame([linha]).with_columns(pl.col("lattes_id").cast(pl.String))

        if not os.path.exists(output_path):
            df.write_csv(output_path)
        else:
            with open(output_path, "a", encoding="utf-8") as f:
                df.write_csv(f, include_header=False)


def report_csv(base_year=current_year):
    researcher_profile_csv()
    technological_production_and_innovation_csv()
    transfer_of_technology_csv()
    participation_in_project_csv()
    human_resources_csv()
    project_analysis_csv()
