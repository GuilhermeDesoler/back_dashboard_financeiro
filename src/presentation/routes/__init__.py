from .payment_modality_routes import payment_modality_bp
from .financial_entry_routes import financial_entry_bp
from .company_routes import company_bp
from .platform_settings_routes import platform_settings_bp
from .installment_routes import installment_bp
from .account_routes import account_bp
from .bank_limit_routes import bank_limit_bp

__all__ = [
    "payment_modality_bp",
    "financial_entry_bp",
    "company_bp",
    "platform_settings_bp",
    "installment_bp",
    "account_bp",
    "bank_limit_bp"
]
