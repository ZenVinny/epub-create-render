import re
from bs4 import BeautifulSoup

def extract_addict_chapter(file_path):
    """
    Extracts chapter title and text from an Addict Habitat MHTML file.
    Returns (title, text) where text is paragraphs joined by double newline.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Locate the HTML part – look for DOCTYPE and then up to closing </html>
    match = re.search(r'<!DOCTYPE html>', content, re.IGNORECASE)
    if not match:
        raise ValueError("No HTML content found in the file.")
    start = match.start()
    end = re.search(r'</html>', content, re.IGNORECASE)
    if not end:
        # If no closing </html>, take the rest of the file
        html_content = content[start:]
    else:
        html_content = content[start:end.end()]

    soup = BeautifulSoup(html_content, 'html.parser')

    # Locate the article container
    article = soup.find('article', class_='markdown-article')
    if not article:
        # Fallback: try to find any article
        article = soup.find('article')
    if not article:
        raise ValueError("Could not find <article> element in the page.")

    # Extract title: first <h1> inside article
    title_tag = article.find('h1')
    if title_tag:
        title = title_tag.get_text(strip=True)
    else:
        # If no h1, use filename without extension
        import os
        title = os.path.splitext(os.path.basename(file_path))[0]

    # Extract all paragraphs inside the article (direct <p> children)
    paragraphs = []
    for p in article.find_all('p', recursive=False):  # only direct children
        text = p.get_text(strip=True)
        if text:
            paragraphs.append(text)

    # If no paragraphs found, try all <p> inside article (including nested)
    if not paragraphs:
        for p in article.find_all('p'):
            text = p.get_text(strip=True)
            if text:
                paragraphs.append(text)

    # Join paragraphs with double newline
    full_text = '\n\n'.join(paragraphs)

    return title, full_text
