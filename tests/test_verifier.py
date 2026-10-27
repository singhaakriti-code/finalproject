from hardwarerisk.ingest import Chunk
from hardwarerisk.verifier import verify
def test_quotes():
    c=Chunk('D1-C1','x.md','The battery has no certification.')
    good=[{'code':'REG-1','severity':3,'likelihood':3,'citations':[{'chunk_id':'D1-C1','quote':'battery has no certification'}]}]
    bad=[{'code':'REG-1','severity':3,'likelihood':3,'citations':[{'chunk_id':'D1-C1','quote':'fabricated'}]}]
    assert len(verify(good,[c])[0])==1 and len(verify(bad,[c])[0])==0

