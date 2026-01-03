"""WSGI configuration for PythonAnywhere deployment.

PythonAnywhere expects a file with an 'application' variable that points
to your WSGI application.

Usage:
    1. Upload this file to PythonAnywhere
    2. Configure Web tab to point to this file
    3. Set Python version to 3.10+
    4. Configure environment variables in Web tab or .env file
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import the FastAPI app
from backend.app.main import app

# PythonAnywhere expects 'application' variable
application = app

# Optional: Add startup logging
if __name__ != "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.info("🚀 Reading App backend started on PythonAnywhere")
    logger.info(f"📁 Project root: {project_root}")

