import re
from dataclasses import dataclass
from pathlib import Path

INJECTION = re.compile(r'ignore (?:all )?(?:previous|prior) instructions|system prompt|you are now|ai reviewers|rate this company|do not mention|as an ai model|^\s*system:', re.I|re.M)
@dataclass
class Chunk:
    id: str; doc: str; text: str; flagged: bool = False

def ingest(folder):
    chunks=[]; events=[]
    files=sorted(Path(folder).glob('*.md'))+sorted(Path(folder).glob('*.txt'))
    for di, path in enumerate(files, 1):
        words=path.read_text(errors='ignore').split()
        for ci in range(0, len(words), 120):
            text=' '.join(words[ci:ci+120]); flagged=bool(INJECTION.search(text))
            c=Chunk(f'D{di}-C{ci//120+1}', path.name, text, flagged); chunks.append(c)
            if flagged: events.append({'agent':'Ingest','action':'guardrail','detail':f'Flagged suspicious instructions in {c.id} ({path.name})'})
    return chunks, events

