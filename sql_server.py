# db-analytics/sql_server.py 
import pyodbc
import pandas as pd
from dotenv import load_dotenv
import os
import logging

class SQLServerConnection:
    def __init__(self):
        load_dotenv()
        self.connection = None
        self._setup_logging()
        
    def _setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def connect(self):
        try:
            server = os.getenv('DB_SERVER')
            database = os.getenv('DB_NAME')
            username = os.getenv('DB_USER')
            password = os.getenv('DB_PASSWORD')
            
            conn_str = (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={server};"
                f"DATABASE={database};"
                f"UID={username};"
                f"PWD={password};"
                "Encrypt=no;"
                "Trusted_Connection=no;"
                "TrustServerCertificate=yes;"
                "Connection Timeout=30;"
            )
            
            self.logger.info("Attempting connection to SQL Server...")
            self.connection = pyodbc.connect(conn_str)
            self.logger.info("Successfully connected to SQL Server")
            return True
        except pyodbc.Error as e:
            error_msg = str(e)
            if hasattr(e, 'sqlstate'):
                self.logger.error(f"Connection failed (SQL State: {e.sqlstate}): {error_msg}")
            else:
                self.logger.error(f"Connection failed: {error_msg}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error: {str(e)}")
            return False
    
    def execute_query(self, query, params=None):
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            columns = [column[0] for column in cursor.description]
            data = cursor.fetchall()
            df = pd.DataFrame.from_records(data, columns=columns)
            return df
        except Exception as e:
            self.logger.error(f"Query failed: {str(e)}")
            raise
        finally:
            if 'cursor' in locals():
                cursor.close()
    
    def close(self):
        if self.connection:
            self.connection.close()
            self.logger.info("Connection closed")
            self.connection = None
