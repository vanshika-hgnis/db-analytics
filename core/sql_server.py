import pyodbc
import pandas as pd
import os
from dotenv import load_dotenv

class SQLServerConnection:
    def __init__(self):
        load_dotenv()
        self.connection = None

    def connect(self):
        server = os.getenv('DB_SERVER')
        database = os.getenv('DB_NAME')
        username = os.getenv('DB_USER')
        password = os.getenv('DB_PASSWORD')

        conn_str = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={server};DATABASE={database};UID={username};PWD={password};"
            "Encrypt=no;Trusted_Connection=no;TrustServerCertificate=yes;Connection Timeout=30;"
        )

        self.connection = pyodbc.connect(conn_str)
        return True

    def execute_query(self, query):
        cursor = self.connection.cursor()
        cursor.execute(query)
        columns = [column[0] for column in cursor.description]
        data = cursor.fetchall()
        return pd.DataFrame.from_records(data, columns=columns)

    def close(self):
        if self.connection:
            self.connection.close()
