import sqlite3
from sqlmodel import Field, SQLModel, Session, create_engine
from db.utils.entities import *
import pandas as pd


def create_db_engine():
    sqlite_file_name = "aero.db"
    sqlite_url = f"sqlite:///{sqlite_file_name}"
    engine = create_engine(url=sqlite_url, echo=True)

    return engine


def create_db_and_tables():
    engine = create_db_engine()
    SQLModel.metadata.create_all(engine)


def get_con(db_path="aero.db"):
    con = sqlite3.connect(db_path)
    return con


def execute_generic_query(db_path, query, first_value=True):

    con = get_con(db_path=db_path)
    cur = con.cursor()

    dict_results = {}

    # Retornamos apenas o primeiro valor da tupla. Mesmo que seja uma query que retorne um único valor, ele em no formato de tupla.
    if first_value is True:
        result = [i[0] for i in cur.execute(query).fetchall()]
        if len(result) == 1:
            result = result[0]
    else:
        result = cur.execute(query).fetchall()
        columns = [descricao[0] for descricao in cur.description]

        for row in result:
            dict_results[row[0]] = dict(zip(columns, row))

        print(dict_results)

    return result, dict_results


def drop_generic_table(table_name: str):
    con = get_con()
    cur = con.cursor()

    try:
        cur.execute(f"DROP TABLE {table_name}")
        print(f"{table_name} table deleted succesfully.")
    except Exception:
        print(Exception(f"Error while trying to delete table {table_name}."))


def load_airports():
    engine = create_db_engine()
    session = Session(engine)

    # Function to load all airports from db/utils/brasil_aeroportos.csv into aero.db
    brazil_airports = pd.read_csv("brasil_aeroportos.csv", sep=",")

    for index, data in brazil_airports.iterrows():
        nome = data[2]
        iata = data[4].replace(" ", "")
        icao = data[3].replace(" ", "")
        cidade = data[-2].split("/")[0].replace(" ", "")
        estado = data[-2].split("/")[1].replace(" ", "")

        airport = Airport(nome=nome, iata=iata, icao=icao, cidade=cidade, estado=estado)
        session.add(airport)
        session.commit()

    session.close()


def load_group_types():
    engine = create_db_engine()
    session = Session(engine)

    # Fonte: Venson e Silva (2023)

    g1 = GroundType(superficie="Concreto/asfalto seco", min_mu_decolagem=0.03, max_mu_decolagem=0.05, min_mu_pouso=0.3, max_mu_pouso=0.6)
    g2 = GroundType(superficie="Concreto/asfalto molhado", min_mu_decolagem=0.04, max_mu_decolagem=0.06, min_mu_pouso=0.15, max_mu_pouso=0.3)
    g3 = GroundType(superficie="Grama curta seca", min_mu_decolagem=0.05, max_mu_decolagem=0.06, min_mu_pouso=0.25, max_mu_pouso=0.35)
    g4 = GroundType(superficie="Grama curta molhada", min_mu_decolagem=0.06, max_mu_decolagem=0.08, min_mu_pouso=0.15, max_mu_pouso=0.25)
    g5 = GroundType(superficie="Concreto/asfalto com gelo", min_mu_decolagem=0.01, max_mu_decolagem=0.03, min_mu_pouso=0.06, max_mu_pouso=0.1)
    g6 = GroundType(superficie="Solo macio", min_mu_decolagem=0.1, max_mu_decolagem=0.3, min_mu_pouso=0.3, max_mu_pouso=0.4)
    g7 = GroundType(superficie="Terra firme e seca", min_mu_decolagem=0.06, max_mu_decolagem=0.1, min_mu_pouso=0.3, max_mu_pouso=0.4)

    for ground in ([g1, g2, g3, g4, g5, g6, g7]):
        session.add(ground)

    session.commit()
    session.close()


def load_default_tables():
    create_db_and_tables()
    load_airports()
    load_group_types()

