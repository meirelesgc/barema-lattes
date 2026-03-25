import os
from datetime import datetime

import polars as pl

from barema.services.ai_evaluation import evaluate_projects
from barema.services.ai_extraction import get_transfer_of_technology
from barema.services.ai_tag import analyze_funding_agencies
from barema.services.queries import (
    get_articles,
    get_books,
    get_cultivar_patents,
    get_foment_level,
    get_guidance_postdoc,
    get_msc_completed,
    get_msc_ongoing,
    get_no_reg_software,
    get_other_technical_production,
    get_phd_completed,
    get_phd_ongoing,
    get_phd_time,
    get_project_funding_agencies,
    get_research_projects,
    get_researchers,
    get_software,
)
from barema.services.report_utils import (
    add_evaluation_window,
    add_phd_level,
    merge_data,
    process_and_merge_production,
)

current_year = datetime.now().year


FILES = [
    "data/csv/researcher_profile.csv",
    "data/csv/technological_production_and_innovation.csv",
    "data/csv/transfer_of_technology.csv",
    "data/csv/participation_in_project.csv",
    "data/csv/human_resources.csv",
    "data/csv/project_analysis.csv",
]

CONFIG = [
    {
        "original": "last_update",
        "new": "Ultima atualização",
        "default": "Erro",
    },
    {
        "original": "nome",
        "new": "Nome",
        "default": "Não informado",
    },
    {
        "original": "lattes_id",
        "new": "Identificador Lattes",
        "default": "Não informado",
    },
    {"original": "_", "new": "Avaliador", "default": "Não informado"},
    {"original": "_", "new": "Segundo olhar", "default": "Não informado"},
    {"original": "_", "new": "Classificação", "default": "Não informado"},
    {"original": "_", "new": "Projeto", "default": "Não informado"},
    {"original": "_", "new": "Proponente", "default": "Não informado"},
    {"original": "_", "new": "Súmula realizações", "default": "Não extraido"},
    {
        "original": "_",
        "new": "Transferência tecnologia impacto",
        "default": "Não extraido",
    },
    {"original": "_", "new": "Observação inicial", "default": "Não informado"},
    {"original": "_", "new": "Extensão inovadora", "default": "Não informado"},
    {"original": "_", "new": "Coeficiente súmula", "default": "Não informado"},
    {"original": "_", "new": "Ad hocs", "default": "Não informado"},
    {"original": "tempo_doutorado", "new": "Tempo doutorado", "default": 0},
    {"original": "nivel_bolsa", "new": "Nível bolsista", "default": 0},
    {"original": "h_index", "new": "Fator h", "default": 0},
    {"original": "_", "new": "Maternidade adoção", "default": "Não extraido"},
    {"original": "total_articles", "new": "Artigos periódicos", "default": 0},
    {"original": "total_books", "new": "Livros capítulos", "default": 0},
    {"original": "total_software", "new": "Software com registro", "default": 0},
    {"original": "total_no_reg_software", "new": "Software sem registro", "default": 0},
    {"original": "total_cultivar_patents", "new": "Patentes cultivares", "default": 0},
    {
        "original": "total_other_technical_production",
        "new": "Outros produtos tecnológicos",
        "default": 0,
    },
    {"original": "_", "new": "Soma produção tecnológica", "default": 0},
    {"original": "_", "new": "Nota produção tecnológica", "default": 0},
    {"original": "_", "new": "Nota coeficiente súmula produção", "default": 0},
    {
        "original": "licenciamento_qtd",
        "new": "Licenciamento transferência",
        "default": 0,
    },
    {"original": "servicos_qtd", "new": "Serviços tecnológicos", "default": 0},
    {"original": "empresas_qtd", "new": "Empresas terceiro setor", "default": 0},
    {"original": "demanda_qtd", "new": "Demanda", "default": 0},
    {"original": "_", "new": "Carta", "default": 0},
    {"original": "_", "new": "Soma transferência tecnologia", "default": 0},
    {"original": "_", "new": "Nota transferência tecnologia", "default": 0},
    {
        "original": "total_scientific_projects",
        "new": "Coord projetos científicos",
        "default": 0,
    },
    {
        "original": "total_projects_with_companies",
        "new": "Coord projetos empresas",
        "default": 0,
    },
    {
        "original": "total_research_projects",
        "new": "Coord projetos pesquisa",
        "default": 0,
    },
    {"original": "_", "new": "Soma projetos", "default": 0},
    {"original": "_", "new": "Nota projetos", "default": 0},
    {"original": "_", "new": "Nota coeficiente súmula projetos", "default": 0},
    {"original": "total_guidance_postdoc", "new": "Pós doutorado", "default": 0},
    {"original": "total_phd_completed", "new": "Doutorado concluído", "default": 0},
    {"original": "total_phd_ongoing", "new": "Doutorado andamento", "default": 0},
    {"original": "total_msc_completed", "new": "Mestrado concluído", "default": 0},
    {"original": "total_msc_ongoing", "new": "Mestrado andamento", "default": 0},
    {"original": "_", "new": "Bolsas tecnológicas", "default": "Não extraido"},
    {"original": "_", "new": "Bolsas ic outras", "default": "Não extraido"},
    {
        "original": "_",
        "new": "Organização programas formação",
        "default": "Não extraido",
    },
    {"original": "_", "new": "Capacitação rh", "default": "Não extraido"},
    {"original": "_", "new": "Nota rh", "default": "Não extraido"},
    {"original": "_", "new": "Nota coeficiente súmula rh", "default": "Não extraido"},
    {
        "original": "publico_produto",
        "new": "Público alvo produto",
        "default": "Projeto não encontrado",
    },
    {
        "original": "objetivos_metas_relevancia",
        "new": "Objetivos metas relevância",
        "default": "Projeto não encontrado",
    },
    {
        "original": "metodologia_gestao",
        "new": "Metodologia gestão",
        "default": "Projeto não encontrado",
    },
    {
        "original": "colaboracoes_financiamento",
        "new": "Colaborações financiamento",
        "default": "Projeto não encontrado",
    },
    {
        "original": "potencial_inovacao_empreendedorismo",
        "new": "Potencial inovação",
        "default": "Projeto não encontrado",
    },
    {
        "original": "demandas_escalabilidade",
        "new": "Demandas escalabilidade",
        "default": "Projeto não encontrado",
    },
    {
        "original": "maturidade_resultados",
        "new": "Maturidade resultados",
        "default": "Projeto não encontrado",
    },
    {
        "original": "organizacao_parcerias_extensao",
        "new": "Organização parcerias extensão",
        "default": "Projeto não encontrado",
    },
    {
        "original": "perfil_tecnologico",
        "new": "Perfil tecnológico",
        "default": "Projeto não encontrado",
    },
    {"original": "_", "new": "Usou formulário", "default": 0},
    {"original": "_", "new": "Observação projeto", "default": 0},
    {"original": "_", "new": "Nota foco desenvolvimento", "default": 0},
    {"original": "_", "new": "Parecer final", "default": 0},
    {"original": "_", "new": "Nota final com súmula", "default": 0},
    {"original": "_", "new": "Nota final sem súmula", "default": 0},
    {"original": "_", "new": "Observação final", "default": 0},
]


