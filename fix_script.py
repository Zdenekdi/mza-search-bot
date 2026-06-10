with open("src/mza_search/ai_reader.py", "r") as f:
    content = f.read()

bad_snippet = """            # Starší HTR+ API (které používá většina historických modelů)
            htr_payload = {"docId": doc_id, "pageList": {"pages": [{"pageId": page_id}]}, "htrId": self.model_id}
            htr_resp = requests.post(f"{self.base_url}/pylaia/process", json=htr_payload, cookies=cookies)
            
            # Transkribus má někdy modely jako PyLaia, někdy jako HTR+, zkusíme oba endpointy pokud jeden selže
            if htr_resp.status_code != 200:
                htr_resp = requests.post(f"{self.base_url}/htr/process", json=htr_payload, cookies=cookies)"""

good_snippet = """            payload = {"docId": doc_id, "pageList": {"pages": [{"pageId": page_id}]}}
            htr_url = f"{self.base_url}/pylaia/{self.col_id}/{self.model_id}/recognition?id={doc_id}&pages=1"
            htr_resp = requests.post(htr_url, cookies=cookies, json=payload)
            
            if htr_resp.status_code == 404:
                htr_url = f"{self.base_url}/recognition/{self.col_id}/{self.model_id}/htrCITlab?id={doc_id}&pages=1"
                htr_resp = requests.post(htr_url, cookies=cookies, json=payload)"""

if bad_snippet in content:
    content = content.replace(bad_snippet, good_snippet)
    with open("src/mza_search/ai_reader.py", "w") as f:
        f.write(content)
    print("Fixed!")
else:
    print("Snippet not found")
