import argparse
import requests
import json

domains = ["com.br", "com.tr", "com", "de", "es", "fi", "fr", "it", "nl"]

def fetch_external_flash_texts(domain):
    url = f"https://www.habbo.{domain}/gamedata/external_flash_texts/0"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.text.split('\n')
    else:
        print(f"Failed to fetch data from {url}. Status code: {response.status_code}")
        return []

def parse_flash_texts(lines):
    flash_texts_dict = {}
    
    for line in lines:
        if '=' in line:
            key, value = line.split('=', 1)
            flash_texts_dict[key.strip()] = value.strip()
    
    return flash_texts_dict

def main():
    parser = argparse.ArgumentParser(description="Fetch and parse external flash texts for a given domain.")
    parser.add_argument("--domain", help="Specify the top-level domain (TLD) for fetching external flash texts.", choices=domains)
    
    args = parser.parse_args()
    
    if args.domain:
        domain = args.domain
    else:
        print("Please provide a valid domain using the --domain argument.")
        return

    domains.remove(domain)
    domains.append(domain)

    all_flash_texts = {}
    with open("../assets/gamedata/ExternalTexts.json", "r", encoding="utf-8") as f:
        all_flash_texts = json.load(f)
    
    for d in domains:
        flash_texts_lines = fetch_external_flash_texts(d)
        flash_texts_dict = parse_flash_texts(flash_texts_lines)
        all_flash_texts = all_flash_texts | flash_texts_dict

    with open("../assets/gamedata/ExternalTexts.json", "w", encoding="utf-8") as f:
        json.dump(all_flash_texts, f, separators=(',', ':'), sort_keys=True)


if __name__ == "__main__":
    main()
