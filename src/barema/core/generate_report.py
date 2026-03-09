import os
from datetime import datetime
from pathlib import Path

import polars as pl
from tqdm import tqdm

from barema.services.ai_evaluation import evaluation
from barema.services.ai_extraction import get_transfer_of_technology
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

    # Tempo doutorado
    phd_time = get_phd_time()
    researchers = merge_data(researchers, phd_time)

    # Nivel do pesquisador
    phd_level = add_phd_level(phd_time)
    researchers = merge_data(researchers, phd_level)

    # Bolsa
    foment_level = get_foment_level()
    researchers = merge_data(researchers, foment_level)

    # Gerar CSV
    researchers.write_csv("data/csv/researcher_profile.csv")
    researchers.write_excel("data/csv/researcher_profile.xlsx")


def technological_production_and_innovation_csv(base_year=current_year):
    researchers = get_researchers()

    # Bolsa
    foment_level = get_foment_level()
    researchers = merge_data(researchers, foment_level)

    # 5 ou 10 Anos
    researchers = add_evaluation_window(researchers)

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
    # Gerar CSV
    researchers.write_csv("data/csv/technological_production_and_innovation.csv")
    researchers.write_excel("data/csv/technological_production_and_innovation.xlsx")


def transfer_of_technology_csv():
    researchers = get_researchers()

    # Bolsa
    foment_level = get_foment_level()
    researchers = merge_data(researchers, foment_level)

    # 5 ou 10 Anos
    researchers = add_evaluation_window(researchers)

    # Extraindo a partir da Sumula - AI
    researchers = get_transfer_of_technology(researchers)

    researchers.write_csv("data/csv/transfer_of_technology.csv")
    researchers.write_excel("data/csv/transfer_of_technology.xlsx")


def participation_in_project_csv(base_year=current_year):
    researchers = get_researchers()

    # Bolsa
    foment_level = get_foment_level()
    researchers = merge_data(researchers, foment_level)

    # 5 ou 10 Anos
    researchers = add_evaluation_window(researchers)
    productions_to_process = [
        (get_scientific_projects, "total_scientific_projects"),
        (get_projects_with_companies, "total_projects_with_companies"),
        (get_research_projects, "total_research_projects"),
    ]
    for get_func, col_name in productions_to_process:
        researchers = process_and_merge_production(
            researchers, get_func, col_name, base_year
        )
    researchers.write_csv("data/csv/participation_in_project.csv")
    researchers.write_excel("data/csv/participation_in_project.xlsx")


def human_resources_csv(base_year=current_year):
    researchers = get_researchers()

    # Bolsa
    foment_level = get_foment_level()
    researchers = merge_data(researchers, foment_level)

    # 5 ou 10 Anos
    researchers = add_evaluation_window(researchers)
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
    researchers.write_csv("data/csv/human_resources.csv")
    researchers.write_excel("data/csv/human_resources.xlsx")


def project_analysis_csv(base_year=current_year):
    def get_processed_ids(path):
        if not os.path.exists(path):
            return set()

        df = pl.read_csv(path)
        return set(df["lattes_id"].to_list())

    researchers = get_researchers()

    foment_level = get_foment_level()
    researchers = merge_data(researchers, foment_level)

    researchers = add_evaluation_window(researchers)

    output_path = "data/csv/project_analysis.csv"

    processed = get_processed_ids(output_path)

    rows = list(researchers.iter_rows(named=True))

    for row in tqdm(rows, desc="Analisando projetos", total=len(rows)):
        if row["lattes_id"] in processed:
            continue

        lattes_id = row["lattes_id"]

        resultado = evaluation(lattes_id)

        linha = {**row, **resultado}

        df = pl.DataFrame([linha])

        if not os.path.exists(output_path):
            df.write_csv(output_path)
        else:
            with open(output_path, "a", encoding="utf-8") as f:
                df.write_csv(f, include_header=False)


def unir_csv_xlsx_por_lattes_id(pasta, output="data/csv/researchers_unificado.xlsx"):
    arquivos = sorted(Path(pasta).glob("*"))
    dfs = []

    for arq in arquivos:
        if arq.suffix == ".csv":
            df = pl.read_csv(arq)
        elif arq.suffix in [".xlsx", ".xls"]:
            df = pl.read_excel(arq)
        else:
            continue

        if "lattes_id" in df.columns:
            df = df.with_columns(pl.col("lattes_id").cast(pl.Utf8).str.zfill(16))

        dfs.append(df)

    base = dfs[0]

    for df in dfs[1:]:
        cols_novas = [
            c for c in df.columns if c not in base.columns or c == "lattes_id"
        ]
        df = df.select(cols_novas)
        base = base.join(df, on="lattes_id", how="left")

    if output.endswith(".csv"):
        base.write_csv(output)
    else:
        base.write_excel(output)

    return base


def start_process(base_year=current_year):
    researcher_profile_csv()
    technological_production_and_innovation_csv()
    transfer_of_technology_csv()
    participation_in_project_csv()
    human_resources_csv()
    project_analysis_csv()
    unir_csv_xlsx_por_lattes_id("data/csv")
