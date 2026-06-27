import os
import re
from bs4 import BeautifulSoup

try:
    from .mhtml_utils import extract_html_from_mhtml_bytes
except ImportError:
    from mhtml_utils import extract_html_from_mhtml_bytes


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
    if title_tag:
        title = title_tag.get_text(strip=True)
        if title.startswith("Book 1 "):
            title = title[7:]
    else:
        title = os.path.splitext(os.path.basename(file_path))[0]

    # Extract paragraphs, skipping any that are empty or only whitespace
    paragraphs = []
    for p in article.find_all('p', recursive=False):
        text = p.get_text(separator=' ', strip=False)
        # Collapse whitespace and strip leading/trailing spaces
        cleaned = re.sub(r'\s+', ' ', text).strip()
        if cleaned:
            paragraphs.append(cleaned)

    # Fallback: if no direct children paragraphs, get all
    if not paragraphs:
        for p in article.find_all('p'):
            text = re.sub(r'\s+', ' ', p.get_text(separator=' ', strip=False)).strip()
            if text:
                paragraphs.append(text)

    return title, '\n\n'.join(paragraphs)