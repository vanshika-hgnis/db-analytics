# sql_validator.py
import sqlglot

class SQLValidator:
    def validate(self, sql_query):
        try:
            sqlglot.parse_one(sql_query)
            return True
        except Exception as e:
            print("Validation failed:", e)
            return False
