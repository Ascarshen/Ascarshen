import requests
import json
import random
import re
import time
import os

NOTION_API_KEY = os.getenv("NOTION_API_KEY")
if NOTION_API_KEY is None:
    raise ValueError("❌ NOTION_API_KEY is not set! Please configure it in GitHub Secrets.")
DATABASE_ID = "1b48dad0e6cd8040a7dff15081f5c956"
SEARCH_URL = "https://api.notion.com/v1/search"
NOTION_API_URL = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"

headers = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def search_notion():
    data = {"query": "", "page_size": 100}
    response = requests.post(SEARCH_URL, headers=headers, json=data)
    
    if response.status_code == 200:
        results = response.json().get("results", [])
        for item in results:
            print(json.dumps(item, indent=4, ensure_ascii=False))  
    else:
        print("❌ Error:", response.status_code, response.text)
        
def fetch_notion_data():
    all_records = []
    has_more = True
    next_cursor = None

    while has_more:
        payload = {"page_size": 100}
        if next_cursor:
            payload["start_cursor"] = next_cursor

        response = requests.post(NOTION_API_URL, headers=headers, json=payload)

        if response.status_code == 200:
            data = response.json()
            all_records.extend(data.get("results", []))
            has_more = data.get("has_more", False)
            next_cursor = data.get("next_cursor", None)
            time.sleep(0.5)
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            return []

    return all_records

def get_random_quote():
    records = fetch_notion_data()
    if not records:
        return "No data available", "Unknown"

    valid_records = []
    for item in records:
        properties = item.get("properties", {})
        quote_data = properties.get("Quote", {}).get("title", [])  
        author_data = properties.get("Author", {}).get("select", {})

        if quote_data and author_data:

            quote_text = " ".join([q["text"]["content"] for q in quote_data])

            author_name = author_data["name"]
            valid_records.append((quote_text, author_name))

    if not valid_records:
        return "No valid quotes found", "Unknown"

    return random.choice(valid_records)



def update_readme_with_quote():
    """Replace placeholder text in README.md with the new random quote."""
    quote, author = get_random_quote()
    new_motto = f'"{quote}"\n\n<div align="right"> {author}</div>'

    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()

    # Regex to replace text between <!-- START_SECTION:daily_motto --> and <!-- END_SECTION:daily_motto -->
    pattern = r"(<!-- START_SECTION:daily_motto -->)(.*?)(<!-- END_SECTION:daily_motto -->)"
    replacement = r"\1\n" + new_motto + r"\n\3"
    updated_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(updated_content)

if __name__ == "__main__":
    update_readme_with_quote()