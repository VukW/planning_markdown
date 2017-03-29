from app import app
from config import PORT, DEBUG
app.run(host='0.0.0.0', port=PORT, debug=DEBUG, threaded=True)
