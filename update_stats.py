#!/usr/bin/env python3
"""
Auto-update publication stats from OpenAlex API.
Run manually or via GitHub Actions (scheduled weekly).
Updates the stats in templates/publications.html and rebuilds the site.

Uses OpenAlex (https://openalex.org) instead of scraping Google Scholar,
because Google Scholar blocks automated requests from cloud IPs.
"""
import requests
import json
import re
import sys

ORCID = '0000-0002-8868-9302'
TEMPLATE = 'templates/publications.html'

# OpenAlex polite pool: provide contact email for faster responses
OPENALEX_EMAIL = 'mail.a.roman@csic.es'


def fetch_openalex_stats():
    """Fetch citation stats from OpenAlex API using ORCID."""
    url = 'https://api.openalex.org/authors'
    params = {
        'filter': f'orcid:{ORCID}',
        'mailto': OPENALEX_EMAIL,
    }
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    data = r.json()

    if not data.get('results'):
        raise ValueError(f'No author found in OpenAlex for ORCID {ORCID}')

    author = data['results'][0]
    stats = {
        'citations': author.get('cited_by_count', 0),
        'hindex': author.get('summary_stats', {}).get('h_index', 0),
        'i10index': author.get('summary_stats', {}).get('i10_index', 0),
    }

    # Citations per year (OpenAlex provides counts_by_year)
    by_year = {}
    for entry in author.get('counts_by_year', []):
        year = entry.get('year')
        cited = entry.get('cited_by_count', 0)
        if year and cited > 0:
            by_year[str(year)] = cited
    stats['by_year'] = by_year

    return stats


def update_template(stats):
    """Update the publications template with fresh stats."""
    with open(TEMPLATE, 'r') as f:
        content = f.read()

    original = content

    # Update f_rings Jinja set block: citations, h-index, i10-index
    if 'citations' in stats:
        content = re.sub(
            r"(\(')\d+(',\s*'Citations')",
            rf"\g<1>{stats['citations']}\2",
            content
        )
    if 'hindex' in stats:
        content = re.sub(
            r"(\(')\d+(',\s*'h-index')",
            rf"\g<1>{stats['hindex']}\2",
            content
        )
    if 'i10index' in stats:
        content = re.sub(
            r"(\(')\d+(',\s*'i10-index')",
            rf"\g<1>{stats['i10index']}\2",
            content
        )

    # Update canvas chart data array
    by_year = stats.get('by_year', {})
    if by_year:
        # Build new data array sorted by year
        sorted_years = sorted(by_year.items(), key=lambda x: int(x[0]))
        entries = ','.join(f"{{y:'{y}',v:{v}}}" for y, v in sorted_years)
        new_data = f'var data=[{entries}];'
        content = re.sub(
            r'var data=\[.*?\];',
            new_data,
            content
        )
        # Update mx (max value for chart scale, round up to nice number)
        max_val = max(by_year.values())
        mx = int((max_val * 1.15 // 50 + 1) * 50)  # ~15% headroom, round to 50
        content = re.sub(
            r'var mx=\d+,',
            f'var mx={mx},',
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
    print('Fetching stats from OpenAlex API...')
    try:
        stats = fetch_openalex_stats()
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
