import os
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
for p in (ROOT / '.env', ROOT.parent / '.env'):
    if p.exists(): load_dotenv(p, override=False)
MODE = os.getenv('MODE', 'optimized')
MODEL = 'gpt-6-luna' if os.getenv('PORTKEY_API_KEY') else os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
MEMO_CAP = int(os.getenv('MEMO_TOKEN_CAP', '120000'))
DAY_CAP = int(os.getenv('DAY_TOKEN_CAP', '1500000'))

