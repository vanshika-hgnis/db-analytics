import sqlglot

class SQLRewriter:

    def __init__(self):
        pass

    def rewrite_aliases(self, query: str) -> str:
        try:
            parsed = sqlglot.parse_one(query)
            table_aliases = {}

            # Detect aliases
            for node in parsed.find_all(sqlglot.exp.From):
                for table in node.args['expressions']:
                    if hasattr(table, 'alias') and table.alias:
                        table_aliases[table.name] = table.alias
                    else:
                        # If no alias provided, assign default alias as first 2 letters
                        default_alias = table.name[:2].lower()
                        table.set("alias", sqlglot.exp.TableAlias(this=sqlglot.exp.Identifier(this=default_alias)))
                        table_aliases[table.name] = default_alias

            # Rewrite all column references consistently
            for col in parsed.find_all(sqlglot.exp.Column):
                if col.table and col.table not in table_aliases.values():
                    table = col.table
                    alias = table_aliases.get(table, None)
                    if alias:
                        col.set("table", sqlglot.exp.Identifier(this=alias))

            return parsed.sql()

        except Exception as e:
            print("SQL Rewrite Failed:", e)
            return query  # Fail-safe: return original
