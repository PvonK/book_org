# parser.py

import re
import os
from .extractor import extract_series, extract_year, extract_file_extension


def clean_filename(name):
    name = name.strip()
    name = name.replace('_ ', ': ')
    name = name.replace('_', ' ')
    name = name.replace('–', '-')
    name = re.sub(r'\s+', ' ', name).strip()
    return name


def parse_annas_filename(filename):
    filename = os.path.splitext(filename)[0]
    title, authors = filename.split(" -- ", 3)[:2]
    return {"title": title, "authors": authors}


def parse_filename(filename):
    if "Anna’s Archive" in filename:
        return parse_annas_filename(filename)

    result = {
        'series': None,
        'authors': None,
        'editors': None,
        'title': None,
        'publisher': None,
        'year': None,
        'volume': None,
        'extension': None,
    }

    # 1. Remove extension
    name, result["extension"] = extract_file_extension(filename)

    # 2. Clean up and normalize
    name = clean_filename(name)

    # 3. Extract bracketed or parenthetical series
    series_match = extract_series(name)
    if series_match:
        result['series'], name = series_match

    # 4. Extract year + publisher (e.g. (2001, Wiley))
    match_year = extract_year(name)
    if match_year:
        result['year'], result['publisher'], name = match_year

    # 5. Handle year-only case
    elif re.search(r'\((\d{4})\)$', name):
        result['year'] = re.search(r'\((\d{4})\)$', name).group(1)
        name = re.sub(r'\((\d{4})\)$', '', name).strip()

    # 6. Remove trailing junk (e.g., z-lib, libgen)
    name = re.sub(r'-?for\(z-lib.*?\)', '', name).strip()
    name = re.sub(r'-?libgen.*$', '', name).strip()

    # 7. Split authors and title (use ` - ` delimiter)
    if ' - ' in name:
        people_part, title_part = name.split(' - ', 1)

        if title_part.count("-") > 3:
            title_part = title_part.replace("-", " ")
        # This here is to separate the publisher from the title
        # I only do it here, when authors are separated, because I feel
        # like only the ones with correctly formated author names would
        # also have publishing data
        elif title_part.count("-") > 0:
            title_part = "-".join(title_part.split("-", -2)[:-1])

        result['title'] = title_part.strip()
        result['authors'] = people_part.strip()

    elif " by " in name:
        title_part, people_part = name.split(' by ', 1)

        if title_part.count("-") > 3:
            title_part = title_part.replace("-", " ")
        elif title_part.count("-") > 0:
            title_part = "-".join(title_part.split("-", -2)[:-1])

        result['title'] = title_part.strip()
        result['authors'] = people_part.strip()
    else:
        # Fallback: title only
        result['title'] = name.strip()

    # 8. Check for volume in title
    volume_match = re.search(r'(Volume|V\.)\s*(\d+)', result['title'] or '')
    if volume_match:
        result['volume'] = volume_match.group(2)

    return result
