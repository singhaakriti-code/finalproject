from pathlib import Path
import subprocess,sys
ROOT=Path(__file__).resolve().parent.parent
with (ROOT/'eval/pytest_summary.txt').open('w') as f: subprocess.run([sys.executable,'-m','pytest','-q'],cwd=ROOT,check=True,stdout=f,stderr=subprocess.STDOUT)
for mode in ('baseline','optimized'): subprocess.run([sys.executable,'-m','eval.run_eval','--mode',mode],cwd=ROOT,check=True)
subprocess.run([sys.executable,'-m','scripts.capture_demo'],cwd=ROOT,check=True)
subprocess.run([sys.executable,'kit/build_submission.py'],cwd=ROOT,check=True)
print('Run all completed.')

