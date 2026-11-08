#!/usr/bin/env python3
"""
Auto-update publication stats from Google Scholar.
Run manually or via GitHub Actions (scheduled weekly).
Updates the stats in templates/publications.html and rebuilds the site.
"""
import requests
from bs4 import BeautifulSoup
import re
import sys

SCHOLAR_ID = 'rOnlIMcAAAAJ'
TEMPLATE = 'templates/publications.html'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/120.0.0.0 Safari/537.36'
}


def fetch_scholar_stats():
    """Scrape Google Scholar profile for citation stats."""
    url = f'https://scholar.google.com/citations?user={SCHOLAR_ID}&hl=en'
    r = requests.get(url, headers=HEADERS, timeout=15)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, 'html.parser')
    stats = {}

    # Citation table (Citations, h-index, i10-index)
    table = soup.find('table', id='gsc_rsb_st')
    if table:
        for row in table.find_all('tr')[1:]:
            cols = row.find_all('td')
            if len(cols) >= 2:
                key = cols[0].text.strip().lower().replace('-', '')
                stats[key] = int(cols[1].text.strip())

    # Citations per year
    years = soup.find_all('span', class_='gsc_g_t')
    counts = soup.find_all('span', class_='gsc_g_al')
    stats['by_year'] = {}
    for y, c in zip(years, counts):
        stats['by_year'][y.text.strip()] = int(c.text.strip())

    return stats


def update_template(stats):
    """Update the publications template with fresh stats."""
    with open(TEMPLATE, 'r') as f:
        content = f.read()

    original = content

    # Update total citations
    if 'citations' in stats:
        content = re.sub(
            r'data-count="\d+"(>0</span>\s*<span[^>]*>Citations)',
            f'data-count="{stats["citations"]}"\\1',
            content
        )

    # Update h-index
    if 'hindex' in stats:
        content = re.sub(
            r'data-count="\d+"(>0</span>\s*<span[^>]*>h-index)',
            f'data-count="{stats["hindex"]}"\\1',
            content
        )

    # Update i10-index
    if 'i10index' in stats:
        content = re.sub(
            r'data-count="\d+"(>0</span>\s*<span[^>]*>i10-index)',
            f'data-count="{stats["i10index"]}"\\1',
            content
        )

    # Update citations per year bars
    by_year = stats.get('by_year', {})
    if by_year:
        max_val = max(by_year.values()) if by_year else 1
        for year, count in by_year.items():
            pct = round(count / max_val * 100)
            # Update data-value and bar value
            content = re.sub(
                rf'data-value="\d+">\s*<div class="pubstats-bar__fill" style="--target-height: \d+%;"></div>\s*<span class="pubstats-bar__val">\d+</span>\s*<span class="pubstats-bar__year">{year}</span>',
                f'data-value="{count}">\n                        <div class="pubstats-bar__fill" style="--target-height: {pct}%;"></div>\n                        <span class="pubstats-bar__val">{count}</span>\n                        <span class="pubstats-bar__year">{year}</span>',
                content
            )

    if content != original:
        with open(TEMPLATE, 'w') as f:
            f.write(content)
        print(f'Updated {TEMPLATE} with fresh stats')
        return True
    else:
        print('No changes needed')
        return False


if __name__ == '__main__':
    print('Fetching Google Scholar stats...')
    try:
        stats = fetch_scholar_stats()
        print(f'  Citations: {stats.get("citations", "?")}')
        print(f'  h-index: {stats.get("hindex", "?")}')
        print(f'  i10-index: {stats.get("i10index", "?")}')
        print(f'  By year: {stats.get("by_year", {})}')

        changed = update_template(stats)

        if changed:
            # Rebuild
            import subprocess
            print('Rebuilding site...')
            subprocess.run([sys.executable, 'build.py'], check=True)
            print('Done!')
        else:
            print('Stats unchanged, no rebuild needed.')

    except Exception as e:
        print(f'Error: {e}')
        sys.exit(1)
