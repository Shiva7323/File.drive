import os
from app import app
import routes  # noqa: F401

# Expose app for gunicorn
application = app

if __name__ == "__main__":
    # Get port from environment variable (for cloud deployment)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
