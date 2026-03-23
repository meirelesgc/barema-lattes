import os

import polars as pl

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
    {"original": "phd_level", "new": "Tempo doutorado", "default": 0},
    {"original": "foment_level", "new": "Nível bolsista", "default": 0},
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


def load_and_merge():
    dfs = []

    for file in FILES:
        if os.path.exists(file):
            df = pl.read_csv(file, schema_overrides={"lattes_id": pl.String})
            dfs.append(df)

    base = dfs[0]

    for df in dfs[1:]:
        new_cols = [c for c in df.columns if c not in base.columns or c == "lattes_id"]
        df = df.select(new_cols)
        base = base.join(df, on="lattes_id", how="left")

    return base


def apply_config(df):
    expressions = []

    for item in CONFIG:
        original = item["original"]
        new = item["new"]
        default = item["default"]

        if original != "_" and original in df.columns:
            expressions.append(pl.col(original).fill_null(default).alias(new))
        else:
            expressions.append(pl.lit(default).alias(new))

    return df.select(expressions)


def generate_final_report():
    df = load_and_merge()
    df = apply_config(df)

    os.makedirs("data/final", exist_ok=True)

    df.write_csv("data/final/barema_final.csv")
    df.write_excel("data/final/barema_final.xlsx")


if __name__ == "__main__":
    generate_final_report()
