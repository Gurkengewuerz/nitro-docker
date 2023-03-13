import json

# Create a dictionary mapping classname to name and description
furniture_dict = {}
with open('gamedata/furnidata.json', 'r', encoding='utf-8') as f:
    furniture_data = json.load(f)
    for furnitype in furniture_data['roomitemtypes']['furnitype']:
        classname = furnitype['classname']
        furniture_dict[classname] = {
            "name": furnitype['name'],
            "description": furnitype['description'],
        }

# Load the JSON file
with open('../assets/gamedata/FurnitureData.json', 'r', encoding='utf-8') as f:
    furniture_data = json.load(f)

# Replace the name and description values with values from the XML file
for furnitype in furniture_data['roomitemtypes']['furnitype']:
    classname = furnitype['classname']
    if classname in furniture_dict:
        furnitype['name'] = furniture_dict[classname]['name']
        furnitype['description'] = furniture_dict[classname]['description']

# Save the updated JSON file
with open('../assets/gamedata/FurnitureData.json', 'w') as f:
    json.dump(furniture_data, f, separators=(',', ':'))
