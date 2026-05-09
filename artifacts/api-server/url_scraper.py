import re
import requests
from bs4 import BeautifulSoup

HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/120.0.0.0 Safari/537.36'
    ),
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
}

def scrape(url):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=12, allow_redirects=True)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')

        for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'noscript', 'meta', 'link']):
            tag.decompose()

        # Try to extract structured job content first
        job_text = _extract_job_sections(soup)
        if job_text and len(job_text) > 100:
            return _clean(job_text)[:4000]

        # Fall back to full page text
        text = soup.get_text(separator=' ', strip=True)
        return _clean(text)[:4000]

    except requests.exceptions.Timeout:
        return None, "Request timed out. The website took too long to respond."
    except requests.exceptions.ConnectionError:
        return None, "Could not connect to the URL. Check if the link is valid."
    except requests.exceptions.HTTPError as e:
        return None, f"HTTP error {e.response.status_code} when accessing the URL."
    except Exception as e:
        return None, f"Failed to scrape URL: {str(e)}"

def scrape_with_status(url):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=12, allow_redirects=True)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')

        for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'noscript']):
            tag.decompose()

        title = soup.find('title')
        page_title = title.get_text(strip=True) if title else url

        job_text = _extract_job_sections(soup)
        if job_text and len(job_text) > 100:
            text = _clean(job_text)[:4000]
        else:
            text = _clean(soup.get_text(separator=' ', strip=True))[:4000]

        return {
            'success': True,
            'text': text,
            'title': page_title,
            'word_count': len(text.split()),
            'url': url
        }
    except requests.exceptions.Timeout:
        return {'success': False, 'error': 'Request timed out. The website took too long to respond.'}
    except requests.exceptions.ConnectionError:
        return {'success': False, 'error': 'Could not connect. Check if the URL is accessible.'}
    except requests.exceptions.HTTPError as e:
        return {'success': False, 'error': f'HTTP {e.response.status_code}: Could not access this page.'}
    except Exception as e:
        return {'success': False, 'error': f'Scrape failed: {str(e)[:100]}'}

def _extract_job_sections(soup):
    parts = []
    selectors = [
        '[class*="job-desc"]', '[class*="job_desc"]', '[class*="jobDesc"]',
        '[class*="job-detail"]', '[class*="job-content"]', '[class*="posting"]',
        '[id*="job-desc"]', '[id*="description"]', '[class*="description"]',
        'article', 'main', '.content', '#content', '[role="main"]'
    ]
    for sel in selectors:
        try:
            el = soup.select_one(sel)
            if el:
                parts.append(el.get_text(separator=' ', strip=True))
                if len(' '.join(parts)) > 500:
                    break
        except Exception:
            continue

    # Also grab headings and list items
    for tag in soup.find_all(['h1', 'h2', 'h3', 'li', 'p']):
        txt = tag.get_text(strip=True)
        if 10 < len(txt) < 500:
            parts.append(txt)

    return ' '.join(parts)

def _clean(text):
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s₹$%@.,:;!?/\-\(\)\'\"]+', ' ', text)
    return text.strip()
