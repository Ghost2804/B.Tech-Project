
import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the 'app' directory to the python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.app import app

if __name__ == '__main__':
    print("Starting Flask app...")
    # Use stat reloader to avoid watchdog restart glitches on Windows
    app.run(
        debug=True, 
        port=5000,
        use_reloader=True,
        reloader_type='stat'  # Prevents watchdog restart loop issues
    )
