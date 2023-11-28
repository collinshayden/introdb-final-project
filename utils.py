# simple utility functions

def select_table(con):
    tables = con.execute("SELECT name FROM sqlite_master WHERE type='table';")
    table_names = []
    print("Select a table to add to:")
    for name in tables.fetchall():
        print(name[0])
        table_names.append(name[0])

    selected_table = ""
    while selected_table not in table_names:
        selected_table = input(" => ").lower()
        if selected_table not in table_names:
            print("Invalid selection.")
    return selected_table, table_names


def print_table(con, table):
    rows = con.execute(f"SELECT * FROM {table}")
    for row in rows:
        print(row)
