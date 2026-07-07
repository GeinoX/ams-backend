# notifications/firebase.py
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

FIREBASE_AVAILABLE = False

try:
    import firebase_admin
    from firebase_admin import credentials

    cred_path = BASE_DIR / "credentials" / "firebase-service-account.json"

    if cred_path.exists() and not firebase_admin._apps:
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
        FIREBASE_AVAILABLE = True
    else:
        if not cred_path.exists():
            print("Firebase credentials file not found — push notifications disabled")

except Exception as e:
    print(f"Firebase initialization failed: {e}")