import pandas as pd

# Load the Excel file
excel_file = 'perms.xlsx'
df = pd.read_excel(excel_file)

headers = list(df)[1:]
column_names = df.iloc[:, 0]

groups = []

for hi, rank in enumerate(headers):
    group = {}
    for index, row in df.iterrows():
        if str(row["col"]) == "nan":
            continue
        
        val = row[rank]
        if str(val) == "nan":
            val = ""
        
        try:
            val = int(val)
        except:
            pass

        group[row["col"]] = val
    groups.append(group)


def generate_insert_sql(table_name, data):
    """
    Generate an SQL INSERT INTO statement.

    Parameters:
    - table_name (str): The name of the table.
    - data (dict): A dictionary representing the column names and values.

    Returns:
    - str: The generated SQL statement.
    """
    columns = ', '.join(data.keys())
    values = ', '.join([f"'{value}'" for value in data.values()])

    sql_statement = f"INSERT INTO {table_name} ({columns}) VALUES ({values});"
    return sql_statement


with open("perms_groups.sql", 'w', encoding="utf-8") as file:
    file.write(f"-- auto generated by mc8051.de\n")

    for group in groups:
        file.write(f"-- permission group {group['name']}\n")
        group_id = group["id"]
        sql = generate_insert_sql("permission_groups", {"id": group_id, "name": group["name"], "description": group["description"], "level": group["level"], "prefix": group["prefix"], "prefix_color": group["prefix_color"], "badge": group["badge"], "room_effect": group["room_effect"], "log_enabled": group["log_enabled"]})
        file.write(sql + "\n")

        for key in group.keys():
            if not str(key).startswith("cmd_"):
                continue
            sql = generate_insert_sql("permission_group_commands", {"group_id": group_id, "command_name": key, "setting_type": group[key]})
            file.write(sql + "\n")

        for key in group.keys():
            if not str(key).startswith("acc_"):
                continue
            sql = generate_insert_sql("permission_group_rights", {"group_id": group_id, "right_name": key, "setting_type": group[key]})
            file.write(sql + "\n")

        file.write("\n\n")