def researcher_profile_csv(base_year=current_year):
    researchers = get_researchers()
    phd_time = get_phd_time()
    researchers = merge_data(researchers, phd_time)
    phd_level = add_phd_level(phd_time)
    researchers = merge_data(researchers, phd_level)
    foment_level = get_foment_level()
    researchers = merge_data(researchers, foment_level)
    researchers.write_csv("data/csv/researcher_profile.csv")
    researchers.write_excel("data/csv/researcher_profile.xlsx")


def technological_production_and_innovation_csv(base_year=current_year):
    researchers = get_researchers()
    foment_level = get_foment_level()
    researchers = merge_data(researchers, foment_level)
    researchers = add_evaluation_window(researchers)
    productions_to_process = [
        (get_articles, "total_articles"),
        (get_books, "total_books"),
        (get_software, "total_software"),
        (get_no_reg_software, "total_no_reg_software"),
        (get_cultivar_patents, "total_cultivar_patents"),
        (get_other_technical_production, "total_other_technical_production"),
    ]
    for get_func, col_name in productions_to_process:
        researchers = process_and_merge_production(
            researchers, get_func, col_name, base_year
        )
    researchers.write_csv("data/csv/technological_production_and_innovation.csv")
    researchers.write_excel("data/csv/technological_production_and_innovation.xlsx")


