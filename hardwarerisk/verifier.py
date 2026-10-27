import json
from pathlib import Path
def verify(findings,chunks):
    by={c.id:c for c in chunks}; tax={x['code'] for x in json.loads((Path(__file__).parent.parent/'data/taxonomy.json').read_text())}; valid=[]; dropped=[]; total=0; good=0
    for f in findings:
        ok=False
        for cite in f.get('citations',[]):
            total+=1; c=by.get(cite.get('chunk_id')); quote=' '.join(cite.get('quote','').split())
            if c and quote.lower() in ' '.join(c.text.split()).lower(): good+=1; ok=True
        if f.get('code') not in tax or not ok: dropped.append({'finding':f,'reason':'unknown taxonomy code or no valid citation'})
        else: valid.append(f)
    return valid,dropped,{'citations_total':total,'citations_valid':good}

