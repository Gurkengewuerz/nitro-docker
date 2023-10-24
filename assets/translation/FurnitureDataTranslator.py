import json

todo_types = ["roomitemtypes", "wallitemtypes"]

# Furnidata id = items_base.sprite_id
# Productdata classname = catalog_items.catalog_name
# Furnidata classname = items_base.item_name/public_name
# items_base.id = catalog_items.items_id which is different from sprite id and furnidata id

def normalize_classnames(classname):
    return str(classname).replace("_", "").replace(" ", "")

# Create a dictionary mapping classname to name and description
furniture_dict = {}
with open('gamedata/furnidata.json', 'r', encoding='utf-8') as f:
    furniture_data = json.load(f)
    for todo_type in todo_types:
        for furnitype in furniture_data[todo_type]["furnitype"]:
            classname = normalize_classnames(furnitype['classname'])
            furniture_dict[classname] = {
                "name": furnitype['name'],
                "description": furnitype['description'],
                "specialtype": furnitype['specialtype'],
            }
            if str(furniture_dict[classname]['description']).endswith("desc"):
                furniture_dict[classname]['description'] = ""

with open('gamedata/productdata.json', 'r', encoding='utf-8') as f:
    product_data = json.load(f)
    for product in product_data["productdata"]["product"]:
        classname = normalize_classnames(product['code'])
        furniture_dict[classname] = {
            "name": product['name'],
            "description": product['description'],
        }
        if str(furniture_dict[classname]['description']).endswith("desc"):
            furniture_dict[classname]['description'] = ""

orig_furniture_data = {}
# Load the JSON file
with open('../assets/gamedata/FurnitureData.json', 'r', encoding='utf-8') as f:
    orig_furniture_data = json.load(f)

# Replace the name and description values with values from the XML file
for todo_type in todo_types:
    for furnitype in orig_furniture_data[todo_type]["furnitype"]:
        classname = normalize_classnames(furnitype['classname'])
        if classname in furniture_dict:
            furnitype['name'] = furniture_dict[classname]['name']
            furnitype['description'] = furniture_dict[classname]['description']
            if "specialtype" in furniture_dict[classname]:
                furnitype['specialtype'] = furniture_dict[classname]['specialtype']


orig_product_dict = {}
# Load the JSON file
with open('../assets/gamedata/ProductData.json', 'r', encoding='utf-8') as f:
    orig_product_dict = json.load(f)

for product in orig_product_dict["productdata"]["product"]:
    classname = normalize_classnames(product['code'])
    if classname in furniture_dict:
        product['name'] = furniture_dict[classname]['name']
        product['description'] = furniture_dict[classname]['description']


# Save the updated JSON file
with open('../assets/gamedata/FurnitureData.json', 'w') as f:
    json.dump(orig_furniture_data, f, separators=(',', ':'))

with open('../assets/gamedata/ProductData.json', 'w') as f:
    json.dump(orig_product_dict, f, separators=(',', ':'))
