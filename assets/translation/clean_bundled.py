import json
import glob
import os

from fuzzywuzzy import process, fuzz

def normalize_classnames(classname):
    return str(classname).replace("_", "").replace(" ", "")

todo_types = ["roomitemtypes", "wallitemtypes"]

orig_furniture_data = {}
# Load the JSON file
with open('../assets/gamedata/FurnitureData.json', 'r', encoding='utf-8') as f:
    orig_furniture_data = json.load(f)

orig_product_dict = {}
# Load the JSON file
with open('../assets/gamedata/ProductData.json', 'r', encoding='utf-8') as f:
    orig_product_dict = json.load(f)

classnames = set()

for todo_type in todo_types:
    for furnitype in orig_furniture_data[todo_type]["furnitype"]:
        classnames.add(normalize_classnames(furnitype['classname']))


for product in orig_product_dict["productdata"]["product"]:
    classnames.add(normalize_classnames(product['code']))

not_matched = set()
nitro_files = glob.glob("../assets/bundled/furniture/*.nitro")
nitro_files_len = float(len(nitro_files))
for index, nitro in enumerate(nitro_files): 
    f_name = os.path.basename(nitro)
    normalized = normalize_classnames(f_name.rstrip(".nitro"))
    matched = False
    perc = str(round((float(index + 1) / nitro_files_len) * 100.0, 2)) + "%"
    for clazz in classnames.copy():
        string_matched = fuzz.ratio(clazz, normalized)
        if string_matched > 75:
            matched = True
            print("Matched", f_name, clazz, perc)
            break
    if not matched:
        not_matched.add(nitro)
        print("Unmatched delete", f_name, perc)
        os.remove(nitro)
    

print()
print()
print("-------------------------------")
print(f"Known Classes: {len(classnames)}")
print(f"Unused Files: {len(not_matched)} this result in {int(nitro_files_len - len(not_matched))} remaining files")