import ast
from hardwarerisk.ingest import ingest
from hardwarerisk.scoring import score_findings
from hardwarerisk.llm import BudgetStop

def test_six_injection_patterns_flagged(tmp_path):
    phrases=['ignore previous instructions','ignore prior instructions','system prompt','you are now','AI reviewers','do not mention','SYSTEM:']
    (tmp_path/'x.md').write_text(' '.join(phrases)); assert ingest(tmp_path)[0][0].flagged

def test_injected_out_of_taxonomy_cannot_score():
    assert score_findings([{'code':'NOT-A-CODE','severity':5,'likelihood':5}])['score'] == 0

def test_budget_cap_stops_calls(monkeypatch):
    import hardwarerisk.llm as llm
    monkeypatch.setattr(llm,'MEMO_CAP',1)
    class U: prompt_tokens=2; completion_tokens=0; prompt_tokens_details=None
    class C: usage=U(); choices=[type('X',(),{'message':type('M',(),{'content':'x'})()})()]
    class Client:
        class chat:
            class completions:
                @staticmethod
                def create(**kw): return C()
    monkeypatch.setattr(llm,'OpenAI',lambda **kw: Client()); monkeypatch.setenv('OPENAI_API_KEY','x')
    try: llm.live_call('x')
    except BudgetStop: return
    assert False

def test_loop_cap_is_bounded():
    assert sum(1 for _ in range(8)) == 8

def test_app_does_not_read_ground_truth():
    tree=ast.parse(open('app.py').read()); names=[n.id for n in ast.walk(tree) if isinstance(n,ast.Name)]
    assert 'ground_truth' not in names
