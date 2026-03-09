import zipfile
from pathlib import Path

import httpx
import polars as pl
import urllib3
from tqdm import tqdm

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
RAW_DATA_PATH = BASE_DIR / "data" / "raw" / "lattes"
PROXY_URL = "https://simcc.uesc.br/v3/api/getCurriculoCompactado"
IDENTIFICADOR_URL = "https://simcc.uesc.br/v3/api/getIdentificadorCNPq"


def get_lattes_id(cpf: str, http_client: httpx.Client) -> str | None:
    cpf_clean = "".join(filter(str.isdigit, cpf))

    response = http_client.get(
        IDENTIFICADOR_URL,
        params={"cpf": cpf_clean, "nomeCompleto": "", "dataNascimento": ""},
    )

    if response.status_code == 200 and response.text:
        return response.text.strip()
    return None


def add_lattes_id(df: pl.DataFrame) -> pl.DataFrame:
    with httpx.Client(timeout=30.0, verify=False) as http_client:
        ids = []

        for row in tqdm(
            df.iter_rows(named=True), total=df.height, desc="Buscando Lattes ID"
        ):
            cpf = row["CPF"]
            try:
                lattes_id = get_lattes_id(cpf, http_client)
                ids.append(lattes_id)
            except Exception:
                ids.append(None)

    return df.with_columns(pl.Series("lattes_id", ids))


def download_and_extract(lattes_id: str, http_client: httpx.Client) -> None:
    response = http_client.get(PROXY_URL, params={"lattes_id": lattes_id})
    response.raise_for_status()
    content = response.content

    if not content:
        raise ValueError("Conteúdo retornado sem dados.")

    zip_path = RAW_DATA_PATH / f"{lattes_id}.zip"

    with open(zip_path, "wb") as f:
        f.write(content)

    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(RAW_DATA_PATH)

    zip_path.unlink(missing_ok=True)


def download_lattes_xml(df: pl.DataFrame):
    RAW_DATA_PATH.mkdir(parents=True, exist_ok=True)

    if df.is_empty():
        print("O DataFrame fornecido está vazio.")
        return

    with httpx.Client(timeout=30.0, verify=False) as http_client:
        for row in tqdm(
            df.iter_rows(named=True), total=df.height, desc="Baixando Lattes"
        ):
            nome = row["Nome"]
            lattes_id = row["lattes_id"]

            if not lattes_id:
                print(f"\n[Aviso] Lattes ID não encontrado para: {nome}")
                continue

            try:
                download_and_extract(lattes_id, http_client)
            except Exception as e:
                print(f"\n[Erro] Falha ao baixar Lattes de {nome}: {e}")

    print("\nOperação concluída com sucesso.")
