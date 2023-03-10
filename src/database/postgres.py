import psycopg2
from src.config import DATABASE


class Postgres:
    """
    Вспомогательный класс для упрощенного доступа к базе данных
    """

    def __init__(self):
        self.conn = psycopg2.connect(dbname=DATABASE['dbname'], user=DATABASE['user'],
                                     password=DATABASE['password'], host=DATABASE['host'])
        self.curs = self.conn.cursor()

    async def create_table(self, table_name: str, params: list[str], serial_pk: bool = True):
        """
        :param table_name: database name like "users"
        :param params: ["column1 TYPE1", "column2 TYPE2"] like ["tg_id INTEGER,", "name VARCHAR(30),"]
        :param serial_pk: True - create already with "id SERIAL PRIMARY KEY", False - without
        :return:
        """
        pars = ''
        for param in params:
            pars += f'{param},\n'
        pars = pars[:len(pars)-2]  # delete extra ",\n"

        create_db_query = f'''CREATE TABLE IF NOT EXISTS {table_name}(
        {"id SERIAL PRIMARY KEY," if serial_pk else ''} 
        {pars}
        );'''

        self.curs.execute(create_db_query)
        self.conn.commit()

    async def insert_into_table(self, table_name: str, params: str, values: list[str]):
        """
        :param table_name: database name like "users"
        :param params: "column1, column2, ..." like "tg_id, name, ..."
        :param values: ["param1, 'param_str1'", "param2, 'param_str2'"] like ["64235, 'Andrew'", "22425, 'Lucio'"]
        :return:
        """
        pars = ''
        for param in params:
            pars += f'{param}'
        vals = ''
        for val in values:
            vals += f'({val}),'
        vals = vals[:len(vals) - 1]
        insert_query = f"INSERT INTO {table_name}({pars})\nVALUES{vals};"

        self.curs.execute(insert_query)
        self.conn.commit()

    async def select_from_table(self, table_name: str, params: str = '*', ex_param: str = ''):
        """
        :param table_name: database name like "users"
        :param params: by default it's ALL(*), can be "column1, column2" like "tg_id, name"
        :param ex_param: by default it's '', can be "FILTER column=value" like "WHERE tg_id=12345"
        :return:
        """
        select_query = f'SELECT {params} FROM {table_name} {ex_param}'
        self.curs.execute(select_query)
        return self.curs.fetchall()

    async def update_table(self, table_name: str, params: str, ex_param: str = ''):
        """
        :param table_name: database name like "users"
        :param params: "column = param" or "(column1, column2, ...) = (param1, param2, ...)"
        :param ex_param: like "WHERE column1 = param1 AND column2 = param2"
        :return:
        """
        update_query = f"UPDATE {table_name} SET {params} {ex_param}"
        self.curs.execute(query=update_query)
        self.conn.commit()

    async def delete_from_table(self, table_name: str, ex_param: str):
        """
        :param table_name: database name like "users"
        :param ex_param: by default it's '', can be like "WHERE column1 = param1 AND column2 = param2"
        :return:
        """
        delete_query = f"DELETE FROM {table_name} {ex_param}"
        self.curs.execute(delete_query)
        self.conn.commit()
