from dashboard.app import app
from config import DASHBOARD_HOST, DASHBOARD_PORT, DEBUG_MODE
if __name__ == '__main__':
    app.run(debug=DEBUG_MODE, host=DASHBOARD_HOST, port=DASHBOARD_PORT)