def transfer_of_technology_csv():
    researchers = get_researchers()
    foment_level = get_foment_level()

    researchers = merge_data(researchers, foment_level)
    researchers = add_evaluation_window(researchers)

    df_final = get_transfer_of_technology(researchers)

    output_csv = "data/csv/transfer_of_technology.csv"
    output_xlsx = "data/csv/transfer_of_technology.xlsx"

    os.makedirs(os.path.dirname(output_csv), exist_ok=True)

    df_final.write_csv(output_csv)
    df_final.write_excel(output_xlsx)


def human_resources_csv():
    researchers = get_researchers()
    foment_level = get_foment_level()
    researchers = merge_data(researchers, foment_level)
    researchers = add_evaluation_window(researchers)
    productions_to_process = [
        (get_guidance_postdoc, "total_guidance_postdoc"),
        (get_phd_completed, "total_phd_completed"),
        (get_phd_ongoing, "total_phd_ongoing"),
        (get_msc_completed, "total_msc_completed"),
        (get_msc_ongoing, "total_msc_ongoing"),
    ]
    for get_func, col_name in productions_to_process:
        researchers = process_and_merge_production(researchers, get_func, col_name, 0)
    researchers.write_csv("data/csv/human_resources.csv")
    researchers.write_excel("data/csv/human_resources.xlsx")


def project_analysis_csv(base_year=current_year):
    researchers = get_researchers()
    foment_level = get_foment_level()

    researchers = merge_data(researchers, foment_level)
    researchers = add_evaluation_window(researchers)

    df_final = evaluate_projects(researchers)

    output_csv = "data/csv/project_analysis.csv"
    output_xlsx = "data/csv/project_analysis.xlsx"

    os.makedirs(os.path.dirname(output_csv), exist_ok=True)

    df_final.write_csv(output_csv)
    df_final.write_excel(output_xlsx)


def _get_projects_base():
    agencies = get_project_funding_agencies()
    df_analyzed = analyze_funding_agencies(agencies)
    projects = get_research_projects()

    return (
        projects.explode("agency_names")
        .join(df_analyzed, left_on="agency_names", right_on="agency_name", how="left")
        .group_by(["project_id", "researcher_id", "year", "is_coordinator", "nature"])
        .agg(
            [
                pl.col("agency_names"),
                pl.col("company_or_organization").any().alias("has_company_funding"),
            ]
        )
    )


def get_coord_cientifico_tecnologico():
    df = _get_projects_base()
    df = df.filter(
        (pl.col("nature") != "PESQUISA")
        & (~pl.col("has_company_funding"))
        & (pl.col("is_coordinator"))
    )
    df = df.group_by(["researcher_id", "year"]).agg(pl.count().alias("qtd"))
    return df.with_columns(
        [
            pl.col("researcher_id").cast(pl.Utf8),
            pl.col("year").cast(pl.Int32),
            pl.col("qtd").cast(pl.Int64),
        ]
    )


