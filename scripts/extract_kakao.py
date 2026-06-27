from bs4 import BeautifulSoup
from .mhtml_utils import extract_html_from_mhtml_bytes

def extract_kakaopage_chapter(file_path):
    """Extract chapter text from a saved KakaoPage MHTML file."""
    with open(file_path, 'rb') as f:
        raw = f.read()

    html = extract_html_from_mhtml_bytes(raw)
    soup = BeautifulSoup(html, 'html.parser')

    template = soup.find('template', attrs={'shadowmode': 'open'}) or soup.find('template', attrs={'shadowrootmode': 'open'})
    if not template:
        raise ValueError("No shadow DOM template found")

    inner_html = ''.join(str(c) for c in template.contents)
    inner = BeautifulSoup(inner_html, 'html.parser')

    container = inner.find('div', class_='DC2CN') or inner.find('div', class_='DC1CN')
    if container and container.get('class', []) == ['DC1CN']:
        container = container.find('div', class_='DC2CN')

    paragraphs = container.find_all('p', attrs={'data-p-id': True}) if container else inner.find_all('p')
    lines = [
        p.get_text(strip=True)
        for p in paragraphs
        if p.get_text(strip=True) and p.get_text(strip=True) not in ('\xa0', '&nbsp;', '')
    ]
    return '\n\n'.join(lines)