import re
import email
from email.policy import default

def extract_html_from_mhtml_bytes(raw_bytes):
    """
    Extract the HTML content from MHTML bytes.
    Returns a decoded HTML string.
    """
    # Attempt to parse as a MIME message
    try:
        msg = email.message_from_bytes(raw_bytes, policy=default)
        for part in msg.walk():
            if part.get_content_type() == 'text/html':
                payload = part.get_payload(decode=True)
                if payload:
                    # Try UTF-8, fallback to latin-1 (never fails)
                    try:
                        return payload.decode('utf-8')
                    except UnicodeDecodeError:
                        return payload.decode('latin-1')
    except Exception:
        pass

    # Fallback: search for HTML tags in the raw bytes
    # Decode with 'replace' to avoid errors
    try:
        text = raw_bytes.decode('utf-8', errors='replace')
    except:
        text = raw_bytes.decode('latin-1')

    # Find the HTML section
    match = re.search(r'<!DOCTYPE\s+html>', text, re.IGNORECASE)
    if not match:
        match = re.search(r'<html', text, re.IGNORECASE)
    if match:
        start = match.start()
        end = re.search(r'</html>', text, re.IGNORECASE)
        if end:
            return text[start:end.end()]
        else:
            return text[start:]

    raise ValueError("Could not extract HTML content from the file.")