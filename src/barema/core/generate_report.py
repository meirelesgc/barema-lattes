from datetime import datetime

from barema.services.ai_evaluation import analyze_projects
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
    researchers = get_researchers()

    # Bolsa
    foment_level = get_foment_level()
    researchers = merge_data(researchers, foment_level)

    # 5 ou 10 Anos
    researchers = add_evaluation_window(researchers)
    researchers = analyze_projects(researchers)

    researchers.write_csv("data/csv/project_analysis.csv")
    researchers.write_excel("data/csv/project_analysis.xlsx")


def start_process(base_year=current_year):
    researcher_profile_csv()
    technological_production_and_innovation_csv()
    transfer_of_technology_csv()
    participation_in_project_csv()
    human_resources_csv()
    project_analysis_csv()
