import re
def scan(text): return bool(re.search(r'ignore (?:all )?(?:previous|prior) instructions|system prompt|ai reviewers|do not mention', text, re.I))

