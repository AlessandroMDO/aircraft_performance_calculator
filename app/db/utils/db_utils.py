import sqlite3

def get_con(db_path="db/aero.db"):
    con = sqlite3.connect(db_path)
    return con

def delete_db_query(db_path, query):

    con = get_con(db_path=db_path)
    cur = con.cursor()
    cur.execute(query)
    con.commit()


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


def insert_data_to_db(db_path, query):

    con = get_con(db_path=db_path)
    cur = con.cursor()
    cur.execute(query)
    con.commit()



def drop_generic_table(table_name: str):
    con = get_con()
    cur = con.cursor()

    try:
        cur.execute(f"DROP TABLE {table_name}")
        print(f"{table_name} table deleted succesfully.")
    except Exception:
        print(Exception(f"Error while trying to delete table {table_name}."))

