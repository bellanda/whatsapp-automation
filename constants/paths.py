import os
import pathlib

# Caminhos base
BASE_PATH = pathlib.Path(__file__).parent.parent

# Pasta de dados
DATA_DIR = BASE_PATH / "data"

# Garantir que a pasta data existe
os.makedirs(DATA_DIR, exist_ok=True)

# Arquivo para salvar o progresso
PROGRESS_FILE = DATA_DIR / "progress.json"
