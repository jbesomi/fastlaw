import pandas as pd
import requests
import json
import os
import glob
import subprocess
import sys

r = requests.get('https://api.case.law/v1/jurisdictions/')

# compute mapping dictionary 'jurisdiction_id': 'jurisdiction_slug'
juri = {juri['id']: str(juri['slug']) for juri in r.json()['results']}
juri = pd.DataFrame.from_dict(juri, orient='index', columns=['slug'])

r = requests.get(
    'https://api.case.law/v1/bulk/?body_format=text&filter_type=jurisdiction')

# compute mapping dictionary 'bulk_filter_id': 'jurisdiction_if'
bulk = {juri['filter_id']: [str(juri['id']), bool(juri['public'])]
        for juri in r.json()['results']}
bulk = pd.DataFrame.from_dict(bulk, orient='index', columns=[
                              'download_id', 'public'])

juri_bulk = juri.join(bulk)

#juri_bulk['public'] = juri_bulk['public'].astype('bool')

if len(sys.argv) > 1:

    slug = sys.argv[1]

    if slug == 'all':
        df = juri_bulk
        print("Download all jurisdictions.")
    elif slug == 'public':
        df = juri_bulk[juri_bulk['public'] == True]
        print("Download all public jurisdictions.")
    elif juri_bulk['slug'].str.contains(slug).any():

        # # check if slug is private:
        # if juri_bulk[(juri_bulk['slug'] == slug) &
        #              (juri_bulk['public'] == False)].size > 0:
        #     print("slug ", slug, " is private.")
        #
        #     # check TOKEN exist and is valid:
        #     if token:
        #         df = juri_bulk[juri_bulk['slug'].isin([slug])]
        #         print("Download ", slug, "jurisdiction.")
        #     else:
        #         print("Cannot download ", slug,
        #               "jurisdiction becuse invalid or unpassed token.")
        #         exit()
        # else:
        print("Download ", slug, "jurisdiction.")
        df = juri_bulk[juri_bulk['slug'].isin([slug])]
    else:
        print("slug", slug, "does not exist.")
        exit()
else:
    print("You need to pass a valid slug parameter.")
    exit()

# Download data


def download_all(df, skip=True):
    """
    Given a padas df with column 'slug' and 'download_id', download all bulk data.

    params:
        - if skip is set to True, avoid to download again already present files.
    """
    slug_id = json.loads(df.set_index('slug').to_json())['download_id']
    for (slug, download_id) in slug_id.items():

        if (skip and os.path.isfile('../data/bulk/' + slug + '.jsonl')):
            print(slug + " already present. Skip download.")
            continue

        print("Download and extract the data for ",
              slug, "id: ", download_id, "...", end=" ")

        status = subprocess.run(["./download_single.sh", download_id, slug])
        if status.returncode == 0:
            print("success!")
        else:
            print("failed to download or to extract!")

    list_jsonl = glob.glob("../data/bulk/*.jsonl")
    list_jsonl

    print("The folder 'data' now contains: ", list_jsonl)


download_all(df, skip=True)
