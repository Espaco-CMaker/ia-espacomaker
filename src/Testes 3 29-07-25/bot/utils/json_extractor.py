import re, json
def extract_first_json(txt: str) -> dict:
    m = re.search(r"\{.*?\}", txt, flags=re.S)
    if not m: raise ValueError("sem JSON")
    return json.loads(m.group(0))
