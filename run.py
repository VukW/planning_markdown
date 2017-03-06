from app import app
from config import PORT
app.run(port=8000, debug=True, threaded=True)
