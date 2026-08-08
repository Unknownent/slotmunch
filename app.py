import os
from dotenv import load_dotenv
load_dotenv()

from flask import Flask, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder='frontend', static_url_path='')
CORS(app)

from routes.auth import auth_bp
from routes.menu import menu_bp
from routes.orders import orders_bp
from routes.staff import staff_bp
from routes.analytics import analytics_bp

app.register_blueprint(auth_bp)
app.register_blueprint(menu_bp)
app.register_blueprint(orders_bp)
app.register_blueprint(staff_bp)
app.register_blueprint(analytics_bp)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    if path == '':
        return send_from_directory(app.static_folder, 'index.html')

    full_path = os.path.join(app.static_folder, path)

    if os.path.isfile(full_path):
        return send_from_directory(app.static_folder, path)

    html_path = f"{path}.html"
    if os.path.isfile(os.path.join(app.static_folder, html_path)):
        return send_from_directory(app.static_folder, html_path)

    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(debug=True)