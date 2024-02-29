import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

if getattr(sys, 'frozen', False):
    ROOT_DIR = Path(sys.executable).parent.absolute()
else:
    ROOT_DIR = Path(__file__).parent.parent.absolute()
    
ABIS_DIR = os.path.join(ROOT_DIR, 'data', 'abis')

with open('private_keys.txt', 'r') as file:
    PRIVATE_KEYS = [row.strip() for row in file]
    
with open('proxies.txt', 'r') as file:
    PROXIES = [row.strip() for row in file]