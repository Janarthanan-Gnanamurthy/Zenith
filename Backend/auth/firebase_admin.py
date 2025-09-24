import os
import firebase_admin
from firebase_admin import credentials, auth
from fastapi import HTTPException, status

current_dir = os.path.dirname(os.path.abspath(__file__))
cred_path = os.path.join(current_dir, "serviceAccountKey.json")

# Initialize Firebase Admin
try:
    if not firebase_admin._apps:  # Only initialize if not already initialized
        if os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
        else:
            # For development, you can use environment variables or default credentials
            # firebase_admin.initialize_app()  # Uses default credentials
            print(f"Warning: Firebase service account key not found at {cred_path}")
            print("Authentication will be disabled. Please add your serviceAccountKey.json file.")
except Exception as e:
    print(f"Warning: Failed to initialize Firebase Admin: {e}")
    print("Authentication will be disabled.")

def verify_firebase_token(id_token):
    """
    Verify the Firebase ID token and return the decoded token.
    """
    try:
        # Check if Firebase is initialized
        if not firebase_admin._apps:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Authentication service not available. Firebase not initialized."
            )
        
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token
    except auth.InvalidIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token."
        )
    except auth.ExpiredIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Expired authentication token."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Failed to authenticate: {str(e)}"
        )