import sqlglot

class SQLValidator:
    def validate(self, sql_query):
        try:
            sqlglot.parse_one(sql_query)
            return True
        except:
            return False
