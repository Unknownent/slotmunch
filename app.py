from dotenv import load_dotenv
load_dotenv()

from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
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

if __name__ == '__main__':
    app.run(debug=True)