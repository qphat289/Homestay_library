from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app import app

# Vercel sẽ tự động nhận biến app này 