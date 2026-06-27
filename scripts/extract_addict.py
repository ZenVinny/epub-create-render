import os
from bs4 import BeautifulSoup
from .mhtml_utils import extract_html_from_mhtml_bytes

def extract_addict_chapter(file_path):
    """Extract title and text from an Addict Habitat MHTML file."""
    with open(file_path, 'rb') as f:
        raw = f.read()

    html = extract_html_from_mhtml_bytes(raw)
    soup = BeautifulSoup(html, 'html.parser')

    article = soup.find('article', class_='markdown-article')
    if not article:
        article = soup.find('article')
    if not article:
        raise ValueError("Could not find <article> element.")

    # Title
    title_tag = article.find('h1')
    title = title_tag.get_text(strip=True) if title_tag else os.path.splitext(os.path.basename(file_path))[0]

    # Paragraphs
    paragraphs = []
    for p in article.find_all('p', recursive=False):
        text = p.get_text(strip=True)
        if text:
            paragraphs.append(text)
    if not paragraphs:  # fallback
        for p in article.find_all('p'):
            text = p.get_text(strip=True)
            if text:
                paragraphs.append(text)

    return title, '\n\n'.join(paragraphs)