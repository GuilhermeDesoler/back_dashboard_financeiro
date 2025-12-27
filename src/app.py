from flask import Flask, jsonify
from src.config import Environment
from src.presentation.routes import payment_modality_bp, financial_entry_bp
from src.database import MongoConnection

env = Environment()

def create_app():
    app = Flask(__name__)
    
    app.config["JSON_SORT_KEYS"] = False
    
    app.register_blueprint(payment_modality_bp, url_prefix="/api")
    app.register_blueprint(financial_entry_bp, url_prefix="/api")
    
    @app.route("/", methods=["GET"])
    def home():
        return jsonify({
            "message": "Bem-vindo ao Dashboard Financeiro API",
            "version": "1.0.0",
            "endpoints": {
                "health": "/health",
                "payment_modalities": {
                    "list": "GET /api/payment-modalities",
                    "create": "POST /api/payment-modalities",
                    "update": "PUT /api/payment-modalities/<id>",
                    "delete": "DELETE /api/payment-modalities/<id>",
                    "toggle": "PATCH /api/payment-modalities/<id>/toggle"
                },
                "financial_entries": {
                    "list": "GET /api/financial-entries",
                    "create": "POST /api/financial-entries",
                    "update": "PUT /api/financial-entries/<id>",
                    "delete": "DELETE /api/financial-entries/<id>"
                }
            }
        }), 200
    
    @app.route("/health", methods=["GET"])
    def health_check():
        return {"status": "ok", "message": "API is running"}, 200
    
    @app.before_request
    def connect_db():
        MongoConnection()
    
    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
