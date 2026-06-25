import re
from ebooklib import epub

def convert_markdown(text):
    """
    Convert *italic* and **bold** markdown to HTML tags.
    Process bold first to avoid interference.
    """
    # Bold: **text** → <b>text</b>
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    # Italic: *text* → <i>text</i>
    text = re.sub(r'\*(.+?)\*', r'<i>\1</i>', text)
    return text

def build_epub(chapters, title, output_path, author="Unknown"):
    book = epub.EpubBook()
    book.set_identifier('kakao_extract')
    book.set_title(title)
    book.set_language('en')
    book.add_author(author)
    spine = ['nav']
    toc = []
    for i, ch in enumerate(chapters, 1):
        e = epub.EpubHtml(title=ch.get('title', f'Chapter {i}'), file_name=f'chapter_{i:04d}.xhtml', lang='en')
        content = f"<h1>{ch.get('title', f'Chapter {i}')}</h1>\n"
        for p in ch['text'].split('\n\n'):
            if p.strip():
                # Apply markdown conversion to each paragraph
                processed = convert_markdown(p.strip())
                content += f"<p>{processed}</p>\n"
        e.content = content
        book.add_item(e)
        spine.append(e)
        toc.append(epub.Link(f'chapter_{i:04d}.xhtml', ch.get('title', f'Chapter {i}'), f'chap_{i}'))
    book.toc = toc
    book.add_item(epub.EpubNav())
    book.spine = spine
    epub.write_epub(output_path, book, {})