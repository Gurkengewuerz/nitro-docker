import json

todo_types = ["roomitemtypes", "wallitemtypes"]

# Create a dictionary mapping classname to name and description
furniture_dict = {}
with open('gamedata/furnidata.json', 'r', encoding='utf-8') as f:
    furniture_data = json.load(f)
    for todo_type in todo_types:
        for furnitype in furniture_data[todo_type]["furnitype"]:
            classname = furnitype['classname']
            furniture_dict[classname] = {
                "name": furnitype['name'],
                "description": furnitype['description'],
            }

orig_furniture_data = {}
# Load the JSON file
with open('../assets/gamedata/FurnitureData.json', 'r', encoding='utf-8') as f:
    orig_furniture_data = json.load(f)

# Replace the name and description values with values from the XML file
for todo_type in todo_types:
    for furnitype in orig_furniture_data[todo_type]["furnitype"]:
        classname = furnitype['classname']
        if classname in furniture_dict:
            furnitype['name'] = furniture_dict[classname]['name']
            furnitype['description'] = furniture_dict[classname]['description']


# Save the updated JSON file
with open('../assets/gamedata/FurnitureData.json', 'w') as f:
    json.dump(orig_furniture_data, f, separators=(',', ':'))
