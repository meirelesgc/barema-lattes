import os
from typing import Optional

import polars as pl
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from barema.core.settings import Settings

SETTINGS = Settings()
llm = ChatOpenAI(api_key=SETTINGS.OPENAI_API_KEY, model="gpt-4o-mini", temperature=0)


class ExtractionResult(BaseModel):
    licenciamento_qtd: int
    licenciamento: Optional[str]
    servicos_qtd: int
    servicos: Optional[str]
    empresas_qtd: int
    empresas: Optional[str]
    demanda_qtd: int
    demanda: Optional[str]


parser = PydanticOutputParser(pydantic_object=ExtractionResult)

prompt_template = """
Você receberá o texto extraído das seções 11 e 12 do currículo.

Para cada critério abaixo:

1) Licenciamento
2) Serviços
3) Empresas/Outros
4) Demanda

Faça:

- Identifique evidências claras no texto.
- Conte quantas evidências distintas existem.
- Produza um pequeno texto em Markdown explicando o que foi identificado.
- Inclua pelo menos uma citação literal curta retirada exatamente do texto.
- A citação deve estar em bloco Markdown usando > 

Se não houver evidência:
- Retorne quantidade 0
- Retorne null para o markdown

A quantidade deve refletir o número real de evidências distintas encontradas no texto.

Responda SOMENTE com o JSON no formato do parser.
{format_instructions}

Texto:
{text}
"""

prompt = PromptTemplate(
    template=prompt_template,
    input_variables=["text"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)

chain = prompt | llm | parser


def _load_text_from_pdf(file_path: str) -> str:
    loader = PyMuPDFLoader(file_path, mode="single")
    documents = loader.load()
    texts = [d.page_content for d in documents]
    return "\n".join(texts)


def extract_data(lattes_id: str):
    file_path = f"data/raw/projects/{lattes_id}.pdf"

    if not os.path.exists(file_path):
        return {
            "licenciamento_qtd": 0,
            "licenciamento": None,
            "servicos_qtd": 0,
            "servicos": None,
            "empresas_qtd": 0,
            "empresas": None,
            "demanda_qtd": 0,
            "demanda": None,
        }

    text = _load_text_from_pdf(file_path)
    parsed = chain.invoke({"text": text})
    return {
        "licenciamento_qtd": parsed.licenciamento_qtd,
        "licenciamento": parsed.licenciamento,
        "servicos_qtd": parsed.servicos_qtd,
        "servicos": parsed.servicos,
        "empresas_qtd": parsed.empresas_qtd,
        "empresas": parsed.empresas,
        "demanda_qtd": parsed.demanda_qtd,
        "demanda": parsed.demanda,
    }


def get_transfer_of_technology(researchers: pl.DataFrame):
    result = researchers.with_columns(
        pl.col("lattes_id")
        .map_elements(
            extract_data,
            return_dtype=pl.Struct(
                {
                    "licenciamento_qtd": pl.Int64,
                    "licenciamento": pl.Utf8,
                    "servicos_qtd": pl.Int64,
                    "servicos": pl.Utf8,
                    "empresas_qtd": pl.Int64,
                    "empresas": pl.Utf8,
                    "demanda_qtd": pl.Int64,
                    "demanda": pl.Utf8,
                }
            ),
        )
        .alias("extraction")
    ).unnest("extraction")

    return result
