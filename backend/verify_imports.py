"""
Quick import validation script.
Run: python verify_imports.py
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

errors = []

def check_import(module_path: str):
    try:
        __import__(module_path)
        print(f"  ✅ {module_path}")
    except Exception as e:
        print(f"  ❌ {module_path}: {e}")
        errors.append(module_path)

print("=" * 60)
print("FraudShield AI — Import Verification")
print("=" * 60)

print("\n📦 Database layer:")
check_import("backend.database.mongo")
check_import("backend.database.redis")

print("\n🔐 Middleware:")
check_import("backend.middleware.auth_middleware")

print("\n📋 Models:")
check_import("backend.models.user")
check_import("backend.models.fraud_case")
check_import("backend.models.report")
check_import("backend.models.subscription")
check_import("backend.models.community_report")

print("\n🤖 Services (existing):")
check_import("backend.prompts.fraud_prompt")
check_import("backend.prompts.hindi_prompt")
check_import("backend.services.risk_engine")
check_import("backend.services.gemini_service")

print("\n🔧 Services (new):")
check_import("backend.services.fraud_service")
check_import("backend.services.alert_service")
check_import("backend.services.cloudinary_service")
check_import("backend.services.razorpay_service")
check_import("backend.services.report_service")

print("\n🛣️  Routes:")
check_import("backend.routes.auth")
check_import("backend.routes.fraud")
check_import("backend.routes.history")
check_import("backend.routes.community")
check_import("backend.routes.reports")
check_import("backend.routes.payments")
check_import("backend.routes.alerts")

print("\n🚀 Main app:")
check_import("backend.main")

print("\n" + "=" * 60)
if errors:
    print(f"❌ {len(errors)} import(s) FAILED: {errors}")
else:
    print("✅ All imports passed successfully!")
print("=" * 60)
