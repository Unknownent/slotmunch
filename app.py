import os
from dotenv import load_dotenv
load_dotenv()

from flask import Flask, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder=None)
CORS(app)

FRONTEND_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'frontend')

from routes.auth import auth_bp
from routes.menu import menu_bp
from routes.orders import orders_bp
from routes.staff import staff_bp
from routes.analytics import analytics_bp

app.register_blueprint(auth_bp, url_prefix='/api')
app.register_blueprint(menu_bp, url_prefix='/api')
app.register_blueprint(orders_bp, url_prefix='/api')
app.register_blueprint(staff_bp, url_prefix='/api')
app.register_blueprint(analytics_bp, url_prefix='/api')

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    if path == '':
        return send_from_directory(FRONTEND_FOLDER, 'index.html')

    full_path = os.path.join(FRONTEND_FOLDER, path)

    if os.path.isfile(full_path):
        return send_from_directory(FRONTEND_FOLDER, path)

    html_path = f"{path}.html"
    if os.path.isfile(os.path.join(FRONTEND_FOLDER, html_path)):
        return send_from_directory(FRONTEND_FOLDER, html_path)

    return send_from_directory(FRONTEND_FOLDER, 'index.html')

if __name__ == '__main__':
    app.run(debug=True)