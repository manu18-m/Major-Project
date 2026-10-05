#!/usr/bin/env python
"""SIH 26165 - single-command project launcher."""
import os, sys, subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
REQ = BASE_DIR / 'requirements.txt'
VENV = BASE_DIR / '.venv'
VENV_PY = VENV / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
MIN_PY = (3, 10)

def run(cmd):
    return subprocess.check_call(cmd, cwd=str(BASE_DIR))

def find_modern_python():
    candidates = []
    if os.name == 'nt':
        candidates += [['py','-3.11'], ['py','-3.12'], ['py','-3.10']]
    for launcher in candidates:
        try:
            p = subprocess.run(launcher + ['-c','import sys; print(sys.executable)'], capture_output=True, text=True, check=True)
            path = Path(p.stdout.strip())
            if path.exists() and sys.version_info >= (3,10):
                return path
        except Exception:
            pass
    return None

def ensure_python():
    if sys.version_info >= MIN_PY:
        return
    if not VENV_PY.exists():
        py = find_modern_python()
        if not py:
            print('SIH 26165 requires Python 3.10+ (Python 3.11 recommended).')
            print('Install Python 3.11+ and run this same command again.')
            raise SystemExit(1)
        print('[SIH 26165] Creating local Python environment...')
        run([str(py), '-m', 'venv', str(VENV)])
    os.execv(str(VENV_PY), [str(VENV_PY), str(BASE_DIR/'manage.py'), *sys.argv[1:]])

def deps_ready():
    try:
        import django, pandas, numpy, sklearn, joblib  # noqa
        return True
    except Exception:
        return False

def ensure_dependencies():
    if deps_ready():
        return
    print('[SIH 26165] Installing all project requirements (first run)...')
    run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'])
    run([sys.executable, '-m', 'pip', 'install', '-r', str(REQ)])

def ensure_model():
    model = BASE_DIR / 'ml' / 'sif_classifier.joblib'
    if model.exists():
        return
    print('[SIH 26165] Preparing demonstration NLP model...')
    from ml.train_model import train
    train()

def ensure_database():
    if len(sys.argv) > 1 and sys.argv[1] in {'runserver','migrate'}:
        from django.core.management import call_command
        call_command('migrate', interactive=False, verbosity=0)

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE','sif_engine.settings')
    ensure_python()
    ensure_dependencies()
    ensure_model()
    from django.core.management import execute_from_command_line
    import django
    django.setup()
    ensure_database()
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
