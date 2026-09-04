"""Percorsi del progetto: i test girano da qualsiasi cartella."""
import pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
APP_URL   = (ROOT / 'index.html').as_uri()
CODEX_URL = (ROOT / 'codex.html').as_uri()
OUT = ROOT / 'tests' / 'out'
OUT.mkdir(exist_ok=True)
NODE = ROOT / 'node_modules'
