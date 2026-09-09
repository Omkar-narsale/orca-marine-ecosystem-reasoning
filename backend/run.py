import os
import sys
from pathlib import Path

# Ensure project root is in sys.path and PYTHONPATH for uvicorn reloader subprocesses
project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)
if "PYTHONPATH" in os.environ:
    os.environ["PYTHONPATH"] = project_root + os.pathsep + os.environ["PYTHONPATH"]
else:
    os.environ["PYTHONPATH"] = project_root

import uvicorn

if __name__ == "__main__":
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, reload=True)

