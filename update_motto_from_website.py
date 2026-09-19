import re
import requests
import random
from bs4 import BeautifulSoup

def scrape_quotes(page_num):
    """Scrape a random quote from AZQuotes (computer topics) on page_num."""
    url = f"https://www.azquotes.com/quotes/topics/computer.html?p={page_num}"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch page {page_num}")
        return None
    
    soup = BeautifulSoup(response.text, 'html.parser')
    quote_divs = soup.select('ul.list-quotes li div.wrap-block')
    quotes_data = []

    for div in quote_divs:
        title_tag = div.select_one('a.title')
        if not title_tag:
            continue
        
        quote_text = title_tag.get_text(strip=True)
        
        author_div = div.select_one('div.author')
        if author_div:
            author_a = author_div.select_one('a')
            author = author_a.get_text(strip=True) if author_a else "Unknown"
        else:
            author = "Unknown"
        
        # Clean up whitespace
        quote_text = re.sub(r"\s+", " ", quote_text)
        author = re.sub(r"\s+", " ", author)

        quotes_data.append({
            'quote': quote_text,
            'author': author
        })

    if quotes_data:
        return random.choice(quotes_data)
    return None

def get_random_computer_quote():
    """Pick a random page (1..40 or so) and scrape one quote."""
    # AZQuotes `computer.html` has ~40 pages (as of now), you can adjust as needed
    random_page = random.randint(1, 40)
    return scrape_quotes(random_page)

def update_readme_with_quote(quote_dict):
    """Replace placeholder text in README.md with the new random quote."""
    quote = quote_dict['quote']
    author = quote_dict['author']
    new_motto = f"\"{quote}\" — {author}"

    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()

    # Regex to replace text between <!-- START_SECTION:daily_motto --> and <!-- END_SECTION:daily_motto -->
    pattern = r"(<!-- START_SECTION:daily_motto -->)(.*?)(<!-- END_SECTION:daily_motto -->)"
    replacement = r"\1\n" + new_motto + r"\n\3"
    updated_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(updated_content)

if __name__ == "__main__":
    quote_data = get_random_computer_quote()
    if quote_data:
        update_readme_with_quote(quote_data)
    else:
        print("No quote found. No update to README.")
