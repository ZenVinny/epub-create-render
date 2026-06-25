import re
from bs4 import BeautifulSoup

def extract_kakaopage_chapter(file_path):
    """Extract chapter text from a saved KakaoPage MHTML file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the HTML part
    match = re.search(r'<!DOCTYPE html>', content, re.IGNORECASE)
    if not match:
        raise ValueError("No HTML found")
    html = content[match.start():]
    end = re.search(r'</html>', html, re.IGNORECASE)
    if end:
        html = html[:end.end()]
    
    soup = BeautifulSoup(html, 'html.parser')
    template = soup.find('template', attrs={'shadowmode': 'open'}) or soup.find('template', attrs={'shadowrootmode': 'open'})
    if not template:
        raise ValueError("No shadow DOM template found")
    
    inner = BeautifulSoup(''.join(str(c) for c in template.contents), 'html.parser')
    container = inner.find('div', class_='DC2CN') or inner.find('div', class_='DC1CN')
    if container and container.get('class', []) == ['DC1CN']:
        container = container.find('div', class_='DC2CN')
    
    paragraphs = container.find_all('p', attrs={'data-p-id': True}) if container else inner.find_all('p')
    lines = [p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True) and p.get_text(strip=True) not in ('\xa0', '&nbsp;', '')]
    return '\n\n'.join(lines)