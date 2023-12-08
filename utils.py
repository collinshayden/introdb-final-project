# simple utility functions

import numpy as np


# prompts user to select a table
def select_table(con):
    tables = con.execute("SELECT name FROM sqlite_master WHERE type='table';")
    # TODO make this cleaner
    table_names = []
    print("Select a table:")
    for name in tables.fetchall():
        print(name[0])
        table_names.append(name[0])

    selected_table = ""
    while selected_table not in table_names:
        selected_table = input(" => ").lower()
        if selected_table not in table_names:
            print("Invalid selection.")
    return selected_table, table_names


# returns list of column names for a given table
def get_column_names(con, table_name):
    cursor = con.cursor()

    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()

    column_names = [column[1] for column in columns]  # Extracting column names
    return column_names


# returns list of columns that have a numeric type
def get_numeric_columns(con):
    cursor = con.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    numeric_columns = {}

    for table in tables:
        table_name = table[0]
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()

        for column in columns:
            col_name = column[1]
            col_type = column[2]
            # if column data type is numeric and not an id field
            if (
                    'INT' in col_type or 'REAL' in col_type or 'FLOAT' in col_type or 'NUM' in col_type) and not col_name.endswith(
                '_id'):
                numeric_columns[col_name] = table_name

    return numeric_columns


# function to calculate std of a numeric column
def calculate_stats(con, column_name, table_name, operation):
    cursor = con.cursor()

    cursor.execute(f"SELECT {column_name} FROM {table_name}")
    column_data = cursor.fetchall()

    # Extract the column values and compute the standard deviation
    values = [x[0] for x in column_data]
    if operation == "std":
        return np.std(values)
    elif operation == "median":
        return np.median(values)
    elif operation == "avg":
        return np.mean(values)
    else:
        return None


# prints all rows in a table
def print_table(con, table):
    rows = con.execute(f"SELECT * FROM {table}")
    for row in rows:
        print(row)


# prints the result of a query
def print_query(con, query):
    result = con.execute(query)
    print("\n\nBelow is the result of your query!")
    print("----------------------------------------")
    result = result.fetchall()
    # if there are no values in the query return
    if len(result) == 0:
        print("There were no results for your query.")
    # if there is only one value, index into result to remove ()
    elif len(result) == 1:
        print(result[0][0])
    # if there are many results, but only one value in each row, print the contents without ()
    elif len(result[0]) == 1:
        for row in result:
            print(row[0])
    # otherwise print all rows
    else:
        for row in result:
            print(row)
    print("----------------------------------------")
