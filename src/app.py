from flask import Flask, jsonify
from src.config import Environment
from src.presentation.routes import payment_modality_bp, financial_entry_bp, company_bp
from src.presentation.routes.auth_routes import auth_bp
from src.presentation.routes.admin_routes import admin_bp
from src.database import MongoConnection

env = Environment()

def create_app():
    app = Flask(__name__)

    app.config["JSON_SORT_KEYS"] = False

    # Rotas de autenticação
    app.register_blueprint(auth_bp, url_prefix="/api")

    # Rotas administrativas (Super Admin only)
    app.register_blueprint(admin_bp, url_prefix="/api")

    # Rotas protegidas
    app.register_blueprint(payment_modality_bp, url_prefix="/api")
    app.register_blueprint(financial_entry_bp, url_prefix="/api")
    app.register_blueprint(company_bp, url_prefix="/api")
    
    @app.route("/", methods=["GET"])
    def home():
        return jsonify({
            "message": "Bem-vindo ao Dashboard Financeiro API - Multi-Tenant",
            "version": "2.0.0",
            "features": ["Multi-Tenant", "JWT Auth", "RBAC"],
            "endpoints": {
                "health": "/health",
                "auth": {
                    "register": "POST /api/auth/register",
                    "login": "POST /api/auth/login",
                    "refresh": "POST /api/auth/refresh",
                    "me": "GET /api/auth/me (requires auth)"
                },
                "admin": {
                    "dashboard": "GET /api/admin/dashboard (super admin only)",
                    "companies": "GET /api/admin/companies (super admin only)",
                    "create_company": "POST /api/admin/companies (super admin only)",
                    "company_details": "GET /api/admin/companies/<id> (super admin only)",
                    "impersonate": "POST /api/admin/impersonate/<company_id> (super admin only - 1h token)",
                    "users": "GET /api/admin/users (super admin only)",
                    "create_user": "POST /api/admin/users (super admin only)",
                    "toggle_user": "PATCH /api/admin/users/<id>/toggle-active (super admin only)"
                },
                "payment_modalities": {
                    "list": "GET /api/payment-modalities (requires auth)",
                    "create": "POST /api/payment-modalities (requires auth)",
                    "update": "PUT /api/payment-modalities/<id> (requires auth)",
                    "delete": "DELETE /api/payment-modalities/<id> (requires auth)",
                    "toggle": "PATCH /api/payment-modalities/<id>/toggle (requires auth)"
                },
                "financial_entries": {
                    "list": "GET /api/financial-entries (requires auth)",
                    "create": "POST /api/financial-entries (requires auth)",
                    "update": "PUT /api/financial-entries/<id> (requires auth)",
                    "delete": "DELETE /api/financial-entries/<id> (requires auth)"
                }
            },
            "database_architecture": {
                "shared_db": ["companies", "users", "features"],
                "per_company_db": ["financial_entries", "payment_modalities", "roles"]
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
