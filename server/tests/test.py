from ..lib.explorer import explore

response = explore(query="HUNTER X HUNTER", max_results=3, doc_chars_max=6000, load_all_available_meta=True)
print(response)