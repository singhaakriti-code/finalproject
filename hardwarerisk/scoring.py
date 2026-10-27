import json
from pathlib import Path
_TAX={x['code'] for x in json.loads((Path(__file__).parent.parent/'data/taxonomy.json').read_text())}
def score_findings(findings):
    per={}
    for f in findings:
        if f.get('code') not in _TAX: continue
        per[f['code']]=max(per.get(f['code'],0), int(f['severity'])*int(f['likelihood']))
    score=min(100, round(sum(per.values())*100/60)); label='Proceed to partner meeting' if score<30 else ('Dig deeper' if score<=60 else 'Pass for now')
    return {'score':score,'label':label,'per_code':per}