def get_membro_cientifico_tecnologico():
    df = _get_projects_base()
    df = df.filter(
        (pl.col("nature") != "PESQUISA")
        & (~pl.col("has_company_funding"))
        & (~pl.col("is_coordinator"))
    )
    df = df.group_by(["researcher_id", "year"]).agg(pl.count().alias("qtd"))
    return df.with_columns(
        [
            pl.col("researcher_id").cast(pl.Utf8),
            pl.col("year").cast(pl.Int32),
            pl.col("qtd").cast(pl.Int64),
        ]
    )


def get_coord_empresa():
    df = _get_projects_base()
    df = df.filter((pl.col("has_company_funding")) & (pl.col("is_coordinator")))
    df = df.group_by(["researcher_id", "year"]).agg(pl.count().alias("qtd"))
    return df.with_columns(
        [
            pl.col("researcher_id").cast(pl.Utf8),
            pl.col("year").cast(pl.Int32),
            pl.col("qtd").cast(pl.Int64),
        ]
    )


def get_membro_empresa():
    df = _get_projects_base()
    df = df.filter((pl.col("has_company_funding")) & (~pl.col("is_coordinator")))
    df = df.group_by(["researcher_id", "year"]).agg(pl.count().alias("qtd"))
    return df.with_columns(
        [
            pl.col("researcher_id").cast(pl.Utf8),
            pl.col("year").cast(pl.Int32),
            pl.col("qtd").cast(pl.Int64),
        ]
    )


def get_coord_pesquisa():
    df = _get_projects_base()
    df = df.filter(
        (pl.col("nature") == "PESQUISA")
        & (~pl.col("has_company_funding"))
        & (pl.col("is_coordinator"))
    )
    df = df.group_by(["researcher_id", "year"]).agg(pl.count().alias("qtd"))
    return df.with_columns(
        [
            pl.col("researcher_id").cast(pl.Utf8),
            pl.col("year").cast(pl.Int32),
            pl.col("qtd").cast(pl.Int64),
        ]
    )


def get_membro_pesquisa():
    df = _get_projects_base()
    df = df.filter(
        (pl.col("nature") == "PESQUISA")
        & (~pl.col("has_company_funding"))
        & (~pl.col("is_coordinator"))
    )
    df = df.group_by(["researcher_id", "year"]).agg(pl.count().alias("qtd"))
    return df.with_columns(
        [
            pl.col("researcher_id").cast(pl.Utf8),
            pl.col("year").cast(pl.Int32),
            pl.col("qtd").cast(pl.Int64),
        ]
    )


def participation_in_project_csv():
    researchers = get_researchers()
    foment_level = get_foment_level()
    researchers = merge_data(researchers, foment_level)
    researchers = add_evaluation_window(researchers)

    productions_to_process = [
        (get_coord_cientifico_tecnologico, "coord_cientifico_tecnologico"),
        (get_membro_cientifico_tecnologico, "membro_cientifico_tecnologico"),
        (get_coord_empresa, "coord_empresa"),
        (get_membro_empresa, "membro_empresa"),
        (get_coord_pesquisa, "coord_pesquisa"),
        (get_membro_pesquisa, "membro_pesquisa"),
    ]

    for get_func, col_name in productions_to_process:
        researchers = process_and_merge_production(
            researchers, get_func, col_name, current_year
        )

    researchers.write_csv("data/csv/participation_in_project.csv")
    researchers.write_excel("data/csv/participation_in_project.xlsx")


def generate_final_report():
    os.makedirs("data/csv/output", exist_ok=True)

    print("researcher_profile_csv")
    researcher_profile_csv()
    print("technological_production_and_innovation_csv")
    technological_production_and_innovation_csv()
    print("transfer_of_technology_csv")
    transfer_of_technology_csv()
    print("project_analysis_csv")
    project_analysis_csv()
    print("human_resources_csv")
    human_resources_csv()
    print("participation_in_project_csv")
    participation_in_project_csv()


if __name__ == "__main__":
    generate_final_report()
