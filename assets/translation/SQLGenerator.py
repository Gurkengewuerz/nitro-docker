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


todo_types = ["roomitemtypes", "wallitemtypes"]

# Load the JSON data from the file
with open("../assets/gamedata/FurnitureData.json", encoding='utf-8') as f:
    data = json.load(f)

with open("catalog_items.sql", "w", encoding='utf-8') as f:
    for todo_type in todo_types:
        for furni in data[todo_type]["furnitype"]:
            furni_id = furni["id"]
            if furni["name"]:
                # get rid of any unwanted characters for sql and remove non latin-1 characters
                # check the collation of the table
                furni_name = sqlescape(furni["name"][:55]).encode("latin-1", "ignore").decode("utf-8")
                f.write(f"UPDATE catalog_items SET catalog_name = '{furni_name}' WHERE item_ids = '{furni_id}';\n")
                #f.write(f"UPDATE items_base SET public_name = '{furni_name}' WHERE id = '{furni_id}';\n")
