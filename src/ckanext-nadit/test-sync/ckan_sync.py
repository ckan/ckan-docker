import requests
import json
import os

from requests import HTTPError
from json import JSONDecodeError

from pathlib import Path

# Configuration
ckan_cache = 'ckan.cache.json'
ckan_endpoint = 'https://ckan.opendata.swiss'
ckan_query = '/api/3/action/package_search?' + \
 'fq=organization:bundesamt-fur-statistik-bfs' + '&' + \
 'q=groups:tourism' + '&' + \
 'rows=1000'

# Locate the cache
ckan_cache = Path(ckan_cache)

if ckan_cache.is_file():
    # Load from a file cache
    with open(ckan_cache, 'r') as f:
        ckan_data = f.read()
        print('Loaded cache:', ckan_cache)

else:
    # Fetch from endpoint
    url = ckan_endpoint + ckan_query
    try:
        response = requests.get(url)
        # Process error conditions (404 etc.)
        response.raise_for_status()
    except HTTPError as http_err:
        print(f'HTTP error: {http_err}')
        exit()
    else:
        # Get the response and cache it
        ckan_data = response.text
        with open(ckan_cache, 'w') as f:
            f.write(ckan_data)
            print('Saved cache:', ckan_cache)

# Load the JSON response
try:
    ckan_json = json.loads(ckan_data)
    results = ckan_json['result']['results']
except JSONDecodeError as err:
    print(f'Parsing error: {err}')
    exit()

# Show a quick summary
for r in results:
    print(r['url'])
print(len(results), 'rows loaded')
