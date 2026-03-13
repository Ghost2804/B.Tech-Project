# ## Step- 1

# import requests

# BASE_URL = "https://api.semanticscholar.org/graph/v1/paper/search"

# def search_semanticscholar(query, max_results=10, api_key='4kA6Y6j2xB8Qckgn4FTGp7QYMAnJIAqg8AY5kakY'):
#     """
#     Search Semantic Scholar API for papers.
#     Returns list of dicts with only the required fields for MVP:
#     {paperId, title, abstract, authors, year, venue, doi, url, pdf_url}
#     """
#     params = {
#         "query": query,
#         "limit": max_results,
#         "fields": ",".join([
#             "paperId",
#             "title",
#             "abstract",
#             "authors.name",
#             "year",
#             "venue",
#             "externalIds",
#             "url",
#             "openAccessPdf",
#             "citationCount"
#         ])
#     }
#     headers = {}
#     if api_key:
#         headers["x-api-key"] = api_key

#     resp = requests.get(BASE_URL, params=params, headers=headers, timeout=10)
#     resp.raise_for_status()
#     data = resp.json()

#     papers = []
#     for item in data.get("data", []):
#         authors = [a.get("name") for a in item.get("authors", [])]
#         external_ids = item.get("externalIds", {}) or {}
#         doi = external_ids.get("DOI")
#         open_access = item.get("openAccessPdf") or {}
#         pdf_url = open_access.get("url")

#         papers.append({
#             "paperId": item.get("paperId"),
#             "title": item.get("title"),
#             "abstract": item.get("abstract") or "",
#             "authors": authors,
#             "year": item.get("year"),
#             "venue": item.get("venue"),
#             "doi": doi,
#             "url": item.get("url"),
#             "pdf_url": pdf_url,
#             'citations': item.get('citationCount')
#         })
#     return papers

## Using Sringer API


import requests

def search_semanticscholar(query, max_results=20, api_key='599305d1868ada4180d052e5ca90fba0', offset=0):
    """
    Query Springer Metadata API (v2) for research papers.
    Returns list of dicts in format compatible with existing pipeline.
    """
    # Clean noise words to prevent empty results for slightly conversational queries
    STOP = {'research', 'paper', 'papers', 'article', 'articles', 'study', 'studies', 
            'review', 'survey', 'find', 'search', 'show', 'fetch', 'get', 'give', 'list', 
            'more', 'please', 'using', 'based', 'via', 'deep', 'novel', 'new', 'recent', 
            'papre', 'papres', 'artical', 'articals', 'related', 'about', 'topic'}
    words = [w for w in query.split() if w.lower() not in STOP]
    clean_query = " ".join(words) if words else query

    base_url = "https://api.springernature.com/meta/v1/json"
    params = {
        "q": clean_query,
        "p": max_results,
        "s": offset + 1,  # Springer 'start' is 1-indexed
        "api_key": api_key
    }

    response = requests.get(base_url, params=params, timeout=50)
    response.raise_for_status()
    data = response.json()

    papers = []
    for record in data.get("records", []):
        title = record.get("title")
        abstract = record.get("abstract")
        doi = record.get("doi")
        authors = [a.get("creator") for a in record.get("creators", []) if a.get("creator")]

        # ✅ Safely extract the year from onlinedate or date
        raw_year = record["onlineDate"][:4]
        year = int(raw_year) if raw_year and raw_year.isdigit() else None

        url = record.get("url", [{}])[0].get("value") if record.get("url") else None

        papers.append({
            "title": title,
            "abstract": abstract,
            "authors": authors,
            "year": year,
            "url": url,
            "venue": record.get("publicationName"),
            "doi": doi,
            "issn": record.get("issn"),
        })

    return papers
