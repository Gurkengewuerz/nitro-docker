import json
import sys

# this is dumb but easier than a mariadb python dependency


def sqlescape(str):
    return str.translate(
        str.maketrans({
            "\0": "\\0",
            "\r": "\\r",
            "\x08": "\\b",
            "\x09": "\\t",
            "\x1a": "\\z",
            "\n": "\\n",
            "\r": "\\r",
            "\"": "",
            "'": "",
            "\\": "\\\\",
            "%": "\\%"
        }))


known_names = []

todo_types = ["roomitemtypes", "wallitemtypes"]

# Load the JSON data from the file
with open("../assets/gamedata/FurnitureData.json", encoding='utf-8') as f:
    data = json.load(f)
    for todo_type in todo_types:
        for furni in data[todo_type]["furnitype"]:
            known_names.append(
                {"name": furni["name"], "classname": furni["classname"]})

with open("../assets/gamedata/ProductData.json", encoding='utf-8') as f:
    data = json.load(f)
    for furni in data["productdata"]["product"]:
        known_names.append({"name": furni["name"], "classname": furni["code"]})


seen = set()
known_names_copy = known_names
known_names = []

for dic in known_names_copy:
    key = (dic['classname'])
    if key in seen:
        continue

    known_names.append(dic)
    seen.add(key)

with open("catalog_items.sql", "w", encoding='utf-8') as f:
    for furni in known_names:
        # get rid of any unwanted characters for sql and remove non latin-1 characters
        # check the collation of the table
        if furni["name"] is None:
            continue
        furni_name = sqlescape(furni["name"].encode(
            "latin-1", "ignore").decode("latin-1"))[:55]
        classname = sqlescape(furni["classname"].encode(
            "latin-1", "ignore").decode("latin-1"))
        #f.write(f"UPDATE catalog_items ci SET ci.catalog_name = '{furni_name}' WHERE item_ids IN (SELECT CAST(id AS CHAR) FROM items_base WHERE item_name = '{classname}');\n")
        f.write(
            f"UPDATE catalog_items ci, (SELECT CAST(id AS CHAR) as id, item_name FROM items_base WHERE item_name = '{classname}') item SET ci.catalog_name = '{classname}' WHERE ci.item_ids = item.id;\n")
