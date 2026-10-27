import json, os, time
from pathlib import Path
from openai import OpenAI
from .config import MODEL, ROOT, MEMO_CAP

class BudgetStop(RuntimeError): pass

def live_call(prompt, agent='analysis', cap=None):
    if os.getenv('HR_SKIP_LIVE') == '1':
        return '', {'input_tokens':0,'cached_tokens':0,'output_tokens':0}
    cap = MEMO_CAP if cap is None else cap
    if not (os.getenv('PORTKEY_API_KEY') or os.getenv('OPENAI_API_KEY')):
        raise RuntimeError('No PORTKEY_API_KEY or OPENAI_API_KEY configured')
    key=os.getenv('PORTKEY_API_KEY') or os.getenv('OPENAI_API_KEY')
    kwargs={'api_key':key}
    if os.getenv('PORTKEY_API_KEY'):
        kwargs.update(base_url='https://api.portkey.ai/v1', default_headers={'x-portkey-api-key':key})
    kwargs['timeout']=15.0
    client=OpenAI(**kwargs); started=time.time()
    response=client.chat.completions.create(model=MODEL,messages=[{'role':'user','content':prompt}],max_completion_tokens=32)
    usage=response.usage; inp=getattr(usage,'prompt_tokens',0) or 0; out=getattr(usage,'completion_tokens',0) or 0
    if inp+out>cap: raise BudgetStop('STOPPED_BUDGET')
    detail=getattr(usage,'prompt_tokens_details',None); cached=getattr(detail,'cached_tokens',0) if detail else 0
    log=ROOT/'logs'; log.mkdir(exist_ok=True)
    with (log/'usage.jsonl').open('a') as f: f.write(json.dumps({'timestamp':time.time(),'agent':agent,'model':MODEL,'input_tokens':inp,'cached_input_tokens':cached,'output_tokens':out,'latency_ms':round((time.time()-started)*1000),'mode':os.getenv('MODE','optimized')})+'\n')
    return response.choices[0].message.content or '', {'input_tokens':inp,'cached_tokens':cached,'output_tokens':out}

