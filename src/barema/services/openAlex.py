import time

import httpx
import polars as pl
from sqlalchemy import text

from barema.db.connection import get_session

OPENALEX_URL = "https://api.openalex.org/authors/orcid:"


def get_researchers_without_openalex():
    session = get_session()

    query = """
    SELECT r.id::text AS researcher_id, r.orcid
    FROM researcher r
    LEFT JOIN openalex_researcher opr
        ON r.id = opr.researcher_id
    WHERE r.orcid IS NOT NULL
        AND opr.researcher_id IS NULL;
    """

    result = session.execute(text(query))
    data = result.mappings().all()

    schema = {
        "researcher_id": pl.Utf8,
        "orcid": pl.Utf8,
    }

    return pl.DataFrame(data, schema=schema)


def insert_openalex_researcher(row):
    session = get_session()

    query = """
    INSERT INTO public.openalex_researcher
        (researcher_id, h_index, relevance_score, works_count,
        cited_by_count, i10_index, scopus, orcid, openalex)
    VALUES
        (:researcher_id, :h_index, :relevance_score, :works_count,
        :cited_by_count, :i10_index, :scopus, :orcid, :openalex);
    """

    session.execute(text(query), row)
    session.commit()


def extract_researcher(researcher_id, data):
    summary = data.get("summary_stats") or {}
    ids = data.get("ids") or {}

    h_index = summary.get("h_index")
    i10_index = summary.get("i10_index")

    orcid = ids.get("orcid")
    if orcid:
        orcid = orcid[-18:]

    scopus = ids.get("scopus")

    openalex = data.get("id")

    works_count = data.get("works_count")

    cited_by_count = data.get("cited_by_count")

    row = {
        "researcher_id": researcher_id,
        "h_index": h_index,
        "relevance_score": 0,
        "works_count": works_count,
        "cited_by_count": cited_by_count,
        "i10_index": i10_index,
        "scopus": scopus,
        "orcid": orcid,
        "openalex": openalex,
    }

    insert_openalex_researcher(row)


def fetch_openalex_researcher(orcid):
    url = OPENALEX_URL + orcid

    with httpx.Client(timeout=60) as client:
        response = client.get(url)

    if response.status_code == 200:
        return response.json()

    return None


def scrapping_researcher_data():
    researchers = get_researchers_without_openalex()

    rows = list(researchers.iter_rows(named=True))

    for row in rows:
        researcher_id = row["researcher_id"]
        orcid = row["orcid"]

        data = fetch_openalex_researcher(orcid)

        if data:
            extract_researcher(researcher_id, data)

            print(f"[201] CREATED RESEARCHER {researcher_id}")
        else:
            print(f"[404] NOT FOUND RESEARCHER {researcher_id}")

        time.sleep(6)


if __name__ == "__main__":
    scrapping_researcher_data()
