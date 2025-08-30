from flask import Flask
from src.routes.home import home_bp
from src.routes.health import health_bp

app = Flask(__name__)

# Register routes
app.register_blueprint(home_bp)
app.register_blueprint(health_bp)

if __name__ == "__main__":
    app.run(debug=True)
