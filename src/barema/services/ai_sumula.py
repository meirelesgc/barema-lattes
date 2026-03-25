import json
import os

import polars as pl
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

from barema.core.settings import Settings
from barema.prompts import PROMPT_BAREMA_NOVO

SETTINGS = Settings()


def evaluation(lattes_id: str):
    file_path = f"data/raw/projects/{lattes_id}.pdf"

    default_response = {
        "sumula": "Não encontrado",
        "transferencia_tecnologia_quantidade": 0,
        "transferencia_tecnologia_observacao": "Relatório não encontrado",
        "extensao_inovadora_quantidade": 0,
        "extensao_inovadora_observacao": "Relatório não encontrado",
        "trajetoria_proponente": 0,
    }

    if not os.path.exists(file_path):
        return default_response

    loader = PyMuPDFLoader(file_path, mode="single")
    documents = loader.load()
    documento_completo = "\n\n".join([doc.page_content for doc in documents])

    llm = ChatOpenAI(
        api_key=SETTINGS.OPENAI_API_KEY,
        model="gpt-4o-mini",
        temperature=0,
        model_kwargs={"response_format": {"type": "json_object"}},
    )

    mensagem = HumanMessage(
        content=f"{PROMPT_BAREMA_NOVO}\n\nDocumento: {documento_completo}"
    )

    resposta = llm.invoke([mensagem])

    try:
        dados = json.loads(resposta.content)
        return dados
    except Exception:
        return default_response


def analyze_projects(researchers: pl.DataFrame):
    df_resultado = researchers.with_columns(
        pl.col("lattes_id")
        .map_elements(
            evaluation,
            return_dtype=pl.Struct(
                [
                    pl.Field("sumula", pl.String),
                    pl.Field("transferencia_tecnologia_quantidade", pl.Int64),
                    pl.Field("transferencia_tecnologia_observacao", pl.String),
                    pl.Field("extensao_inovadora_quantidade", pl.Int64),
                    pl.Field("extensao_inovadora_observacao", pl.String),
                    pl.Field("trajetoria_proponente", pl.Int64),
                ]
            ),
        )
        .alias("barema_data")
    ).unnest("barema_data")

    return df_resultado
